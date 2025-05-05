from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv
from .github_tracker import GitHubTracker
from .repo_activity_tracker import RepoActivityTracker
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import parser
from .date_handler import DateHandler
import logging 
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置日志
logging.basicConfig(level=logging.INFO)

# 加载环境变量
load_dotenv()

# 初始化定时任务调度器
scheduler = BackgroundScheduler()

app = FastAPI(title="GitHub Tracker API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 开发服务器的地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 headers
    expose_headers=["*"]  # 允许浏览器访问的响应头
)

# 获取项目根目录
base_dir = Path(__file__).parent.parent
github_token = os.getenv('GITHUB_TOKEN')
zhipu_api_key = os.getenv('ZHIPU_API_KEY')

if not github_token:
    raise ValueError("请设置 GITHUB_TOKEN 环境变量")

# 初始化追踪器
github_tracker = GitHubTracker(github_token, base_dir)
repo_tracker = RepoActivityTracker(github_token, base_dir)

class RepoTrackRequest(BaseModel):
    repo_full_name: str

class ScheduledTaskRequest(BaseModel):
    email: EmailStr
    repositories: List[str]
    frequency: str  # immediate, daily, weekly, monthly
    weekday: Optional[str] = None
    monthDay: Optional[str] = None
    executeTime: Optional[str] = "09:00"  # 默认早上9点执行

class ScheduledTask(ScheduledTaskRequest):
    id: str
    created_at: datetime

@app.get("/api/hot-repos")
async def get_hot_repos() -> List[Dict[str, Any]]:
    """获取热门仓库列表"""
    try:
        print("开始获取热门仓库...")  # 添加调试日志
        repos = github_tracker.get_trending_repositories()
        print(f"获取到 {len(repos)} 个仓库")  # 添加调试日志
        
        # 转换数据格式以匹配前端需求
        formatted_repos = []
        for repo in repos:
            formatted_repos.append({
                "name": repo["name"].split("/")[-1],  # 从 full_name 中提取仓库名
                "full_name": repo["name"],
                "description": repo["description"],
                "description_zh": repo["description_zh"],
                "stars": repo["stars"],
                "forks": repo["forks"],
                "updated_at": repo["updated_at"].isoformat(),
                "url": repo["url"]
            })
        print(f"返回格式化后的仓库数据: {formatted_repos}")  # 添加调试日志
        return formatted_repos
    except Exception as e:
        print(f"获取热门仓库时出错: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracked-repos")
async def get_tracked_repos(days: int = 1) -> List[Dict[str, Any]]:
    """获取已追踪的仓库列表
    
    Args:
        days: 获取最近几天的活动，默认为1天
    """
    try:
        # 从配置文件读取追踪的仓库
        config_file = base_dir / "config" / "tracked_repos.json"
        if not config_file.exists():
            return []
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 获取每个仓库的最新活动
        tracked_repos = []
        activity_dir = base_dir / "data" / "repo_activities"
        
        for repo in config.get('repositories', []):
            repo_full_name = repo['full_name']
            
            # 获取仓库详情信息
            repo_details = github_tracker.get_repository_details(repo_full_name)
            
            # 查找该仓库的最新活动文件
            repo_files = list(activity_dir.glob(f"{repo_full_name.replace('/', '_')}*.json"))
            repo_files.sort(reverse=True)  # 最新的文件排在前面
            
            repo_data = {
                "full_name": repo_full_name,  # 仓库的完整名称
                "name": repo_details.get("name", repo_full_name.split("/")[-1]),  # 仓库名称
                "description": repo_details.get("description", ""),  # 仓库描述
                "stars": repo_details.get("stars", 0),  # 星标数量
                "forks": repo_details.get("forks", 0),  # Fork 数量
                "updated_at": repo_details.get("updated_at", ""),  # 最后更新时间
                "has_updates": False,  # 是否有更新
                "last_updated": "",  # 最后更新的时间
                "activities": []  # 活动列表
            }
            
            if repo_files:
                try:
                    with open(repo_files[0], 'r', encoding='utf-8') as f:
                        activity_data = json.load(f)
                        
                    # 更新仓库信息
                    repo_data["last_updated"] = activity_data.get("timestamp", "")
                    
                    # 检查是否有未读更新（根据传入的days参数）
                    recent_time = DateHandler.get_recent_time(days)  # datetime.now() - timedelta(days=days)
                    logging.info(f"{days}天前的日期: {recent_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 处理提交
                    activities = []
                    for commit in activity_data.get("activities", {}).get("commits", []):
                        commit_date = DateHandler.parse(commit["date"]) #parser.isoparse(commit["date"])
                        logging.info(f"commit 日期: {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        activities.append({
                            "type": "Commit",
                            "title": commit["message"].split("\n")[0],
                            "created_at": commit["date"],
                            "description": f"作者: {commit['author']}",
                            "url": commit.get("url", "")
                        })
                        if commit_date > recent_time:
                            repo_data["has_updates"] = True
                    
                    # 处理议题
                    for issue in activity_data.get("activities", {}).get("issues", []):
                        issue_date = DateHandler.parse(issue["updated_at"]) #parser.isoparse(issue["updated_at"])
                        logging.info(f"issue 日期: {issue_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        activities.append({
                            "type": "Issue",
                            "title": issue["title"],
                            "created_at": issue["updated_at"],
                            "description": f"状态: {issue['state']}",
                            "url": issue.get("url", "")
                        })
                        if issue_date > recent_time:
                            repo_data["has_updates"] = True
                    
                    # 处理PR
                    for pr in activity_data.get("activities", {}).get("pull_requests", []):
                        pr_date = DateHandler.parse(pr["updated_at"]) #parser.isoparse(pr["updated_at"])
                        logging.info(f"pr 日期: {pr_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        activities.append({
                            "type": "Pull Request",
                            "title": pr["title"],
                            "created_at": pr["updated_at"],
                            "description": f"状态: {pr['state']}",
                            "url": pr.get("url", "")
                        })
                        if pr_date > recent_time:
                            repo_data["has_updates"] = True
                    
                    # 处理发布
                    for release in activity_data.get("activities", {}).get("releases", []):
                        release_date = DateHandler.parse(release["date"]) #parser.isoparse(release["date"])
                        logging.info(f"release 日期: {release_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        activities.append({
                            "type": "Release",
                            "title": release["name"],
                            "created_at": release["date"],
                            "description": f"标签: {release['tag']}",
                            "url": release.get("url", "")
                        })
                        if release_date > recent_time:
                            repo_data["has_updates"] = True
                    
                    # 按时间排序，最新的在前
                    activities.sort(key=lambda x: x["created_at"], reverse=True)
                    repo_data["activities"] = activities
                    
                except Exception as e:
                    print(f"处理仓库 {repo_full_name} 活动数据时出错: {str(e)}")
            
            tracked_repos.append(repo_data)
            
        return tracked_repos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/track-repo")
async def track_repo(request: RepoTrackRequest):
    """添加要追踪的仓库"""
    try:
        config_file = base_dir / "config" / "tracked_repos.json"
        config_dir = config_file.parent
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取现有配置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"repositories": []}
            
        # 检查仓库是否已经在追踪列表中
        repo_list = config.get('repositories', [])
        if not any(repo['full_name'] == request.repo_full_name for repo in repo_list):
            # 添加新仓库
            repo_list.append({
                "full_name": request.repo_full_name
            })
            config['repositories'] = repo_list
            
            # 保存更新后的配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        return {"message": "Repository tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/untrack-repo")
async def untrack_repo(request: RepoTrackRequest):
    """取消追踪仓库"""
    try:
        config_file = base_dir / "config" / "tracked_repos.json"
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No tracked repositories found")
            
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 移除指定的仓库
        repo_list = config.get('repositories', [])
        config['repositories'] = [
            repo for repo in repo_list 
            if repo['full_name'] != request.repo_full_name
        ]
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        return {"message": "Repository untracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh-activities")
async def refresh_activities():
    """刷新所有追踪仓库的活动"""
    try:
        repo_tracker.track_all_repos()
        return {"message": "Activities refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/activities/refresh")
async def refresh_activities(days: int = 7):  # 添加 days 参数，默认值为 7
    """刷新所有追踪仓库的活动
    
    Args:
        days: 获取最近几天的活动，默认为 7 天
    """
    try:
        # 更新 RepoActivityTracker 中的 get_repo_activities 方法调用
        repo_tracker.track_all_repos(days=days)  # 传递 days 参数
        return {"message": f"Activities refreshed successfully for last {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/activities/refresh/{owner}/{repo}")  # 修改路由，分开处理 owner 和 repo
async def refresh_repo_activities(owner: str, repo: str, days: int = 7):
    """刷新指定仓库的活动
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        days: 获取最近几天的活动，默认为 7 天
    """
    try:
        repo_full_name = f"{owner}/{repo}"
        activities = repo_tracker.get_repo_activities(repo_full_name, days)
        if activities:
            repo_tracker.save_activities(activities)
            return {"message": f"Activities refreshed successfully for {repo_full_name}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to get activities for repository {repo_full_name}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-repos")
async def search_repos(query: str = Query(..., description="搜索关键词")) -> List[Dict[str, Any]]:
    """搜索GitHub仓库
    
    Args:
        query: 搜索关键词
    """
    try:
        # 使用 GitHub API 搜索仓库
        repos = github_tracker.search_repositories(query)
        
        # 转换数据格式以匹配前端需求
        formatted_repos = []
        for repo in repos:
            formatted_repos.append({
                "name": repo["name"].split("/")[-1],
                "full_name": repo["name"],
                "description": repo["description"],
                "stars": repo["stars"],
                "forks": repo.get("forks", 0),
                "updated_at": repo.get("updated_at", datetime.now().isoformat()),
                "url": repo["url"]
            })
        return formatted_repos
    except Exception as e:
        logging.error(f"搜索仓库时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scheduled-tasks")
async def get_scheduled_tasks() -> List[Dict[str, Any]]:
    """获取所有定时任务"""
    try:
        # 从配置文件读取定时任务
        config_file = base_dir / "config" / "scheduled_tasks.json"
        if not config_file.exists():
            return []
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return config.get('tasks', [])
    except Exception as e:
        logging.error(f"获取定时任务时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scheduled-tasks")
async def create_scheduled_task(task: ScheduledTaskRequest) -> Dict[str, Any]:
    """创建定时任务"""
    try:
        config_file = base_dir / "config" / "scheduled_tasks.json"
        config_dir = config_file.parent
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取现有配置
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {"tasks": []}
            
        # 创建新任务
        new_task = {
            "id": str(uuid.uuid4()),
            "email": task.email,
            "repositories": task.repositories,
            "frequency": task.frequency,
            "created_at": datetime.now().isoformat(),
            "executeTime": task.executeTime
        }
        
        # 添加特定频率的参数
        if task.frequency == "weekly" and task.weekday:
            new_task["weekday"] = task.weekday
        elif task.frequency == "monthly" and task.monthDay:
            new_task["monthDay"] = task.monthDay
            
        # 添加到任务列表
        config["tasks"].append(new_task)
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        # 设置定时任务
        schedule_task(new_task)
            
        return new_task
    except Exception as e:
        logging.error(f"创建定时任务时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/scheduled-tasks/{task_id}")
async def delete_scheduled_task(task_id: str) -> Dict[str, Any]:
    """删除定时任务"""
    try:
        config_file = base_dir / "config" / "scheduled_tasks.json"
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No scheduled tasks found")
            
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 移除指定的任务
        tasks = config.get('tasks', [])
        
        # 查找要删除的任务
        task_to_remove = None
        updated_tasks = []
        for task in tasks:
            if task['id'] == task_id:
                task_to_remove = task
            else:
                updated_tasks.append(task)
                
        if not task_to_remove:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
            
        # 更新配置
        config['tasks'] = updated_tasks
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        # 从调度器中移除任务
        if hasattr(scheduler, 'get_job'):
            job = scheduler.get_job(task_id)
            if job:
                scheduler.remove_job(task_id)
            
        return {"message": "Task deleted successfully", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"删除定时任务时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/scheduled-tasks/{task_id}")
async def update_scheduled_task(task_id: str, task: ScheduledTaskRequest) -> Dict[str, Any]:
    """更新定时任务"""
    try:
        config_file = base_dir / "config" / "scheduled_tasks.json"
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No scheduled tasks found")
            
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 获取所有任务
        tasks = config.get('tasks', [])
        
        # 查找并更新任务
        task_found = False
        for i, existing_task in enumerate(tasks):
            if existing_task['id'] == task_id:
                # 更新任务，保留原有的ID和创建时间
                updated_task = {
                    "id": task_id,
                    "email": task.email,
                    "repositories": task.repositories,
                    "frequency": task.frequency,
                    "created_at": existing_task.get("created_at", datetime.now().isoformat()),
                    "updated_at": datetime.now().isoformat(),
                    "executeTime": task.executeTime
                }
                
                # 添加特定频率的参数
                if task.frequency == "weekly" and task.weekday:
                    updated_task["weekday"] = task.weekday
                elif task.frequency == "monthly" and task.monthDay:
                    updated_task["monthDay"] = task.monthDay
                    
                # 更新任务
                tasks[i] = updated_task
                task_found = True
                
                # 更新调度器中的任务
                if hasattr(scheduler, 'get_job'):
                    job = scheduler.get_job(task_id)
                    if job:
                        scheduler.remove_job(task_id)
                        
                # 重新设置定时任务
                schedule_task(updated_task)
                break
                
        if not task_found:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
            
        # 更新配置
        config['tasks'] = tasks
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"更新定时任务时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scheduled-tasks/{task_id}/execute")
async def execute_scheduled_task(task_id: str) -> Dict[str, Any]:
    """立即执行定时任务"""
    try:
        config_file = base_dir / "config" / "scheduled_tasks.json"
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No scheduled tasks found")
            
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 获取所有任务
        tasks = config.get('tasks', [])
        
        # 查找要执行的任务
        task_to_execute = None
        for task in tasks:
            if task['id'] == task_id:
                task_to_execute = task
                break
                
        if not task_to_execute:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
            
        # 立即执行任务
        await execute_task(task_to_execute)
            
        return {"message": f"Task {task_id} executed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"执行定时任务时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_task(task: Dict[str, Any]):
    """执行定时任务"""
    try:
        # 获取任务所需的信息
        email = task['email']
        repositories = task['repositories']
        
        logging.info(f"开始执行定时任务: 任务ID={task.get('id')}, 邮箱={email}")
        logging.info(f"需要检查的仓库列表: {repositories}")
        
        # 收集仓库更新信息
        updates = []
        for repo_full_name in repositories:
            try:
                logging.info(f"正在获取仓库 {repo_full_name} 的活动信息...")
                # 获取仓库活动
                activities = repo_tracker.get_repo_activities(repo_full_name, days=7)  # 获取最近7天活动
                if activities and 'activities' in activities:
                    repo_activities = activities['activities']
                    
                    # 检查是否有更新
                    has_commits = bool(repo_activities.get('commits'))
                    has_issues = bool(repo_activities.get('issues'))
                    has_prs = bool(repo_activities.get('pull_requests'))
                    has_releases = bool(repo_activities.get('releases'))
                    
                    logging.info(f"仓库 {repo_full_name} 活动统计:")
                    logging.info(f"- 提交: {len(repo_activities.get('commits', []))} 个")
                    logging.info(f"- 议题: {len(repo_activities.get('issues', []))} 个")
                    logging.info(f"- PR: {len(repo_activities.get('pull_requests', []))} 个")
                    logging.info(f"- 发布: {len(repo_activities.get('releases', []))} 个")
                    
                    if has_commits or has_issues or has_prs or has_releases:
                        logging.info(f"仓库 {repo_full_name} 有更新，获取详细信息...")
                        # 获取仓库详情
                        repo_details = github_tracker.get_repository_details(repo_full_name)
                        
                        # 添加到更新列表
                        updates.append({
                            'repo': repo_details,
                            'activities': repo_activities
                        })
                        logging.info(f"已添加仓库 {repo_full_name} 的更新信息到列表")
                    else:
                        logging.info(f"仓库 {repo_full_name} 没有新的活动")
                else:
                    logging.warning(f"仓库 {repo_full_name} 未获取到活动信息")
            except Exception as e:
                logging.error(f"获取仓库 {repo_full_name} 更新时出错: {str(e)}")
                
        # 如果有更新，发送邮件
        if updates:
            logging.info(f"共有 {len(updates)} 个仓库有更新，准备发送邮件...")
            send_email(email, updates)
            logging.info(f"已向 {email} 发送仓库更新邮件")
        else:
            logging.info(f"没有仓库更新，不发送邮件")
    except Exception as e:
        logging.error(f"执行定时任务时出错: {str(e)}")
        raise

def schedule_task(task: Dict[str, Any]):
    """设置定时任务"""
    try:
        # 对于立即执行的任务，直接执行一次
        if task['frequency'] == 'immediate':
            # 创建一个立即执行一次的任务
            scheduler.add_job(
                send_repo_update_email,
                'date',  # 指定日期触发器
                id=task['id'],
                kwargs={
                    'task': task
                },
                replace_existing=True
            )
            logging.info(f"已添加立即执行任务: {task['id']}")
            return
            
        # 获取执行时间（默认9:00）
        execute_time = task.get('executeTime', '09:00').split(':')
        hour = int(execute_time[0])
        minute = int(execute_time[1])
            
        # 根据频率设置触发器
        if task['frequency'] == 'daily':
            trigger = CronTrigger(hour=hour, minute=minute)  # 每天指定时间
        elif task['frequency'] == 'weekly':
            # 星期几 (1-7，1代表星期一)
            weekday = int(task.get('weekday', '1'))
            trigger = CronTrigger(day_of_week=weekday - 1, hour=hour, minute=minute)  # 每周指定日指定时间
        elif task['frequency'] == 'monthly':
            # 每月几号 (1-31)
            day = int(task.get('monthDay', '1'))
            trigger = CronTrigger(day=day, hour=hour, minute=minute)  # 每月指定日指定时间
        else:
            logging.error(f"未知的任务频率: {task['frequency']}")
            return
            
        # 添加任务到调度器
        scheduler.add_job(
            send_repo_update_email,
            trigger=trigger,
            id=task['id'],
            kwargs={
                'task': task
            },
            replace_existing=True
        )
        
        logging.info(f"已添加定时任务: {task['id']}, 频率: {task['frequency']}, 时间: {hour}:{minute}")
    except Exception as e:
        logging.error(f"设置定时任务时出错: {str(e)}")

async def send_repo_update_email(task: Dict[str, Any]):
    """发送仓库更新邮件"""
    try:
        # 获取任务信息
        email = task['email']
        repositories = task['repositories']
        
        # 收集仓库更新信息
        updates = []
        for repo_full_name in repositories:
            try:
                # 获取仓库活动
                activities = repo_tracker.get_repo_activities(repo_full_name, days=7)  # 获取最近7天活动
                if activities and 'activities' in activities:
                    repo_activities = activities['activities']
                    
                    # 检查是否有更新
                    if repo_activities.get('commits') or repo_activities.get('issues') or repo_activities.get('pull_requests') or repo_activities.get('releases'):
                        # 获取仓库详情
                        repo_details = github_tracker.get_repository_details(repo_full_name)
                        
                        # 添加到更新列表
                        updates.append({
                            'repo': repo_details,
                            'activities': repo_activities
                        })
            except Exception as e:
                logging.error(f"获取仓库 {repo_full_name} 更新时出错: {str(e)}")
                
        # 如果有更新，发送邮件
        if updates:
            send_email(email, updates)
            logging.info(f"已向 {email} 发送仓库更新邮件")
        else:
            logging.info(f"仓库没有更新，不发送邮件")
    except Exception as e:
        logging.error(f"发送仓库更新邮件时出错: {str(e)}")

def send_email(to_email: str, updates: List[Dict[str, Any]]):
    """发送邮件"""
    try:
        # 从环境变量获取邮件配置
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        logging.info("邮件服务器配置信息:")
        logging.info(f"- SMTP服务器: {smtp_server}")
        logging.info(f"- SMTP端口: {smtp_port}")
        logging.info(f"- SMTP用户名: {smtp_username}")
        logging.info(f"- 密码是否已设置: {'是' if smtp_password else '否'}")
        
        if not all([smtp_server, smtp_username, smtp_password]):
            logging.error("邮件服务器配置不完整:")
            if not smtp_server: logging.error("- 缺少 SMTP_SERVER 配置")
            if not smtp_username: logging.error("- 缺少 SMTP_USERNAME 配置")
            if not smtp_password: logging.error("- 缺少 SMTP_PASSWORD 配置")
            return
            
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = 'GitHub 项目更新通知'
        
        logging.info("开始构建邮件内容...")
        
        # 构建邮件内容
        email_body = "<html><body>"
        email_body += "<h2>GitHub 项目更新通知</h2>"
        email_body += f"<p>以下是您关注的项目在最近一周的更新动态：</p>"
        
        for update in updates:
            repo = update['repo']
            activities = update['activities']
            
            logging.info(f"添加仓库 {repo['full_name']} 的更新信息到邮件内容")
            
            email_body += f"<h3>{repo['name']} ({repo['full_name']})</h3>"
            email_body += f"<p>Stars: {repo['stars']}, Forks: {repo['forks']}</p>"
            
            # 提交信息
            if activities.get('commits'):
                email_body += "<h4>最新提交</h4><ul>"
                for commit in activities['commits'][:5]:  # 最多显示5个提交
                    message = commit['message'].split('\n')[0]
                    email_body += f"<li>{message} (作者: {commit['author']})</li>"
                if len(activities['commits']) > 5:
                    email_body += f"<li>... 还有 {len(activities['commits']) - 5} 个提交</li>"
                email_body += "</ul>"
                
            # Issue信息
            if activities.get('issues'):
                email_body += "<h4>最新议题</h4><ul>"
                for issue in activities['issues'][:5]:  # 最多显示5个issue
                    email_body += f"<li>{issue['title']} (状态: {issue['state']})</li>"
                if len(activities['issues']) > 5:
                    email_body += f"<li>... 还有 {len(activities['issues']) - 5} 个议题</li>"
                email_body += "</ul>"
                
            # PR信息
            if activities.get('pull_requests'):
                email_body += "<h4>最新拉取请求</h4><ul>"
                for pr in activities['pull_requests'][:5]:  # 最多显示5个PR
                    email_body += f"<li>{pr['title']} (状态: {pr['state']})</li>"
                if len(activities['pull_requests']) > 5:
                    email_body += f"<li>... 还有 {len(activities['pull_requests']) - 5} 个拉取请求</li>"
                email_body += "</ul>"
                
            # 发布信息
            if activities.get('releases'):
                email_body += "<h4>最新发布</h4><ul>"
                for release in activities['releases'][:5]:  # 最多显示5个release
                    email_body += f"<li>{release['name']} (标签: {release['tag']})</li>"
                if len(activities['releases']) > 5:
                    email_body += f"<li>... 还有 {len(activities['releases']) - 5} 个发布</li>"
                email_body += "</ul>"
                
            # 添加仓库链接
            email_body += f"<p><a href=\"{repo['url']}\">访问仓库</a></p>"
            email_body += "<hr/>"
        
        email_body += "<p>此邮件由 GitHub 项目追踪器自动发送，请勿直接回复。</p>"
        email_body += "</body></html>"
        
        # 添加HTML内容
        msg.attach(MIMEText(email_body, 'html'))
        
        logging.info("邮件内容构建完成，准备发送...")
        
        # 发送邮件
        try:
            logging.info(f"连接到SMTP服务器 {smtp_server}:{smtp_port}...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            logging.info("启用TLS加密...")
            server.ehlo()
            server.starttls()
            server.ehlo()
            logging.info("尝试登录SMTP服务器...")
            server.login(smtp_username, smtp_password)
            logging.info("登录成功，发送邮件...")
            server.send_message(msg)
            logging.info("邮件发送完成，关闭SMTP连接...")
            server.quit()
            logging.info(f"成功发送邮件到 {to_email}")
        except Exception as e:
            logging.error(f"发送邮件时出错: {str(e)}")
            logging.error(f"错误类型: {type(e).__name__}")
            logging.error(f"错误详情: {str(e)}")
            raise
    except Exception as e:
        logging.error(f"准备发送邮件时出错: {str(e)}")
        logging.error(f"错误类型: {type(e).__name__}")
        logging.error(f"错误详情: {str(e)}")
        raise

# 启动时加载已有的定时任务
def load_scheduled_tasks():
    """加载所有定时任务"""
    try:
        config_file = base_dir / "config" / "scheduled_tasks.json"
        if not config_file.exists():
            return
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        tasks = config.get('tasks', [])
        for task in tasks:
            schedule_task(task)
            
        logging.info(f"已加载 {len(tasks)} 个定时任务")
    except Exception as e:
        logging.error(f"加载定时任务时出错: {str(e)}")

# 每天自动获取仓库动态的任务
def scheduled_refresh():
    """每天自动获取仓库动态的任务"""
    print("执行定时任务: 自动获取仓库动态")
    repo_tracker.track_all_repos()

# 在应用启动时加载定时任务
@app.on_event("startup")
def startup_event():
    # 加载已配置的定时任务
    load_scheduled_tasks()
    
    # 添加每天自动刷新仓库的任务
    scheduler.add_job(
        scheduled_refresh,
        CronTrigger(hour=3),  # 每天凌晨3点执行
        id='daily_refresh',
        replace_existing=True
    )
    
    # 启动定时任务调度器
    scheduler.start()

# 应用关闭时关闭定时任务
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)