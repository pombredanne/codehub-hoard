package com.bah.heimdall.ingestjobs

/**
  * Domain model for the Github data
  */
object Project {
  case class OrgRepo(stage_id:String,
                     organization:Org,
                     origin:String,
                     repository:String,
                     repository_url:String,
                     full_name:String,
                     project_name:String,
                     project_description:String,
                     language:String,
                     stars:Int,
                     forks:Forks,
                     releases:List[Release],
                     updated_at:String,
                     created_at:String,
                     contributors_list:List[Contributor],
                     languages:Map[String,String],
                     readMe: ReadMe,
                     watchers: Int,
                     contributors:Int,
                     commits: Int,
                     rank:Int,
                     suggest:List[SuggestField])
  case class Org(organization:String, organization_url:String, org_avatar_url:String, org_type:String)
  case class Contributor(username:String, profile_url:String, avatar_url:String, user_type:String)
  case class ReadMe(content:String, url:String)
  case class SuggestField(input:List[String], output:String)
  case class Forks(forkedRepos:List[ForkRepo])
  case class ForkRepo(id:String, name:String, org_name:String)
  case class Release(id:String, name:String, tag_name:String, assets:List[ReleaseAsset], total_downloads:Int)
  case class ReleaseAsset(id:String, name:String, label:String, size:Int, download_count:Int)
}
