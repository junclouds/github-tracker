import { Repo, TrackedRepo } from '../types'

const API_BASE_URL = 'http://localhost:8000'  // 添加后端服务器地址

export async function fetchHotRepos(): Promise<Repo[]> {
  const response = await fetch(`${API_BASE_URL}/api/hot-repos`)
  if (!response.ok) {
    throw new Error('Failed to fetch hot repos')
  }
  return response.json()
}

export async function fetchTrackedRepos(days: number = 1): Promise<TrackedRepo[]> {
  const response = await fetch(`${API_BASE_URL}/api/tracked-repos?days=${days}`)
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

// 修改 refreshActivities 函数，添加 days 参数
export const refreshActivities = async (days: number = 7) => {
  const response = await fetch(`${API_BASE_URL}/activities/refresh?days=${days}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Failed to refresh activities');
  }
  
  // 添加响应日志
  const data = await response.json();
  console.log('Refresh activities response:', data);
  return data;
};

// 添加刷新单个仓库活动的函数
export const refreshRepoActivities = async (repoFullName: string, days: number = 7) => {
  const [owner, repo] = repoFullName.split('/');
  const response = await fetch(
    `${API_BASE_URL}/activities/refresh/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}?days=${days}`,
    {
      method: 'POST',
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to refresh repository activities');
  }
  return response.json();
};