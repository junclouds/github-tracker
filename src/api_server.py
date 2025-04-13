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
from datetime import datetime

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
async def get_tracked_repos() -> List[Dict[str, Any]]:
    """获取已追踪的仓库列表"""
    try:
        # 从配置文件读取追踪的仓库
        config_file = base_dir / "config" / "tracked_repos.json"
        if not config_file.exists():
            return []
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('repositories', [])
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