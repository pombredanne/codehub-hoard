package com.bah.heimdall.common

import java.util

import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.BaseSpec
import org.json4s.JsonAST.JField
import org.json4s.jackson.JsonMethods._

class HttpUtilsSpec extends BaseSpec{

  "Invalid url" should "throw runtime error" in {
    val url = "https://1234.com/index"
    intercept[RuntimeException]{
      HttpUtils.getResponse(url, false)
    }
  }

  "valid url" should "not contain stage error in response" in {
    val url = "https://github.boozallencsn.com/api/v3/organization?access_token=4faddc49265b75feffa1ab129c957d0dd5c8461f"
    val js = parse(HttpUtils.getResponseFromUrl(url, false))
    val fld = js findField {
      case JField(STAGE_ERROR, _) => true
      case _ => false
    }
    assert(fld == None)
  }

  "Invalid url" should "contain stage error in response" in {
    val url = "https://1234.com/index"
    val js = parse(HttpUtils.getResponse(url))
    val fld = js findField {
      case JField(STAGE_ERROR, _) => true
      case _ => false
    }
    assert(fld != None)
  }

  //"response body" should "be returned" in {
  ignore should "be returned" in {
    val responseToReturn: util.ArrayList[String] = new util.ArrayList[String]
    val expectedJson = """{
                         |  "login": "Project-Heimdall",
                         |  "id": 18699526,
                         |  "description": "Seer of Code Worlds",
                         |  "company": "abc",
                         |  "html_url": "https://github.com/Project-Heimdall",
                         |  "created_at": "2016-04-27T11:33:40Z",
                         |  "type": "Organization"
                         |}""".stripMargin
    responseToReturn.add(expectedJson)
    val json = HttpUtils.getResponseWithPagedData("https://someurl.com", true)
    println(json)
    println("Count" + json.length)
    assert(expectedJson == json)
  }

  //"Response body and paging header" should "be returned" in {
  ignore should "be returned in a List" in {
    val result = HttpUtils.getResponseWithPagedData("https://", true)
    println(result)
  }
}
