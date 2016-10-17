package com.bah.heimdall.ingestjobs

import com.bah.heimdall.common.{AppConfig, JsonUtils}
import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.common.JsonUtils._
import com.bah.heimdall.common.HttpUtils._
import com.bah.heimdall.common.CodecUtils._
import com.bah.heimdall.ingestjobs.Project._
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.rdd.RDD
import org.json4s._
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write

import scala.collection.immutable.List
import scala.collection.mutable.ArrayBuffer

object Github {

  implicit val formats = DefaultFormats

  def main(args: Array[String]): Unit = {
    if(args.length < 2) {
      println("Usage: spark-submit with params <configFile> <outputPath>")
      System.exit(0)
    }

    val configFile = args(0)
    val outPath = args(1)

    AppConfig(configFile)
    //local mode
    val sc = new SparkContext(new SparkConf().setAppName("Process Project Data").setMaster("local[1]"))

    val runEnv = AppConfig.conf.getString(RUN_ENV)
    println(s"Project run environment is set to $runEnv")
    if(runEnv == PUBLIC){
      AppConfig.envType = PUBLIC
      val orgUrlsRdd = sc.parallelize(getPublicOrgsList)
      val orgsRdd = orgUrlsRdd.map(getOrgData(_))
      pullData(orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ENTERPRISE){
      AppConfig.envType = ENTERPRISE
      val orgTypeList = getEnterpriseOrgTypesList
      val orgsList = (getResponseWithPagedData(orgTypeList(0), true) ++ getResponseWithPagedData(orgTypeList(1), true))
      val orgsRdd = sc.parallelize(orgsList)
      pullData(orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ALL){
      //AppConfig.envType = PUBLIC
      //val orgUrlsRdd = sc.parallelize(getPublicOrgsList)
      println("** ALL Orgs List **")
      //orgUrlsRdd.foreach(println(_))
    }
  }

  def isPublic(env:String) = (env == "PUBLIC")

  def getSourceUrl() = {
   if(isPublic(AppConfig.envType)) AppConfig.conf.getString(PUB_GITHUB_API_URL) else AppConfig.conf.getString(ENT_GITHUB_API_URL)
  }

  def getAccessToken() = {
    val accessToken = if(isPublic(AppConfig.envType)) AppConfig.conf.getString(PUB_ACCESS_TOKEN) else AppConfig.conf.getString(ENT_ACCESS_TOKEN)
    s"access_token=$accessToken"
  }

  def getPublicOrgsList(): Array[String] = {
    AppConfig.conf.getString(ORGS).split(",").map(getSourceUrl() + "users/" + _ +"?"+ getAccessToken())
  }

  def getEnterpriseOrgTypesList(): Array[String] = {
    "organizations,users".split(",").map(getSourceUrl() + _ +"?since=0&per_page=100&"+ getAccessToken())
  }

  def pullData(orgsRdd: RDD[JValue]): RDD[String] = {
    val orgsOutput = orgsRdd.map(orgJson => {
      val reposUrl = (orgJson \ "repos_url").extract[String]
      val orgRepos = getOrgRepos(reposUrl)
      //Repo fields
      val orgReposOutput = orgRepos.children.map(repoJson => {
        buildOrgStructure(orgJson, repoJson)
      })
      write(orgReposOutput)
    })
    orgsOutput
  }

  def getOrgData(url: String): JValue = {
    getJsonResponse(url, false)
  }

  def getOrgRepos(orgRepoUrl: String): JValue = {
    getJsonResponse(s"$orgRepoUrl?" + getAccessToken(), false)
  }

  def getPagedRepoProperties(org: String, repoName: String, propertyName: String): ArrayBuffer[JValue] = {
      val respPerPage = if (AppConfig.conf.getInt(RESPONSE_PER_PAGE) > 0) AppConfig.conf.getInt(RESPONSE_PER_PAGE) else 100
      getResponseWithPagedData(getSourceUrl() + s"repos/$org/$repoName/$propertyName?since=0&per_page=$respPerPage&" + getAccessToken(), true)
  }

  def getRepoProperties(org: String, repoName: String, propertyName: String): String = {
    getResponse(getSourceUrl() + s"repos/$org/$repoName/$propertyName?" + getAccessToken(), true)
  }

  def calculateRanks(repoJson: JValue, numWatchers:Int, numContributors:Int, numCommits:Int): Int ={
    val stars = (repoJson \ "stargazers_count").extract[Int]
    (stars*3) + (numWatchers*4) + (numContributors*5) + numCommits
  }

  def buildOrgStructure(orgJson: JValue, repoJson: JValue): OrgRepo = {
    val orgLogin = (orgJson \ "login").extract[String]
    val orgId = (orgJson \ "id").extract[String]
    val repoName = (repoJson \ "name").extract[String]
    //Get list properties
    val contributorsJson = getPagedRepoProperties(orgLogin, repoName, "contributors")
    val (contributors, numCommits) = buildContributors(contributorsJson)
    val languages = getRepoProperties(orgLogin, repoName, "languages")
    val watchers = getPagedRepoProperties(orgLogin, repoName, "subscribers")
    val numWatchers = buildWatchers(watchers)
    //Get file associated to repo
    val readmeRaw = getRepoProperties(orgLogin, repoName, "contents/README.md")
    //Auto suggest
    val autoSuggest = buildAutoSuggest(repoName,"","",languages,contributors)

      //Build repo structure
    val orgRepo = OrgRepo(orgId + ES_ID_SEPARATOR + (repoJson \ "id").extract[String],
      Org((repoJson \ "owner" \ "login").extract[String],
          (repoJson \ "owner" \ "html_url").extract[String],
          (repoJson \ "owner" \ "avatar_url").extract[String],
          (repoJson \ "owner" \ "type").extract[String]),
      "public", //TODO: pull from config?
      (repoJson \ "name").extract[String],
      (repoJson \ "html_url").extract[String],
      (repoJson \ "full_name").extract[String],
      (repoJson \ "name").extract[String],
      (repoJson \ "description").extract[String],
      (repoJson \ "language").extract[String],
      (repoJson \ "stargazers_count").extract[String],
      (repoJson \ "forks").extract[String],
      0,//num of releases
      (repoJson \ "updated_at").extract[String],
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
        else Contributor((contributorJson \ "login").extract[String],
            (contributorJson \ "html_url").extract[String],
            (contributorJson \ "avatar_url").extract[String],
            (contributorJson \ "type").extract[String])
      })
      contributors.toList
    }

    if(contributorsJson.nonEmpty && !JsonUtils.hasField(STAGE_ERROR, contributorsJson(0)))
      (getContributors(contributorsJson), numCommits)
    else
      (List(),0)
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

  def buildAutoSuggest(repoName:String,
                       repoDesc:String,
                       orgName:String,
                       languages:String,
                       contributors:List[Contributor]): String ={
    val langKeys: Map[String, String] = parse(languages).mapField( k =>{
      (k._1, k._2)
    }).extract[Map[String, String]]
    val keysSuggest = write(langKeys.keySet)
    val contribNames = contributors.map(contrib => {
      contrib.username
    })
    val suggestContributors : JArray = contribNames.toSeq
    val repoNameClean = replacePunctuation(repoName)
    val repoDescClean = replacePunctuation(repoDesc)

    var autoSuggestFields = ArrayBuffer.empty[SuggestField]
    autoSuggestFields += SuggestField(s"[$repoNameClean,$repoDescClean]",repoNameClean )
    autoSuggestFields += SuggestField(repoName, repoNameClean)
    autoSuggestFields += SuggestField(keysSuggest, repoNameClean)
    autoSuggestFields += SuggestField(write(suggestContributors), repoNameClean)
    write(Suggest(autoSuggestFields.toList))
  }

  def replacePunctuation(value:String):String = {
    value.replaceAll("[^-_a-zA-Z0-9\\s]", "")
  }
}