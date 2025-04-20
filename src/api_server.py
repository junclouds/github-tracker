from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv
from .github_tracker import GitHubTracker
from .repo_activity_tracker import RepoActivityTracker
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import parser
from .date_handler import DateHandler
import logging 

# 配置日志
logging.basicConfig(level=logging.INFO)

# 加载环境变量
load_dotenv()

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

if not github_token:
    raise ValueError("请设置 GITHUB_TOKEN 环境变量")

# 初始化追踪器
github_tracker = GitHubTracker(github_token, base_dir)
repo_tracker = RepoActivityTracker(github_token, base_dir)

class RepoTrackRequest(BaseModel):
    repo_full_name: str

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
                "stars": repo["stars"],
                "forks": 0,  # 需要从 API 获取
                "updated_at": datetime.now().isoformat(),  # 临时使用当前时间
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
            # 查找该仓库的最新活动文件
            repo_files = list(activity_dir.glob(f"{repo_full_name.replace('/', '_')}*.json"))
            repo_files.sort(reverse=True)  # 最新的文件排在前面
            
            repo_data = {
                "full_name": repo_full_name,  # 仓库的完整名称
                "name": repo_full_name.split("/")[-1],  # 仓库名称
                "description": "",  # 仓库描述
                "stars": 0,  # 星标数量
                "forks": 0,  # Fork 数量
                "updated_at": "",  # 最后更新时间
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

# 添加定时任务
scheduler = BackgroundScheduler()

# 每天凌晨3点自动获取仓库动态
@scheduler.scheduled_job(CronTrigger(hour=3))
def scheduled_refresh():
    print("执行定时任务: 自动获取仓库动态")
    repo_tracker.track_all_repos()

# 启动定时任务
scheduler.start()

# 应用关闭时关闭定时任务
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()