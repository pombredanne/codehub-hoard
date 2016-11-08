package com.bah.heimdall.process

import com.bah.heimdall.common.{AppConfig, KafkaConsumer}
import com.bah.heimdall.common.AppConstants._
import org.apache.spark.sql
import org.apache.spark.sql.SparkSession
import org.json4s.DefaultFormats
import org.json4s.jackson.JsonMethods._

import scala.util.{Failure, Success, Try}

object ElasticDataOutput {

  implicit val formats = DefaultFormats

  def addIndexMetaData(jsonLine: String, indexName:String, docType: String): String ={
    val id = (parse(jsonLine) \ "stage_id").extract[String]
    val outJson = s"""{"index":{"_index": \"$indexName\","_type":\"$docType\", "_id":\"$id\"}}\n""" + jsonLine
    outJson
  }

  def main(args: Array[String]): Unit = {
    if(args.length <3) {
      println("Usage: spark-submit with params <configFile> <inputPath> <outputPath>")
      System.exit(0)
    }

    val configFile = args(0)
    val inputPath = args(1)
    val outputPath = args(2)
    AppConfig(configFile)
    val conf = AppConfig.conf
    val completeTopic = conf.getString(INGEST_COMPLETION_TOPIC)
    val indexName = conf.getString(PROJECTS_INDEX_NAME)
    val docType = "project"

    val spark = SparkSession
      .builder()
      .appName("Process data output")
      //.config("spark.some.config.option", "some-value")
      .master("local[1]")
      .getOrCreate()
    import spark.implicits._

    println(s"Fetching messages from topic $completeTopic")
    val consumer = KafkaConsumer(conf)
    val messages = consumer.getMessages(completeTopic, conf).getOrElse(List())
    consumer.close

    println("Message count " + messages.length)
    messages.foreach(message => {
      val batchId = message.key
      val indexName = message.value.split(":")(1)
      println(s"Processing Index Data:$indexName for batchId:$batchId from topic $completeTopic")
      val jsonDF = Try(spark.read.json(s"$inputPath/*/$batchId/part*")) match {
        case Success(jsonDF) => Some(jsonDF)
        case Failure(ex) => {
          println(s"$STAGE_ERROR: Error occurred while processing Index:$indexName for batchId:$batchId from topic:$completeTopic")
          ex.printStackTrace()
          None
        }
      }
      val resultDF = jsonDF.getOrElse(Seq.empty[String].toDF())
      resultDF.printSchema()
      resultDF.show()
      val outDS = resultDF.toJSON.map(json => addIndexMetaData(json, indexName, docType))
      outDS.rdd.saveAsTextFile(s"$outputPath/$batchId")

    })
  }
}