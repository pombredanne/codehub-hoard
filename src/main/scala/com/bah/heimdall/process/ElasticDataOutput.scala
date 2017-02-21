package com.bah.heimdall.process

import java.util.Date

import com.bah.heimdall.common.{AppConfig, ElasticClientManager, KafkaConsumer}
import com.bah.heimdall.common.AppConstants._
import org.apache.spark.sql.{Dataset, SparkSession}
import org.json4s.DefaultFormats
import org.json4s.jackson.JsonMethods._

import scala.util.{Failure, Success, Try}

/**
  * Takes in new, update and upsert records from a json dump and adds metadata required by ES to perform bulk
  * insert or update.
  */
object ElasticDataOutput {
  implicit val formats = DefaultFormats

  def addIndexMetaData(jsonLine: String, action:String, indexName:String, docType: String): String ={
    val id = (parse(jsonLine) \ "stage_id").extract[String]
    //Prepare data to index as doc, add any attribute to doc
    val jsonStr = action match {
      case ES_ACTION_UPSERT => s"""{"doc":$jsonLine, "doc_as_upsert": true}"""
      case _ => jsonLine
    }
    //Prepare metadata for bulk Ingest
    val es_action = if (action.equalsIgnoreCase(ES_ACTION_UPSERT)) ES_ACTION_UPDATE else action
    val outJson = s"""{$es_action:{"_index": \"$indexName\","_type":\"$docType\", "_id":\"$id\"}}\n""" + jsonStr
    outJson
  }


  def main(args: Array[String]): Unit = {
    if(args.length <4) {
      println("Usage: spark-submit with params <configFile> <inputPath> <outputPath> <updateInputPath")
      System.exit(0)
    }

    val configFile = args(0)
    val inputPath = args(1)
    val outputPath = args(2)
    val updateInputPath = args(3)
    AppConfig(configFile)
    val conf = AppConfig.conf
    val completeTopic = conf.getString(INGEST_COMPLETION_TOPIC)
    val docType = "project"

    val spark = SparkSession
      .builder()
      .appName("Process data output")
      //.config("spark.some.config.option", "some-value")
      //.master("local[1]")
      .getOrCreate()
    import spark.implicits._

    //Preparing data to be indexed
    println(s"Fetching messages from topic $completeTopic")
    val consumer = KafkaConsumer(conf)
    val messages = consumer.getMessages(completeTopic, conf).getOrElse(List())
    consumer.close
    println("Message count " + messages.length)
    messages.foreach(message => {
      val batchId = message.key
      val indexName = message.value.split(":")(1)
      val actionType = message.value.split(":")(2)
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
      //resultDF.printSchema()
      //resultDF.show()
      val outDS = resultDF.toJSON.map(json => addIndexMetaData(json, actionType , indexName, docType))
      if (outDS.count > 0 )
        outDS.rdd.saveAsTextFile(s"$outputPath/$batchId")

    })

  }

}