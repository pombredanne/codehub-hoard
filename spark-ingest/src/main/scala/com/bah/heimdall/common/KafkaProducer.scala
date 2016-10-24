package com.bah.heimdall.common

import java.util.concurrent.TimeUnit

import com.typesafe.config.Config
import org.apache.kafka.clients.producer.{ProducerRecord, KafkaProducer => JavaKafkaProducer}
import com.bah.heimdall.common.AppConstants._

import collection.JavaConverters._
import scala.util.{Failure, Success, Try}

object KafkaProducer {
  val BOOTSTRAP_SERVERS = "bootstrap.servers"
  val ACKS = "acks"
  val RETRIES = "retries"
  val BATCH_SIZE = "batch.size"
  val LINGER_MS = "linger.ms"
  val BUFFER_MEMORY = "buffer.memory"
  val KEY_SERLZR = "key.serializer"
  val VAL_SERLZR = "value.serializer"

  def apply(conf: Config): KafkaProducer = {
    val kafkaProducer = new KafkaProducer
    kafkaProducer.producer = new JavaKafkaProducer[String,String](getProducerConfig(conf).asJava)
    kafkaProducer
  }

  def getProducerConfig(conf:Config):Map[String, Object] = {
    Map[String, Object](
      BOOTSTRAP_SERVERS -> conf.getString(KAFKA_BOOTSTRAP_SERVERS),
      ACKS -> conf.getString(KAFKA_ACKS),
      RETRIES -> conf.getString(KAFKA_RETRIES),
      BATCH_SIZE -> conf.getString(KAFKA_BATCH_SIZE),
      LINGER_MS -> "1",
      BUFFER_MEMORY -> conf.getString(KAFKA_BUFFER_MEMORY),
      KEY_SERLZR -> "org.apache.kafka.common.serialization.StringSerializer",
      VAL_SERLZR -> "org.apache.kafka.common.serialization.StringSerializer")
  }
}


class KafkaProducer {
  var producer: JavaKafkaProducer[String, String] = null

  /**
    * Messages are usually sent asynchronously but this method calls a get to block and return only
    * after the message is send completes
    *
    * @param topic
    * @param key
    * @param message
    * @param conf
    * @return
    */
  def sendMessageBlocking(topic:String, key:String, message:String, conf:Config): Boolean ={
    val messageRecord  = new ProducerRecord[String,String](topic,key,message)

    val status = Try(producer.send(messageRecord).get(conf.getInt(KAFKA_PRODUCER_TIMEOUT), TimeUnit.MILLISECONDS)) match {
      case Success(status) => {
        println(s"Sent message:$message to topic:$topic successfully")
        true
      }
      case Failure(ex) =>{
        println(s"$STAGE_ERROR:Failed sending message:$message to topic:$topic")
        false
      }
    }
    status
  }

  def close()={
    if (producer != null) producer.close()
  }
}
