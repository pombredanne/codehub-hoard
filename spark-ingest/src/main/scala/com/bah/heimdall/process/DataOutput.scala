package com.bah.heimdall.process

import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD

object DataOutput {

  def main(args: Array[String]): Unit = {
    val inputPath = args(0)
    val outputPath = args(1)

    val sc = new SparkContext(new SparkConf().setAppName("Process data output").setMaster("local"))

    val lineRdd = sc.textFile(inputPath+"/part*")
    val outputRdd = reformatJsonForElastic(lineRdd)

    outputRdd.saveAsTextFile(outputPath)
  }

  def stripBrackets(jsonline: String): String = {
    jsonline.stripPrefix("[").stripSuffix("]")
  }

  def addIndexMetaData(jsonline: String, indexName:String = "", doctype: String = "", id:String = ""): String ={
    "{\"index\":{ \"_type\": \"project\" }}\n" + jsonline
  }

  def reformatJsonForElastic(lineRdd:RDD[String]): RDD[String] ={
    val outRdd = lineRdd.map(line => addIndexMetaData(stripBrackets(line)))
    outRdd
  }
}
