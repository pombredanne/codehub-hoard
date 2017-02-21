package com.bah.heimdall.common

import java.net.InetAddress

import com.typesafe.config.Config
import org.elasticsearch.client.Client
import org.elasticsearch.client.transport.TransportClient
import org.elasticsearch.common.settings.Settings
import org.elasticsearch.common.transport.InetSocketTransportAddress
import org.elasticsearch.index.query.QueryBuilders

import collection.JavaConverters._

object ElasticClientManager {
  private var esClient : Client = null

  def apply(conf: Config): ElasticClientManager = {
    val esClientManager = new ElasticClientManager()
    esClient = setupESClient(conf)
    esClientManager
  }


  def setupESClient(conf: Config): Client ={
    val port = 9300//conf.getString("")
    val esNodes = List("localhost")
    val addresses = esNodes.map { host => new InetSocketTransportAddress(InetAddress.getByName(host), port) }
    val settings = Settings.settingsBuilder()
      .put("cluster.name", "stagesearch")
      .build()
    TransportClient.builder().settings(settings).build().addTransportAddresses(addresses: _*)
  }
}

class ElasticClientManager{
  import ElasticClientManager._

  def getAllDocuments(index:String) = {
    esClient.admin().indices().prepareRefresh(index).get()
    esClient.prepareSearch(index).execute().actionGet()
  }

  def getAllDocumentIds(index:String) = {
    esClient.admin().indices().prepareRefresh(index).get()
    esClient.prepareSearch(index).setSize(1500).addFields("id", "text").execute().actionGet()
  }
}
