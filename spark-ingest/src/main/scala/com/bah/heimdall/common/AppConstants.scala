package com.bah.heimdall.common


object AppConstants {
  //config settings
  //Github settings
  //Enterprise github
  val RUN_ENV = "ingest.projects.env"
  val ENT_GITHUB_API_URL = "ingest.projects.github.enterpriseurl"
  val ENT_ACCESS_TOKEN = "ingest.projects.github.ent_accessToken"
  //Public github
  val ORGS = "ingest.projects.github.orgs"
  val PUB_GITHUB_API_URL = "ingest.projects.github.publicurl"
  val PUB_ACCESS_TOKEN = "ingest.projects.github.pub_accessToken"
  val RESPONSE_PER_PAGE = "ingest.projects.github.httpReponsePerPage"
  val PROJECT_DOC_TYPE = "ingest.projects.github.docType"

  //Elastic search
  val ES_ID_SEPARATOR = "_"
  val PROJECTS_INDEX_NAME = "ingest.projects.indexName"

  //Stage Constants
  val STAGE_ERROR = "STAGE_ERROR"
  val PUBLIC = "PUBLIC"
  val ENTERPRISE = "ENTERPRISE"
  val ALL = "ALL"
}
