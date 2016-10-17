package com.bah.heimdall.examples

import scala.io.Source
import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats


object ScalaDemo {

  implicit val formats = DefaultFormats

  def main(args: Array[String]): Unit = {
    val urls = List("https://api.github.com/user?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2",
                "https://api.github.com/orgs/Project-Heimdall/members?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2",
                "https://api.github.com/organizations?since=135&access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2")
    urls.par.map(get( _ ))
    println("Complete")
  }

  def get(url: String) = {
    println(url)
    try {
      val content = Source.fromURL(url).mkString
      val myjson = parse(content)
      println(content)
      println(myjson.toString())
      val loginname = myjson \ "login"
      println().toString

    } catch {
      case ioe: java.io.IOException =>  {
        println("IO Error occured while processing url " + url)
      }
      case ste: java.net.SocketTimeoutException => println("Socker timeout occured while processing url " + url)// handle this
    }

  }
}
