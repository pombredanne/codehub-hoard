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
    val url = "https://api.github.com/repos/Project-Heimdall/heimdall-devops/contents/README.md?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2"
    //val url = "https://github.boozallencsn.com/api/v3/organizations?access_token=785cfc22173deb5d3ebe0903e5d96b4238f57347"
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
    //HttpUtils.getResponseWithPagedData("https://github.boozallencsn.com/api/v3/repos/BAH-Internal/Tolga-Demo-Project/contributors?since=0&per_page=100&access_token=785cfc22173deb5d3ebe0903e5d96b4238f57347", false)
    HttpUtils.getResponseWithPagedData("https://github.boozallencsn.com/api/v3/repos/BAH-Internal/Tolga-Demo-Project/contents/README.md?access_token=785cfc22173deb5d3ebe0903e5d96b4238f57347", false)
  }

  "test body" should "be returned" in {
    //val json = HttpUtils.getResponseWithPagedData("https://api.github.com/repos/elastic/beat123s-packer/subscribers?since=0&per_page=5&access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2", true)
    val json = HttpUtils.getResponseWithPagedData("https://github.boozallencsn.com/api/v3/organizations?since=0&per_page=100&access_token=785cfc22173deb5d3ebe0903e5d96b4238f57347", true)
    println(json)
    println("Count" + json.length)

  }




  "Response body and paging header" should "be returned" in {
    //val mockUtil = mock[IngestUtil]

    val result = HttpUtils.getResponseWithPagedData("https://api.github.com/repos/elastic/elasticsearch.github.com/contributors?since=0&per_page=100&anon=true&access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2", true)
    println(result)
  }
}
