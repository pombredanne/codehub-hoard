import com.bah.heimdall.BaseSparkSpec
import com.bah.heimdall.common.HttpUtils._
import com.bah.heimdall.common.{AppConfig, HttpUtils, JsonUtils}
import com.bah.heimdall.ingestjobs.Project._
import com.bah.heimdall.ingestjobs.Github
import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.{read, write}
import org.scalatest.{Ignore, Matchers}

import scala.collection.immutable.List
import scala.collection.mutable.ArrayBuffer


class GithubSpec extends BaseSparkSpec with Matchers {
  val json = "{\"id\": 60997192, \"name\": \"archive-chorus-uidesigns\",\"owner\": {\"login\": \"Project-Heimdall\", \"id\": 18699526,\"avatar_url\": \"https://avatars.githubusercontent.com/u/18699526?v=3\"}},\n{\"id\": 66205992, \"name\": \"heimdall-devops\",\"owner\": {\"login\": \"Project-Heimdall\",\"id\": 18699526,\"avatar_url\": \"https://avatars.githubusercontent.com/u/18699526?v=3\"}}"
  val orgUrl = "https://api.github.com/users/project-heimdall?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2"

  implicit val formats = DefaultFormats

  val public_github_api_url = "https://api.github.com"
  val orgs = List("project-heimdall", "elastic")
  val accessToken = "access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2"


  "Contributor Json" should "be built" in {
    val contributorsJson =
        """[{"login": "kimchy",
        "id": 41300,
        "avatar_url": "https://avatars.githubusercontent.com/u/41300?v=3",
        "url": "https://api.github.com/users/kimchy",
        "html_url": "https://github.com/kimchy",
        "type": "User",
        "site_admin": false,
        "contributions": 847},
        {"login": "clintongormley",
        "id": 56599,
        "avatar_url": "https://avatars.githubusercontent.com/u/56599?v=3",
        "url": "https://api.github.com/users/clintongormley",
        "html_url": "https://github.com/clintongormley",
        "type": "User",
        "site_admin": false,
        "contributions": 201
        }]"""

    var contributors = ArrayBuffer.empty[JValue]
    contributors ++= JsonUtils.getJson(contributorsJson).children
    val (result, numCommits) = Github.buildContributors(contributors)
    println(result.toString())
    assert(numCommits == 1048)
  }

  "Full org Json" should "be returned" in {
    val appConf = AppConfig
    val orgUrls = sc.parallelize(Github.getPublicOrgsList())
    val orgsRdd = orgUrls.map(Github.getOrgData(_))
    val result = Github.pullData(orgsRdd)
    println(result.count())
    //val or = result.map(org => write(org))
    val ls = result.collect()
    ls.foreach(println(_))
    //result.map(org => System.out.println(org.toString()))
  }

  "Enterprise Github data" should "be returned" in {
    val appConf = AppConfig("C:\\dev\\projects\\spark-ingest\\conf\\application.conf")
    AppConfig.envType = "ENTERPRISE"
    val orgTypeList = Github.getEnterpriseOrgTypesList
    println("** Enterprise Orgs Types **")
    orgTypeList.foreach(println(_))
    val orgsList = (HttpUtils.getResponseWithPagedData(orgTypeList(0), true))// ++ HttpUtils.getResponseWithPagedData(orgTypeList(1), true))
    println("total orgs:" + orgsList.length)
    //orgsList.foreach(println(_))
    val orgsRdd = sc.parallelize(orgsList)
    //orgsRdd.foreach((println(_)))
    Github.pullData(orgsRdd).foreach(println(_))
  }

  "Full Org Json" should "be built" in {
    val appConf = AppConfig
    val orgRepoJson = """{"id": 469489,
                          "name": "elasticsearch.github.com",
                          "owner": {
                            "login": "elastic",
                            "id": "6764390",
                              "avatar_url": "https://avatars.githubusercontent.com/u/6764390?v=3",
                              "url": "https://api.github.com/users/elastic",
                              "html_url": "https://github.com/elastic",
                              "repos_url": "https://api.github.com/users/elastic/repos",
                              "type": "Organization"},
                          "private": false}"""
    val contributorsJson = """[{"login": "kimchy",
                        "id": 41300,
                        "avatar_url": "https://avatars.githubusercontent.com/u/41300?v=3",
                        "url": "https://api.github.com/users/kimchy",
                        "html_url": "https://github.com/kimchy",
                        "type": "User"},
                        {"login": "clintongormley",
                        "id": 56599,
                        "avatar_url": "https://avatars.githubusercontent.com/u/56599?v=3",
                        "url": "https://api.github.com/users/clintongormley",
                        "html_url": "https://github.com/clintongormley",
                        "type": "User"
                        }]"""
    val expectedJson = """{"organization":"Project-Heimdall","organization_url":"https://github.com/Project-Heimdall","org_avatar_url":"https://avatars.githubusercontent.com/u/18699526?v=3","org_type":"Organization","origin":"public","repository":"archive-chorus-uidesigns","contributors":[{"username":"kimchy","profile_url":"https://github.com/kimchy","avatar_url":"https://avatars.githubusercontent.com/u/41300?v=3","user_type":"User"},{"username":"clintongormley","profile_url":"https://github.com/clintongormley","avatar_url":"https://avatars.githubusercontent.com/u/56599?v=3","user_type":"User"}]}"""
    val orgRepo = Github.buildOrgStructure(parse("""{"login":"elastic"}"""), parse(orgRepoJson))
    //println(orgRepo)
    println(orgRepo.toString())
    //assert(write(orgRepo) == expectedJson)
  }

  "Orgs Url" should "be loaded from config" in {
    val appConf = AppConfig
    val orgs = Github.getPublicOrgsList()
    orgs should equal (Array("https://api.github.com/users/project-heimdall?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2", "https://api.github.com/users/elastic?access_token=7547b53ecee4ed32f8e14c6a84c056b935531dd2"))
  }

  "Read me json" should "be parsed correctly" in {
    val js = """{"content":"abc", "download_url":"http://url"}"""
    val readme = Github.buildReadme(js)
    assert(readme == new ReadMe("abc", "http://url"))
  }

  "Invalid Read me json" should "return empty object" in {
    val js = """{"message":"error"}"""
    val readme = Github.buildReadme(js)
    assert(readme == new ReadMe("", ""))
  }

  "count of watchers" should "be returned" in {
    var watchers = ArrayBuffer.empty[JValue]
    val jsWatchers =
      """[{"login": "jordansissel", "id": 131818},
         |{"login": "untergeek","id": 1020383}]""".stripMargin
    watchers ++= parse(jsWatchers).children
    val watchersCount = Github.buildWatchers(watchers)
    assert(watchersCount == 2)
  }


  "count of watchers" should "return 0" in {
    var watchers = ArrayBuffer.empty[JValue]
    watchers += JsonUtils.getJson("""{"STAGE_ERROR":"NotFound"}""")
    val watchersCount = Github.buildWatchers(watchers)
    assert(watchersCount == 0)
  }
}