package com.bah.heimdall.process

import com.bah.heimdall.common.{AppConfig, KafkaConsumer}
import com.bah.heimdall.common.AppConstants._
import org.apache.spark.sql.SparkSession
import org.json4s.DefaultFormats
import org.json4s.jackson.JsonMethods._

object ElasticDataOutput {

  implicit val formats = DefaultFormats

  def addIndexMetaData(jsonLine: String, indexName:String, docType: String): String ={
    val id = (parse(jsonLine) \ "id").extract[String]
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

    val consumer = KafkaConsumer(conf)
    println(s"Fetching messages from topic $completeTopic")
    val messages = consumer.getMessages(completeTopic, conf).getOrElse(List())
    println("Message count " + messages.length)
    messages.foreach(message => {
      val batchId = message.value
      println(s"Processing batchId:$batchId from topic $completeTopic")
      val jsonDF = spark.read.json(s"$inputPath/$batchId/part*")
      jsonDF.printSchema()
      jsonDF.show()
      val outDS = jsonDF.toJSON.map(json => addIndexMetaData(json, indexName, docType))
      outDS.rdd.saveAsTextFile(s"$outputPath/$batchId")
    })
  }
}