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

export interface ScheduledTask {
  id: string
  email: string
  repositories: string[]
  frequency: 'immediate' | 'daily' | 'weekly' | 'monthly'
  weekday?: string
  monthDay?: string
  executeTime?: string
  created_at: string
}

export interface HotReposResponse {
  repos: Repo[]
  summary: string
}

export interface TrackedReposResponse {
  repos: TrackedRepo[]
  summary: string
} 