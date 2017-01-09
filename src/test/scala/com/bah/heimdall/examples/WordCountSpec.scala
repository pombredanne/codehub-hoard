package com.bah.heimdall.examples

import com.bah.heimdall.BaseSparkSpec
import org.scalatest.{Matchers}

class WordCountSpec extends BaseSparkSpec with Matchers {

  "Unique words" should "be counted" in {
    val testLines = Seq("First day fall", "fall starts September")
    val linesRdd = sc.parallelize(testLines)
    val countRdd = WordCount.getWC(linesRdd)

    //Assert
    countRdd.count() should equal(5)

    val wordCountMap = countRdd.collectAsMap()
    assert(wordCountMap.get("First").get == 1)
    assert(wordCountMap.get("day").get == 1)
    assert(wordCountMap.get("fall").get == 2)
    assert(wordCountMap.get("September").get == 1)
    assert(wordCountMap.get("starts").get == 1)
  }

}
