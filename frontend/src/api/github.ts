import { Repo, TrackedRepo } from '../types'

const API_BASE_URL = 'http://localhost:8000'  // 添加后端服务器地址

export async function fetchHotRepos(): Promise<Repo[]> {
  const response = await fetch(`${API_BASE_URL}/api/hot-repos`)
  if (!response.ok) {
    throw new Error('Failed to fetch hot repos')
  }
  return response.json()
}

export async function fetchTrackedRepos(): Promise<TrackedRepo[]> {
  const response = await fetch(`${API_BASE_URL}/api/tracked-repos`)
  if (!response.ok) {
    throw new Error('Failed to fetch tracked repos')
  }
  return response.json()
}

export async function trackRepo(repoFullName: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/track-repo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ repo_full_name: repoFullName }),
  })
  if (!response.ok) {
    throw new Error('Failed to track repo')
  }
}

export async function untrackRepo(repoFullName: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/untrack-repo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ repo_full_name: repoFullName }),
  })
  if (!response.ok) {
    throw new Error('Failed to untrack repo')
  }
} 