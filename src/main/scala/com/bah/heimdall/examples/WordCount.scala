package com.bah.heimdall.examples

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD


object WordCount {

  def getWC (linesRdd : RDD[String]): RDD[(String, Int)] = {
    val tokenized = linesRdd.flatMap(_.split(" "))
    val wordCounts = tokenized.map((_ , 1)).reduceByKey(_ + _)
    wordCounts.foreach(println)
    println(s"Total no of unique words: $wordCounts.count")
    return wordCounts
  }

  def main(args: Array[String]){
    //local mode
    val sc = new SparkContext(new SparkConf().setAppName("Process Project Data").setMaster("local"))
    val inPath = args(0)
    val outPath = args(1)

    val linesRdd = sc.textFile(inPath)
    getWC(linesRdd).saveAsTextFile(outPath)
  }
}