package com.bah.heimdall.ingestjobs

object Project {
  case class Org(organization:String, organization_url:String, org_avatar_url:String, org_type:String)
  case class OrgRepo(stage_source:String,
                     id:String,
                     organization:Org,
                     origin:String,
                     repository:String,
                     repository_url:String,
                     full_name:String,
                     project_name:String,
                     project_description:String,
                     language:String,
                     stars:String,
                     forks:String,
                     releases:Int,
                     updated_at:String,
                     contributors_list:List[Contributor],
                     languages:String,
                     readMe: ReadMe,
                     watchers: Int,
                     contributors:Int,
                     commits: Int,
                     rank:Int,
                     suggest:String)
  case class Contributor(username:String, profile_url:String, avatar_url:String, user_type:String)
  case class ReadMe(content:String, url:String)
  case class Suggest(fields:List[SuggestField])
  case class SuggestField(input:String, output:String)
}
