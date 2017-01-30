package com.bah.heimdall.ingestjobs

import java.util.Date

import com.bah.heimdall.common.{AppConfig, JsonUtils, KafkaMessage, KafkaProducer}
import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.common.JsonUtils._
import com.bah.heimdall.common.HttpUtils._
import com.bah.heimdall.common.CodecUtils._
import com.bah.heimdall.ingestjobs.Project._
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.rdd.RDD
import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write

import scala.collection.immutable.List
import scala.collection.mutable.ArrayBuffer

/**
  * Pulls Github data (public, enterprise) using the Github rest api. It filters/enriches
  * data that is needed for Stage and creates domain model objects.
  */
object Github extends GithubBase{

  implicit val formats = DefaultFormats

  def main(args: Array[String]): Unit = {
    if(args.length < 2) {
      println("Usage: spark-submit with params <configFile> <outputPath>")
      System.exit(0)
    }

    val configFile = args(0)
    AppConfig(configFile)

    val batchId = new Date().getTime();
    println(s"Processing batchId: $batchId")
    val indexName = AppConfig.conf.getString(PROJECTS_INDEX_NAME)

    val outPath = args(1) + "/"+ batchId
    val completeTopic = AppConfig.conf.getString(INGEST_COMPLETION_TOPIC)

    val sparkConf = new SparkConf().setAppName("Ingest Project Data")
    sparkConf.set("spark.eventLog.enabled", "true")
    val sc = new SparkContext(sparkConf)
    //print configs
    //sc.getConf.toDebugString()

    val runEnv = AppConfig.conf.getString(RUN_ENV)
    println(s"Project run environment is set to $runEnv")
    if(runEnv == PUBLIC){
      val orgUrlsRdd = sc.parallelize(getPublicOrgsList())
      val orgsRdd = orgUrlsRdd.map(getOrgData(_))
      pullData(runEnv, orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ENTERPRISE){
      val orgTypeList = getEnterpriseOrgTypesList
      val orgsList = (getResponseWithPagedData(orgTypeList(0), true) ++ getResponseWithPagedData(orgTypeList(1), true))
      val orgsRdd = sc.parallelize(orgsList)
      pullData(runEnv, orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ALL){
      val orgUrlsRdd = sc.parallelize(getPublicOrgsList())
      val pubOrgsRdd = orgUrlsRdd.map(getOrgData(_))
      val pubOutRdd = pullData(PUBLIC, pubOrgsRdd)

      val orgTypeList = getEnterpriseOrgTypesList
      val orgsList = (getResponseWithPagedData(orgTypeList(0), true) ++ getResponseWithPagedData(orgTypeList(1), true))
      val entOrgsRdd = sc.parallelize(orgsList)
      val entOutRdd = pullData(ENTERPRISE, entOrgsRdd)
      pubOutRdd.union(entOutRdd).saveAsTextFile(outPath)
    }
    //Write completion message
    val producer = KafkaProducer(AppConfig.conf)
    val msg = new KafkaMessage(batchId.toString, s"$batchId:$indexName:$ES_ACTION_UPSERT")
    producer.sendMessageBlocking(completeTopic, msg , AppConfig.conf)
    producer.close()

    sc.stop
  }

  def pullData(env:String, orgsRdd: RDD[JValue]): RDD[String] = {
    val orgsOutput = orgsRdd.map(orgJson => {
      val reposUrl = (orgJson \ "repos_url").extract[String]
      val orgRepos = getOrgRepos(env, reposUrl)
      //Repo fields
      val orgReposOutput = orgRepos.children.map(repoJson => {
        buildOrgStructure(env, orgJson, repoJson)
      })
      write(orgReposOutput)
    })
    orgsOutput
  }

  def buildOrgStructure(env:String, orgJson: JValue, repoJson: JValue): OrgRepo = {
    val orgLogin = (orgJson \ "login").extract[String]
    val orgId = (orgJson \ "id").extract[String]
    val repoName = (repoJson \ "name").extract[String]
    val repoDesc = (repoJson \ "description").extract[String]
    //Get list properties
    val contributorsJson = getPagedRepoProperties(env, orgLogin, repoName, "contributors")
    val languagesJson = getRepoProperties(env, orgLogin, repoName, "languages")
    val watchers = getPagedRepoProperties(env, orgLogin, repoName, "subscribers")
    val forksJson = getPagedRepoProperties(env, orgLogin, repoName, "forks")
    //Get readme file associated to repo
    val readmeRaw = getRepoProperties(env, orgLogin, repoName, "contents/README.md")
    //build
    val (contributors, numCommits) = buildContributors(contributorsJson)
    val numWatchers = buildWatchers(watchers)
    val languages = buildLanguageMap(languagesJson)
    val forks = buildForks(forksJson)
    //Auto suggest
    val autoSuggest = buildAutoSuggest(repoName,repoDesc,"",languages,contributors)

    //Build repo structure
    val orgRepo = OrgRepo(orgId + ES_ID_SEPARATOR + (repoJson \ "id").extract[String],
      Org((repoJson \ "owner" \ "login").extract[String],
        (repoJson \ "owner" \ "html_url").extract[String],
        (repoJson \ "owner" \ "avatar_url").extract[String],
        (repoJson \ "owner" \ "type").extract[String]),
      env,
      repoName,
      (repoJson \ "html_url").extract[String],
      (repoJson \ "full_name").extract[String],
      (repoJson \ "name").extract[String],
      repoDesc,
      (repoJson \ "language").extract[String],
      (repoJson \ "stargazers_count").extract[Int],
      forks,
      0,//num of releases
      (repoJson \ "updated_at").extract[String],
      (repoJson \ "created_at").extract[String],
      contributors,
      languages,
      buildReadme(readmeRaw),
      numWatchers,
      contributors.length,
      numCommits,
      calculateRanks(repoJson, numWatchers, contributors.length, numCommits),
      autoSuggest)

    orgRepo
  }

  def buildContributors(contributorsJson: ArrayBuffer[JValue]): (List[Contributor], Int) = {
    var numCommits = 0

    def getContributors(jsonContributors:ArrayBuffer[JValue]): List[Contributor] = {
      val contributors = jsonContributors.map(contributorJson => {
        val cType = (contributorJson \ "type").extract[String]
        numCommits += (contributorJson \ "contributions").extract[Int]
        if (cType == "User")
          Contributor((contributorJson \ "login").extract[String],
            (contributorJson \ "html_url").extract[String],
            (contributorJson \ "avatar_url").extract[String],
            (contributorJson \ "type").extract[String])
        else Contributor((contributorJson \ "name").extract[String],
          "", "",
          (contributorJson \ "type").extract[String])
      })
      contributors.toList
    }

    if(contributorsJson.nonEmpty && !JsonUtils.hasField(STAGE_ERROR, contributorsJson(0)))
      (getContributors(contributorsJson), numCommits)
    else
      (List(),0)
  }

  def buildForks(forksJson: ArrayBuffer[JValue]): Forks = {
    val forkRepos = forksJson.map(forkJson => {
      val id = (forkJson \ "owner" \ "id").extract[String] + ES_ID_SEPARATOR + (forkJson \ "id").extract[String]
      val forkRepo = ForkRepo(id,
        (forkJson \ "name").extract[String],
        (forkJson \ "owner" \ "login").extract[String])
      forkRepo
    })
    Forks(forkRepos.toList)
  }

  def buildReadme(readmeRaw: String): ReadMe = {
    val jsonReadme = parse(readmeRaw)
    val fld = jsonReadme findField {
      case JField(STAGE_ERROR, _) => true
      case _ => false
    }
    if(fld.isEmpty){
      val content = (jsonReadme \ "content").extract[String]
      ReadMe(decodeBase64(content), (jsonReadme \ "download_url").extract[String])
    }else {
      ReadMe("", "")
    }
  }

  def buildWatchers(watchersJson:ArrayBuffer[JValue]): Integer = {
    if(watchersJson.nonEmpty && !JsonUtils.hasField(STAGE_ERROR, watchersJson(0))){
      watchersJson.size
    }else {
      0
    }
  }

  def buildLanguageMap(languages:String): Map[String, String] = {
    parse(languages).mapField( k =>{
      (k._1, k._2)
    }).extract[Map[String, String]]
  }

  def calculateRanks(repoJson: JValue, numWatchers:Int, numContributors:Int, numCommits:Int): Int ={
    val stars = (repoJson \ "stargazers_count").extract[Int]
    (stars*3) + (numWatchers*4) + (numContributors*5) + numCommits
  }

  def buildAutoSuggest(repoName:String,
                       repoDesc:String,
                       orgName:String,
                       languages:Map[String,String],
                       contributors:List[Contributor]): List[SuggestField] ={
    val contribNames = contributors.map(contrib => {
      contrib.username
    })
    val repoNameClean = replacePunctuation(repoName)
    val repoDescCleanList = replacePunctuation(repoDesc).split(" ").toList

    var autoSuggestFields = ArrayBuffer.empty[SuggestField]
    autoSuggestFields += SuggestField(List(repoNameClean),repoNameClean + "# name")
    autoSuggestFields += SuggestField(List(repoName), repoNameClean + "# name")
    autoSuggestFields += SuggestField(repoDescCleanList, repoNameClean + "# desc")
    autoSuggestFields += SuggestField(languages.keySet.toList, repoNameClean + "# languages")
    autoSuggestFields += SuggestField(contribNames, repoNameClean + "# project contributors")
    autoSuggestFields.toList
  }

  def replacePunctuation(value:String):String = {
    if (value == null)
      ""
    else
      value.replaceAll("[^-_a-zA-Z0-9\\s]", "")
  }
}