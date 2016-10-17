package com.bah.heimdall.process

import com.bah.heimdall.BaseSparkSpec
import org.apache.spark.sql.SQLContext
import org.scalatest.Matchers


class DataOutputSpec extends BaseSparkSpec with Matchers{
  val json =
    """[{"organization":"project-heimdall", "origin":"public","repository":"ui-designs","contributors":[{"username":"camelspeed","profile_url":"someurl","user_type":"User"}]},
      | {"organization":"project-heimdall", "origin":"public","repository":"hoard","contributors":[{"username":"camelspeed123","profile_url":"someurl","user_type":"User"}]}]""".stripMargin

  "Enclosing brackets" should "be removed" in {
    val result = DataOutput.stripBrackets("""[{"username":"123", "phone":[{"num":"703"},{"num","202"}]}]""")
    val expectedOut = """{"username":"123", "phone":[{"num":"703"},{"num","202"}]}"""
    assert(result == expectedOut)
  }



}
