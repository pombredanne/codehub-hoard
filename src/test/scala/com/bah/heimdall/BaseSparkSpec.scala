package com.bah.heimdall

import org.apache.spark.sql.SparkSession
import org.apache.spark.{SparkConf, SparkContext}
import org.scalatest.{BeforeAndAfter, FlatSpec}

class BaseSparkSpec extends FlatSpec with BeforeAndAfter{
  private val master = "local[1]"
  private val appName = "test-spark-ingest"

  var sc: SparkContext = _
  var spark: SparkSession = _

  before {
    val conf = new SparkConf()
      .setMaster(master)
      .setAppName(appName)
      .set("spark.sql.warehouse.dir", System.getProperty("java.io.tmpdir"))

    sc = new SparkContext(conf)

    spark = SparkSession
      .builder()
      .appName("Process Github Data")
      .master("local[1]")
      //.config("spark.some.config.option", "some-value")
      .getOrCreate()
  }

  after {
    if (sc != null) sc.stop()
    if (spark != null) spark.stop()
  }
}
