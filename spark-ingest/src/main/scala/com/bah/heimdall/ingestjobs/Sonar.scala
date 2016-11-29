package com.bah.heimdall.ingestjobs

import java.util.Date

import com.bah.heimdall.common.{AppConfig, KafkaMessage, KafkaProducer}
import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.common.HttpUtils._
import com.bah.heimdall.ingestjobs.Code.Metric
import com.bah.heimdall.ingestjobs.Project.Org
import org.apache.spark.rdd.RDD
import org.apache.spark.{SparkConf, SparkContext}
import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write

object Sonar extends GithubBase{

  implicit val formats = DefaultFormats

  def main(args: Array[String]):Unit = {
    if (args.length < 2) {
      println("Usage: spark-submit with params <configFile> <outputPath>")
      System.exit(0)
    }

    val configFile = args(0)
    AppConfig(configFile)

    val batchId = new Date().getTime();
    println(s"Processing batchId: $batchId")

    val outPath = args(1) + "/" + batchId
    val completeTopic = AppConfig.conf.getString(INGEST_COMPLETION_TOPIC)
    val indexName = AppConfig.conf.getString(CODES_INDEX_NAME)

    val sc = new SparkContext(new SparkConf().setAppName("Ingest Code Data"))

    val runEnv = AppConfig.conf.getString(RUN_ENV)
    println(s"Project run environment is set to $runEnv")

    if (runEnv == PUBLIC) {
      val orgUrlsRdd = sc.parallelize(getPublicOrgsList)
      val orgsRdd = orgUrlsRdd.map(getOrgData(_))
      pullData(runEnv, orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ENTERPRISE){
      val orgTypeList = getEnterpriseOrgTypesList
      val orgsList = (getResponseWithPagedData(orgTypeList(0), true) ++ getResponseWithPagedData(orgTypeList(1), true))
      val orgsRdd = sc.parallelize(orgsList)
      pullData(runEnv, orgsRdd).saveAsTextFile(outPath)
    }else if(runEnv == ALL){
        val orgUrlsRdd = sc.parallelize(getPublicOrgsList)
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
    val msg = new KafkaMessage(batchId.toString, s"$batchId:$indexName")
    producer.sendMessageBlocking(completeTopic, msg , AppConfig.conf)
    producer.close()
  }

  def pullData(env:String, orgsRdd: RDD[JValue]): RDD[String] = {
      val orgsOutput = orgsRdd.map(orgJson => {
      val reposUrl = (orgJson \ "repos_url").extract[String]
      val orgRepos = getOrgRepos(env, reposUrl)
      //Repo fields
      val orgMetricsOutput = orgRepos.children.map(repoJson => {
        buildOrgMetricsStructure(env, orgJson, repoJson)
      })
      write(orgMetricsOutput)
    })
    orgsOutput
  }

  def getOrgMetricsJson(metricTypes: String, projectName:String): JValue = {
    val url = AppConfig.conf.getString(SONAR_API_REMOTE_BASE_URL)+s"?resource=$projectName&metrics=$metricTypes&format=json"
    parse(getResponse(url, true))
  }

  def buildOrgMetricsStructure(env:String, orgJson: JValue, repoJson: JValue): Metric = {
    val metricsToCollect = AppConfig.conf.getString(SONAR_PROJECT_HEALTH_METRICS)
    val orgLogin = (orgJson \ "login").extract[String]
    val orgId = (orgJson \ "id").extract[String]
    val repoName = (repoJson \ "name").extract[String]

    //val orgMetricsJson = getOrgMetricsJson(metricsToCollect, "org.eclipse.ease:ease")
    val orgMetricsJson = getOrgMetricsJson(metricsToCollect, repoName)
    val metricsMap = getMetrics(orgMetricsJson)
    var metricFinal  = Map.empty[String, Map[String, String]]
    metricsMap.foreach(entry => {
      metricFinal += (entry.get("key").getOrElse("") -> entry)
    })
    val metrics = Metric(SRC_SONAR,
                      orgId + ES_ID_SEPARATOR + (repoJson \ "id").extract[String],
                      Org((repoJson \ "owner" \ "login").extract[String],
                        (repoJson \ "owner" \ "html_url").extract[String],
                        (repoJson \ "owner" \ "avatar_url").extract[String],
                        (repoJson \ "owner" \ "type").extract[String]),
                      repoName,
                      env,
                      (repoJson \ "language").extract[String],
                      (repoJson \ "updated_at").extract[String],
                      metricFinal
    )
    metrics
  }


  def getMetrics(metrics:JValue): List[Map[String,String]] = {
    val metricsMap = (metrics \ "msr").extract[List[Map[String,String]]]
    metricsMap
  }
}
