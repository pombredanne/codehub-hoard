package com.bah.heimdall.common

import com.bah.heimdall.{BaseSpec, TestAppConfig}
import org.scalatest.Matchers

class ElasticClientManagerSpec extends BaseSpec with Matchers{

  "test" should "return all documents in ES Index" in {
    val conf = TestAppConfig.getConf
    val elasticClientManager = ElasticClientManager(conf)
    val esResponse = elasticClientManager.getAllDocumentIds("projects")

    val docIds = esResponse.getHits.getHits.map( doc => {
      doc.getId
    })
    //println(esResponse)
    docIds.foreach(println(_))
  }
}
