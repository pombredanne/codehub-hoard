package com.bah.heimdall.common

import com.typesafe.config.Config
import com.bah.heimdall.common.AppConstants._
import org.apache.kafka.clients.consumer.{ConsumerConfig, ConsumerRecord, ConsumerRecords, KafkaConsumer => JavaKafkaConsumer}

import collection.JavaConverters._
import scala.util.{Failure, Success, Try}

object KafkaConsumer {

  def apply(conf: Config): KafkaConsumer = {
    val kafkaConsumer = new KafkaConsumer
    kafkaConsumer.consumer = new JavaKafkaConsumer[String, String](getConsumerConfig(conf).asJava)
    kafkaConsumer
  }

  def getConsumerConfig(conf: Config): Map[String, Object] = {
    Map[String, Object](
      ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG -> conf.getString(KAFKA_BOOTSTRAP_SERVERS),
      ConsumerConfig.GROUP_ID_CONFIG -> conf.getString(KAFKA_GROUP_ID),
      ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG -> conf.getString(KAFKA_ENABLE_AUTO_COMMIT),
      ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG -> conf.getString(KAFKA_AUTO_COMMIT_INTERVAL_MS),
      ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG -> conf.getString(KAFKA_SESSION_TIMEOUT_MS),
      ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG -> "org.apache.kafka.common.serialization.StringDeserializer",
      ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG -> "org.apache.kafka.common.serialization.StringDeserializer")
  }
}

class KafkaConsumer {
  var consumer: JavaKafkaConsumer[String, String] = null

  def getMessages(topic : String, conf:Config): Option[List[KafkaMessage]] = {
    val topics = List(topic)
    consumer.subscribe(topics.asJava)
    val messages = consumer.poll(1000).asScala
    consumer.commitSync();
    if(messages.size >0 ){
      val message = messages.map(record => {
        KafkaMessage(record.key(), record.value())
      })
      Some(message.toList)
    }else{
      None
    }
  }

  def close = {
    consumer.close()
  }
}

case class KafkaMessage(key:String, value:String)