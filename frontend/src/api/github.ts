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

export async function searchRepos(query: string): Promise<Repo[]> {
  const response = await fetch(`${API_BASE_URL}/api/search-repos?query=${encodeURIComponent(query)}`)
  if (!response.ok) {
    throw new Error('Failed to search repos')
  }
  return response.json()
}

// 获取定时任务列表
export async function fetchScheduledTasks() {
  const response = await fetch(`${API_BASE_URL}/api/scheduled-tasks`)
  if (!response.ok) {
    throw new Error('Failed to fetch scheduled tasks')
  }
  return response.json()
}

// 创建定时任务
export async function createScheduledTask(taskData: {
  email: string;
  repositories: string[];
  frequency: string;
  weekday?: string;
  monthDay?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/api/scheduled-tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  })
  if (!response.ok) {
    throw new Error('Failed to create scheduled task')
  }
  return response.json()
}

// 删除定时任务
export async function deleteScheduledTask(taskId: string) {
  const response = await fetch(`${API_BASE_URL}/api/scheduled-tasks/${taskId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete scheduled task')
  }
  return response.json()
}

// 立即执行定时任务
export async function executeScheduledTask(taskId: string) {
  const response = await fetch(`${API_BASE_URL}/api/scheduled-tasks/${taskId}/execute`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to execute scheduled task')
  }
  return response.json()
}

// 更新定时任务
export async function updateScheduledTask(
  taskId: string,
  taskData: {
    email: string;
    repositories: string[];
    frequency: string;
    weekday?: string;
    monthDay?: string;
  }
) {
  const response = await fetch(`${API_BASE_URL}/api/scheduled-tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  })
  if (!response.ok) {
    throw new Error('Failed to update scheduled task')
  }
  return response.json()
}