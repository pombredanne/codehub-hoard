import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.JsonDSL._
import org.json4s.jackson.Serialization.write

implicit val formats = DefaultFormats

val languages = """{"Python":49623,"Shell":1717}"""

val langKeys: Map[String, String] = parse(languages).mapField( k =>{
  (k._1, k._2)}).extract[Map[String, String]]

val keysSuggest = write(langKeys.keySet)




val test = List("1","2","3")

val arr : JArray = test.toSeq

write(arr)

//*******************************
case class Address(street: String, city: String)
case class PersonWithAddresses(name: String, addresses: Map[String, Map[String, String]])
val mapjson = parse("""
         {
           "name": "joe",
           "addresses": {
             "address1": {
               "street": "Bulevard",
               "city": "Helsinki"
             },
             "address2": {
               "street": "Soho",
               "city": "London"
             }
           }
         }""")
val js =  mapjson.extract[PersonWithAddresses]
val backtoJson = write(js)
val jsonResponse =
  """
    |[{"id":4809,"uuid":"AVgHDUJU0ThXESs5KBt3","key":"heimdall-hoard","name":"heimdall-hoard of Project-Heimdall","scope":"PRJ","qualifier":"TRK","creationDate":"2016-10-27T16:50:59+0000","date":"2016-10-27T19:39:27+0000","lname":"heimdall-hoard of Project-Heimdall","version":"1.0","msr":[{"key":"complexity","val":312.0,"frmt_val":"312"},{"key":"bugs","val":1.0,"frmt_val":"1"},{"key":"code_smells","val":38.0,"frmt_val":"38"},{"key":"security_rating","val":1.0,"frmt_val":"A","data":"A"},{"key":"reliability_rating","val":3.0,"frmt_val":"C","data":"C"},{"key":"violations","val":39.0,"frmt_val":"39"},{"key":"vulnerabilities","val":0.0,"frmt_val":"0"}]}]
  """.stripMargin
val metricJson = parse(jsonResponse)
val metrics = (metricJson \ "msr").extract[List[Map[String, String]]]
write(metrics)

