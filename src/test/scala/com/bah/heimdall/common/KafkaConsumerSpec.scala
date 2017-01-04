package com.bah.heimdall.common

import com.bah.heimdall.{BaseSpec, TestAppConfig}


class KafkaConsumerSpec extends BaseSpec{
  "message" should "be retrieved from the topic" in {
    val conf = TestAppConfig.getConf
    val topic = "testtopic"
    val producer = KafkaProducer(conf)
    producer.sendMessageBlocking(topic, new KafkaMessage("key1", "key1:value1"), conf)

    val consumer = KafkaConsumer(conf)
    val message = consumer.getMessages("", conf)

    assert(message.get(0).key == "key1")
    assert(message.get(0).value == "value1")
  }
}
