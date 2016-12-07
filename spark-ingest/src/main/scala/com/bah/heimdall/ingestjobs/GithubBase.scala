package com.bah.heimdall.ingestjobs

import com.bah.heimdall.common.AppConfig
import com.bah.heimdall.common.AppConstants._
import com.bah.heimdall.common.HttpUtils._
import com.bah.heimdall.common.JsonUtils._
import org.json4s._

import scala.collection.mutable.ArrayBuffer


trait GithubBase {
  def isPublic(env:String) = (env == "PUBLIC")

  def getPublicOrgsList(): Array[String] = {
    AppConfig.conf.getString(ORGS).split(",").map(getSourceUrl(PUBLIC) + "users/" + _ +"?"+ getAccessToken(PUBLIC))
  }

  def getSourceUrl(env:String) = {
    if(isPublic(env)) AppConfig.conf.getString(PUB_GITHUB_API_URL) else AppConfig.conf.getString(ENT_GITHUB_API_URL)
  }

  def getAccessToken(env:String) = {
    val accessToken = if(isPublic(env)) AppConfig.conf.getString(PUB_ACCESS_TOKEN) else AppConfig.conf.getString(ENT_ACCESS_TOKEN)
    s"access_token=$accessToken"
  }

  def getEnterpriseOrgTypesList(): Array[String] = {
    "organizations,users".split(",").map(getSourceUrl(ENTERPRISE) + _ +"?since=0&per_page=100&"+ getAccessToken(ENTERPRISE))
  }

  def getOrgData(url: String): JValue = {
    getJsonResponse(url, false)
  }

  def getOrgRepos(env:String, orgRepoUrl: String): JValue = {
    getJsonResponse(s"$orgRepoUrl?" + getAccessToken(env), false)
  }

  def getPagedRepoProperties(env:String, org: String, repoName: String, propertyName: String): ArrayBuffer[JValue] = {
    val respPerPage = if (AppConfig.conf.getInt(RESPONSE_PER_PAGE) > 0) AppConfig.conf.getInt(RESPONSE_PER_PAGE) else 100
    getResponseWithPagedData(getSourceUrl(env) + s"repos/$org/$repoName/$propertyName?since=0&per_page=$respPerPage&" + getAccessToken(env), true)
  }

  def getRepoProperties(env:String, org: String, repoName: String, propertyName: String): String = {
    getResponse(getSourceUrl(env) + s"repos/$org/$repoName/$propertyName?" + getAccessToken(env), true)
  }

}
