package com.bah.heimdall.ingestjobs

import com.bah.heimdall.ingestjobs.Project.Org

object Code {
  //Project Health
  //Sonar Metric
  case class Metric(stage_source:String,
                    stage_id:String,
                    organization:Org,
                    project_name:String,
                    origin: String,
                    language:String,
                    updated_at:String,
                    metrics:Map[String,Map[String,String]]
                   )
  //Project Dependencies
  case class Dependency(components: List[Component],
                        language:String,
                        org:String,
                        project_name:String)

  case class Component(artifactId:String,
                        exclusions:String,
                        version:String)
}
