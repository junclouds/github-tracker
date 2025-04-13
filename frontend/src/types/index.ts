export interface Repo {
  name: string
  full_name: string
  description: string
  stars: number
  forks: number
  updated_at: string
}

export interface Activity {
  type: string
  title: string
  created_at: string
}

export interface TrackedRepo extends Repo {
  activities: Activity[]
} 