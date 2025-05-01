export interface Repo {
  name: string
  full_name: string
  description: string
  description_zh?: string
  stars: number
  forks: number
  updated_at: string
  url: string
}

export interface Activity {
  type: string
  title: string
  title_zh?: string
  description: string
  description_zh?: string
  created_at: string
  url: string
}

export interface TrackedRepo extends Repo {
  activities: Activity[]
  has_updates: boolean
  last_updated: string
  summary?: string
} 