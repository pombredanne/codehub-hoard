package com.bah.heimdall.common

import com.bah.heimdall.{BaseSpec, TestAppConfig}
import com.bah.heimdall.common.AppConstants._

class KafkaProducerSpec extends BaseSpec{
  "Good message" should "return success" in {
    val conf = TestAppConfig.getConf
    val producer = KafkaProducer(conf)
    val successStatus = producer.sendMessageBlocking(conf.getString(INGEST_COMPLETION_TOPIC), new KafkaMessage("key123", "key123:testMsg2"), conf)
    producer.close()
    assert(successStatus == true)
  }

  "Invalid topic name" should "return unsuccessful status" in {
    val conf = TestAppConfig.getConf
    val producer = KafkaProducer(conf)
    val successStatus = producer.sendMessageBlocking("", new KafkaMessage("key123", "key123:testMsg2"), conf)
    producer.close()
    assert(successStatus == false)
  }

  "new topic name" should "return unsuccessful status" in {
    val conf = TestAppConfig.getConf
    val producer = KafkaProducer(conf)
    val successStatus = producer.sendMessageBlocking("newtopic", new KafkaMessage("key123", "key123:testMsg2"), conf)
    producer.close()
    assert(successStatus == false)
  }
}
