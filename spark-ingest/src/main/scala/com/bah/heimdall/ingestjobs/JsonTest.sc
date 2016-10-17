import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.JsonDSL._
import org.json4s.jackson.Serialization.write

implicit val formats = DefaultFormats

val languages = """{"Python":49623,"Shell":1717}"""

val langKeys = parse(languages).values

val test = List("1","2","3")

val arr : JArray = test.toSeq

write(arr)



