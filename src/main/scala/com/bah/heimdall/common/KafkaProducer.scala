package com.bah.heimdall.common

import java.util.concurrent.TimeUnit

import com.typesafe.config.Config
import org.apache.kafka.clients.producer.{ProducerConfig, ProducerRecord, KafkaProducer => JavaKafkaProducer}
import com.bah.heimdall.common.AppConstants._

import collection.JavaConverters._
import scala.util.{Failure, Success, Try}

object KafkaProducer {

  def apply(conf: Config): KafkaProducer = {
    val kafkaProducer = new KafkaProducer
    kafkaProducer.producer = new JavaKafkaProducer[String,String](getProducerConfig(conf).asJava)
    kafkaProducer
  }

  def getProducerConfig(conf:Config):Map[String, Object] = {
    Map[String, Object](
      ProducerConfig.BOOTSTRAP_SERVERS_CONFIG -> conf.getString(KAFKA_BOOTSTRAP_SERVERS),
      ProducerConfig.ACKS_CONFIG -> conf.getString(KAFKA_ACKS),
      ProducerConfig.RETRIES_CONFIG -> conf.getString(KAFKA_RETRIES),
      ProducerConfig.BATCH_SIZE_CONFIG -> conf.getString(KAFKA_BATCH_SIZE),
      ProducerConfig.LINGER_MS_CONFIG -> "1",
      ProducerConfig.BUFFER_MEMORY_CONFIG -> conf.getString(KAFKA_BUFFER_MEMORY),
      ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG -> "org.apache.kafka.common.serialization.StringSerializer",
      ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG -> "org.apache.kafka.common.serialization.StringSerializer")
  }
}


class KafkaProducer {
  var producer: JavaKafkaProducer[String, String] = null

  /**
    * Messages are usually sent asynchronously but this method calls a get to block and return only
    * after the message send completes
    *
    * @param topic
    * @param msg
    * @param conf
    * @return
    */
  def sendMessageBlocking(topic:String, msg:KafkaMessage, conf:Config): Boolean ={
    val messageRecord  = new ProducerRecord[String,String](topic,msg.key,msg.value)

    val status = Try(producer.send(messageRecord).get(conf.getInt(KAFKA_PRODUCER_TIMEOUT), TimeUnit.MILLISECONDS)) match {
      case Success(status) => {
        println(s"Sent message for batchId:${msg.key} to topic:$topic successfully")
        true
      }
      case Failure(ex) =>{
        println(s"$STAGE_ERROR:Failed sending message for batchId:${msg.key} to topic:$topic")
        ex.printStackTrace()
        false
      }
    }
    status
  }

  def close()={
    if (producer != null) producer.close()
  }
}
