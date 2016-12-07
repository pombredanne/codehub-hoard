package com.bah.heimdall.common

import java.io.File

import com.typesafe.config._
import com.bah.heimdall.common.AppConstants._

object AppConfig {
  private var config = ConfigFactory.empty()
  def conf :Config = config

  def apply(configFile:String): AppConfig = {
    val app = new AppConfig()
    if (configFile.isEmpty) {
      println(s"Configuration file was set not while submitting the Job")
      throw new RuntimeException(s"Configuration file could not be loaded from $configFile")
    }
    config = ConfigFactory.parseFile(new File(configFile))
    app.validate(config)
    app
  }
}

class AppConfig {
  def getMessage(propName:String) = s"$propName is not set in configuration file"

  def validate(conf : Config) = {
    if(conf.getString(PUB_GITHUB_API_URL).isEmpty)
      throw new RuntimeException(getMessage(PUB_GITHUB_API_URL))
    if(conf.getString(ORGS).isEmpty)
      throw new RuntimeException(getMessage(ORGS))
    if(conf.getString(PUB_ACCESS_TOKEN).isEmpty)
      throw new RuntimeException(getMessage(PUB_ACCESS_TOKEN))
    if(conf.getString(ENT_ACCESS_TOKEN).isEmpty)
      throw new RuntimeException(getMessage(ENT_ACCESS_TOKEN))
    //Kafka Required properties
    if(conf.getString(KAFKA_BOOTSTRAP_SERVERS).isEmpty)
      throw new RuntimeException(getMessage(KAFKA_BOOTSTRAP_SERVERS))
  }
}
