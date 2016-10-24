package com.bah.heimdall

import com.bah.heimdall.common.AppConfig
import com.typesafe.config._
import com.bah.heimdall.common.AppConstants._

object TestAppConfig {
  def getConf: Config = {
    val conf = ConfigFactory.load()
    val app = new AppConfig()
    app.validate(conf)
    conf
  }
}

class TestAppConfig {
  def validate(conf: Config) = {
    if (conf.getString(PUB_GITHUB_API_URL).isEmpty)
      throw new RuntimeException(getMessage(PUB_GITHUB_API_URL))
    if (conf.getString(ORGS).isEmpty)
      throw new RuntimeException(getMessage(ORGS))
    if (conf.getString(PUB_ACCESS_TOKEN).isEmpty)
      throw new RuntimeException(getMessage(PUB_ACCESS_TOKEN))
    def getMessage(propName: String) = s"$propName is not set in configuration file"
  }
}
