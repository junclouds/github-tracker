export interface Repo {
  name: string
  full_name: string
  description?: string
  description_zh?: string
  name_zh?: string
  stars: number
  forks: number
  updated_at: string
  url: string
}

export interface Activity {
  type: string
  title: string
  created_at: string
  description: string
  url?: string
}

export interface TrackedRepo extends Repo {
  has_updates: boolean
  last_updated: string
  activities: Activity[]
}

export interface ScheduledTask {
  id: string
  email: string
  repositories: string[]
  frequency: string
  weekday?: string
  monthDay?: string
  executeTime?: string
  created_at: string
} 