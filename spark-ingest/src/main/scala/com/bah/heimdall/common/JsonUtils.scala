package com.bah.heimdall.common

import org.json4s._
import org.json4s.jackson.JsonMethods._
import com.bah.heimdall.common.HttpUtils._

object JsonUtils {
  def getJsonResponse(url:String, continueOnErr:Boolean = true):JValue={
    parse(getResponse(url, continueOnErr))
  }

  def getJson(jsonStr:String):JValue = {
    parse(jsonStr)
  }

  def hasField(fieldName:String, jValue: JValue): Boolean = {
     (jValue \ fieldName) != JNothing
  }
}
