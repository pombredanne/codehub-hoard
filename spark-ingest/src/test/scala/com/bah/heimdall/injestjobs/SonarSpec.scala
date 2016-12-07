package com.bah.heimdall.injestjobs

import com.bah.heimdall.BaseSparkSpec
import com.bah.heimdall.common.AppConfig
import com.bah.heimdall.ingestjobs.Sonar
import org.json4s.DefaultFormats
import org.json4s._
import org.json4s.jackson.JsonMethods._


class SonarSpec extends BaseSparkSpec{
    implicit val formats = DefaultFormats

    "Sonar Org Structure" should "be returned" in {
      val appConf = AppConfig("src/test/resources/application.conf")
      val orgUrls = sc.parallelize(Sonar.getPublicOrgsList())
      orgUrls.foreach(println(_))
      val orgsRdd = orgUrls.map(Sonar.getOrgData(_))
      orgsRdd.foreach(println(_))

    }

    "Metric Map " should "be returned" in {
      val metricsType = List("bugs","vulnerabilities")
      val jsonResponse =
        """
          |[{"id":4809,"uuid":"AVgHDUJU0ThXESs5KBt3","key":"heimdall-hoard","name":"heimdall-hoard of Project-Heimdall","scope":"PRJ","qualifier":"TRK","creationDate":"2016-10-27T16:50:59+0000","date":"2016-10-27T19:39:27+0000","lname":"heimdall-hoard of Project-Heimdall","version":"1.0","msr":[{"key":"bugs","val":1.0,"frmt_val":"1"},{"key":"vulnerabilities","val":0.0,"frmt_val":"0"}]}]
        """.stripMargin
      val orgMetrics = parse(jsonResponse)
      val metricMap = Sonar.getMetrics(orgMetrics)

      val key1 = metricMap(0).get("key").getOrElse("")
      val key2 = metricMap(1).get("key").getOrElse("")
      assert(metricsType.contains(key1))
      assert(metricsType.contains(key2))
    }
}
