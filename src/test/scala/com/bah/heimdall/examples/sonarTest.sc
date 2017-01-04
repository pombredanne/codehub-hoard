import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization._
import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.JsonDSL._
import org.json4s.jackson.Serialization.write

implicit val formats = DefaultFormats

val jsonResponse =
  """
    |[{"id":4809,"uuid":"AVgHDUJU0ThXESs5KBt3",
    |"key":"heimdall-hoard",
    |"name":"heimdall-hoard of Project-Heimdall",
    |"scope":"PRJ",
    |"qualifier":"TRK",
    |"creationDate":"2016-10-27T16:50:59+0000",
    |"date":"2016-10-27T19:39:27+0000",
    |"lname":"heimdall-hoard of Project-Heimdall",
    |"version":"1.0",
    |"msr":[{"key":"complexity","val":312.0,"frmt_val":"312"},
    |{"key":"bugs","val":1.0,"frmt_val":"1"},
    |{"key":"code_smells","val":38.0,"frmt_val":"38"},
    |{"key":"security_rating","val":1.0,"frmt_val":"A","data":"A"},
    |{"key":"reliability_rating","val":3.0,"frmt_val":"C","data":"C"},
    |{"key":"violations","val":39.0,"frmt_val":"39"},
    |{"key":"vulnerabilities","val":0.0,"frmt_val":"0"}]}]
  """.stripMargin


val metricJson = parse(jsonResponse)
val metrics = (metricJson \ "msr").extract[List[Map[String, String]]]
//val metricsFinal = metrics.map(m)
var m  = Map.empty[String, Map[String, String]]
metrics.foreach(entry => {
  m += (entry.get("key").getOrElse("") -> entry)
})
println(m)

write(m)






