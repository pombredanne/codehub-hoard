package com.bah.heimdall.common

import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.BaseSpec
import org.json4s.JsonAST.JField
import org.json4s.jackson.JsonMethods._
import org.scalatest.mock.MockitoSugar
import org.mockito.Mockito._

class HttpUtilsSpec extends BaseSpec{
  "Invalid url" should "throw runtime error" in {
    val url = "https://1234.com/index"
    intercept[RuntimeException]{
      HttpUtils.getResponse(url, false)
    }
  }

  "valid url" should "not contain stage error in response" in {
    val url = "https://api.github.com"
    val js = parse(HttpUtils.getResponse(url))
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

  "Response body" should "be returned" in {
    HttpUtils.getResponseWithPagedData("https://", false)
  }

  "test body" should "be returned" in {
    val json = HttpUtils.getResponseWithPagedData("https://", true)
    println(json)
    println("Count" + json.length)

  }

  "Response body and paging header" should "be returned" in {
    //val mockUtil = mock[IngestUtil]

    val result = HttpUtils.getResponseWithPagedData("https://", true)
    println(result)
  }
}
