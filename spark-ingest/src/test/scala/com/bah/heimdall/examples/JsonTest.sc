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



