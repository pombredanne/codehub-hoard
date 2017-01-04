package com.bah.heimdall.common


object AppConstants {
  //Github settings
  //Enterprise github
  val RUN_ENV = "ingest.env"
  val ENT_GITHUB_API_URL = "ingest.projects.github.enterpriseurl"
  val ENT_ACCESS_TOKEN = "ingest.projects.github.ent_accessToken"
  //Public github
  val ORGS = "ingest.projects.github.orgs"
  val PUB_GITHUB_API_URL = "ingest.projects.github.publicurl"
  val PUB_ACCESS_TOKEN = "ingest.projects.github.pub_accessToken"
  val RESPONSE_PER_PAGE = "ingest.projects.github.httpReponsePerPage"
  val PROJECT_DOC_TYPE = "ingest.projects.github.docType"
  val PROJECTS_INDEX_NAME = "ingest.projects.indexName"

  //Sonar settings
  val CODES_INDEX_NAME = "ingest.code.indexName"
  val SONAR_API_LOCAL_BASE_URL="ingest.code.sonar.api_local_base_url"
  val SONAR_API_REMOTE_BASE_URL="ingest.code.sonar.api_remote_base_url"
  val SONAR_PROJECT_HEALTH_METRICS="ingest.code.sonar.health_metrics"


  //Elastic search
  val ES_ID_SEPARATOR = "_"


  //Stage Constants
  val STAGE_ERROR = "STAGE_ERROR:"
  val PUBLIC = "PUBLIC"
  val ENTERPRISE = "ENTERPRISE"
  val ALL = "ALL"
  val SRC_GITHUB = "GITHUB"
  val SRC_SONAR = "SONAR"

  //Kafka
  val KAFKA_BOOTSTRAP_SERVERS = "ingest.kafka.bootstrap_servers"
  //Producer
  val KAFKA_ACKS = "ingest.kafka.producer.acks"
  val KAFKA_RETRIES = "ingest.kafka.producer.retries"
  val KAFKA_BATCH_SIZE = "ingest.kafka.producer.batch_size"
  val KAFKA_BUFFER_MEMORY = "ingest.kafka.producer.buffer_memory"
  val KAFKA_PRODUCER_TIMEOUT = "ingest.kafka.producer.timeout"
  //Consumer
  val KAFKA_GROUP_ID = "ingest.kafka.consumer.group_id"
  val KAFKA_ENABLE_AUTO_COMMIT = "ingest.kafka.consumer.enable_auto_commit"
  val KAFKA_AUTO_COMMIT_INTERVAL_MS = "ingest.kafka.consumer.auto_commit_interval_ms"
  val KAFKA_SESSION_TIMEOUT_MS = "ingest.kafka.consumer.session_timeout_ms"
  //Ingest Topics
  val INGEST_COMPLETION_TOPIC = "ingest.kafka.completion_topic"

}
