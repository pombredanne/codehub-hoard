package com.bah.heimdall.common

import com.bah.heimdall.common.AppConstants._

import scala.io.Source
import scala.util.{Failure, Success, Try}
import com.bah.heimdall.util.IngestUtil
import org.json4s.JValue

import collection.JavaConverters._
import scala.collection.mutable.ArrayBuffer

object HttpUtils {
  def getResponseFromUrl(url: String, continueOnErr: Boolean = true): String = {
    def tryUrl(url: String): Try[String] = Try(Source.fromURL(url).mkString)

    val jsonRaw = tryUrl(url) match {
      case Success(jsonRaw) => jsonRaw
      case Failure(ex) => {
        println(s"$STAGE_ERROR:Failed connecting to $url\n$ex")
        if (!continueOnErr)
          throw new RuntimeException(ex)
        else
          s"""{"$STAGE_ERROR":"$ex"}"""
      }
    }
    jsonRaw
  }

  def getResponse(url: String, continueOnErr: Boolean = true): String = {
    //println(s"Fetching data from url: $url")
    val str = IngestUtil.getHttpResponseWithHeaders(url, continueOnErr).asScala.toList(0)
    str
  }

  /**
    * Recursively extracts paged data from github api and returns the full dataset.
    * @param url
    * @param continueOnErr
    * @return
    */
  def getResponseWithPagedData(url:String, continueOnErr:Boolean): ArrayBuffer[JValue] = {
    //println(s"Fetching data from paged url:$url")
    var result = ArrayBuffer.empty[JValue]

    def getPagedData(url:String, continueOnErr:Boolean): ArrayBuffer[JValue] ={
      val responseList = IngestUtil.getHttpResponseWithHeaders(url, continueOnErr).asScala.toList
      if(responseList.length>0 && responseList(0).contains(STAGE_ERROR)) {
        result += (JsonUtils.getJson(responseList(0)))
      }else if (responseList.length == 0)
        result
      else if(responseList.length == 1){
        result ++= JsonUtils.getJson(responseList(0)).children
      }else{
        result ++= JsonUtils.getJson(responseList(0)).children
        getPagedData(parseNextUrl(responseList(1)), continueOnErr)
      }
    }

    getPagedData(url, continueOnErr)
  }

  def parseNextUrl(linkValue:String): String ={
    if(linkValue.contains("\"next\"")) {
      linkValue.split(",")(0).split(";")(0).stripPrefix("<").stripSuffix(">")
    }else{
      ""
    }
  }
}