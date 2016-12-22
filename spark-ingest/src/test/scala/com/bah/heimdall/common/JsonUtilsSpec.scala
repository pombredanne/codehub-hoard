package com.bah.heimdall.common

import com.bah.heimdall.BaseSpec


class JsonUtilsSpec extends BaseSpec{
  "SPARK_ERROR field" should "not be found" in {
    assert(JsonUtils.hasField("SPARK_ERROR",JsonUtils.getJson("""[{"login":"123"}]""")) == false)
  }

  "SPARK_ERROR field" should "be found" in {
    assert(JsonUtils.hasField("SPARK_ERROR",JsonUtils.getJson("""{"SPARK_ERROR":""}""")) == true)
  }


}
