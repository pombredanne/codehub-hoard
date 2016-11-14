package com.bah.heimdall.ingestjobs

import com.bah.heimdall.ingestjobs.Project.Org

object Code {
  //Project Health
  case class Metric(stage_source:String,
                    stage_id:String,
                    organization:Org,
                    project_name:String,
                    origin: String,
                    language:String,
                    updated_at:String,
                    //root_dir:String,
                    //src_list:List[String],
                    metrics:Map[String,Map[String,String]]
                   )
}
