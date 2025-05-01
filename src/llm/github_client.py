from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from .base import BaseGitHubClient
from .base_llm import BaseLLM

class GitHubClient(BaseGitHubClient):
    """GitHub客户端"""
    
    def __init__(self, config_path: Path, llm: BaseLLM):
        """
        初始化GitHub客户端
        
        Args:
            config_path: 配置文件路径
            llm: LLM实例
        """
        super().__init__(config_path)
        self.llm = llm
        
    def get_repos_with_translation(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量获取仓库信息的翻译
        
        Args:
            repos: 仓库信息列表
            
        Returns:
            List[Dict[str, Any]]: 包含翻译的仓库信息列表
        """
        # 准备需要翻译的文本
        items_to_translate = [(repo.get('name', ''), repo.get('description', '')) for repo in repos]
        
        # 批量翻译
        translations = self.llm.batch_translate(items_to_translate)
        
        # 更新仓库信息
        translated_repos = []
        for repo, (name_zh, desc_zh) in zip(repos, translations):
            repo_copy = repo.copy()
            if name_zh:
                repo_copy['name_zh'] = name_zh
            if desc_zh:
                repo_copy['description_zh'] = desc_zh
            translated_repos.append(repo_copy)
            
        return translated_repos
        
    def search_repos(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        搜索仓库
        
        Args:
            query: 搜索关键词
            **kwargs: 其他搜索参数
            
        Returns:
            List[Dict[str, Any]]: 仓库列表
        """
        def _search():
            repos = []
            for repo in self.github.search_repositories(query, **kwargs):
                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "updated_at": repo.updated_at.isoformat(),
                    "url": repo.html_url
                })
            return self.get_repos_with_translation(repos)
            
        return self._make_request(f"search_{query}", _search)
        
    def get_tracked_repos(self, repo_names: List[str]) -> List[Dict[str, Any]]:
        """
        获取已追踪的仓库列表
        
        Args:
            repo_names: 仓库名称列表
            
        Returns:
            List[Dict[str, Any]]: 仓库列表
        """
        def _get_repos():
            repos = []
            for name in repo_names:
                repo = self.github.get_repo(name)
                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "updated_at": repo.updated_at.isoformat(),
                    "url": repo.html_url
                })
            return self.get_repos_with_translation(repos)
            
        return self._make_request(f"tracked_repos_{','.join(repo_names)}", _get_repos)
        
    def get_repo_activities_with_translation(self, repo_name: str, days: int = 7) -> Dict[str, Any]:
        """
        获取仓库活动，包含中文翻译和总结
        
        Args:
            repo_name: 仓库全名
            days: 获取最近几天的活动
            
        Returns:
            Dict[str, Any]: 活动信息
        """
        def _get_activities():
            repo = self.github.get_repo(repo_name)
            activities = {
                "timestamp": datetime.now().isoformat(),
                "activities": {
                    "commits": [],
                    "issues": [],
                    "pull_requests": [],
                    "releases": []
                },
                "summary": ""
            }
            
            # 获取提交
            commits_to_translate = []
            for commit in repo.get_commits(since=datetime.now() - timedelta(days=days)):
                commits_to_translate.append((
                    commit.commit.message,
                    ""  # 提交信息不需要描述
                ))
            
            # 批量翻译提交信息
            commit_translations = self.llm.batch_translate(commits_to_translate)
            
            for commit, (message_zh, _) in zip(repo.get_commits(since=datetime.now() - timedelta(days=days)), commit_translations):
                commit_data = {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "message_zh": message_zh,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "url": commit.html_url
                }
                activities["activities"]["commits"].append(commit_data)
                
            # 获取议题
            issues_to_translate = []
            for issue in repo.get_issues(state='all', since=datetime.now() - timedelta(days=days)):
                issues_to_translate.append((
                    issue.title,
                    issue.body or ""
                ))
            
            # 批量翻译议题
            issue_translations = self.llm.batch_translate(issues_to_translate)
            
            for issue, (title_zh, body_zh) in zip(repo.get_issues(state='all', since=datetime.now() - timedelta(days=days)), issue_translations):
                issue_data = {
                    "number": issue.number,
                    "title": issue.title,
                    "title_zh": title_zh,
                    "body": issue.body,
                    "body_zh": body_zh,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "url": issue.html_url
                }
                activities["activities"]["issues"].append(issue_data)
                
            # 获取PR
            prs_to_translate = []
            for pr in repo.get_pulls(state='all', sort='updated', direction='desc'):
                if pr.updated_at < datetime.now() - timedelta(days=days):
                    break
                prs_to_translate.append((
                    pr.title,
                    pr.body or ""
                ))
            
            # 批量翻译PR
            pr_translations = self.llm.batch_translate(prs_to_translate)
            
            for pr, (title_zh, body_zh) in zip(repo.get_pulls(state='all', sort='updated', direction='desc'), pr_translations):
                if pr.updated_at < datetime.now() - timedelta(days=days):
                    break
                pr_data = {
                    "number": pr.number,
                    "title": pr.title,
                    "title_zh": title_zh,
                    "body": pr.body,
                    "body_zh": body_zh,
                    "state": pr.state,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "url": pr.html_url
                }
                activities["activities"]["pull_requests"].append(pr_data)
                
            # 获取发布
            releases_to_translate = []
            for release in repo.get_releases():
                if release.created_at < datetime.now() - timedelta(days=days):
                    break
                releases_to_translate.append((
                    release.title,
                    release.body or ""
                ))
            
            # 批量翻译发布
            release_translations = self.llm.batch_translate(releases_to_translate)
            
            for release, (title_zh, body_zh) in zip(repo.get_releases(), release_translations):
                if release.created_at < datetime.now() - timedelta(days=days):
                    break
                release_data = {
                    "tag": release.tag_name,
                    "name": release.title,
                    "name_zh": title_zh,
                    "body": release.body,
                    "body_zh": body_zh,
                    "date": release.created_at.isoformat(),
                    "url": release.html_url
                }
                activities["activities"]["releases"].append(release_data)
                
            # 生成总结
            activities_text = f"""
            最近{days}天的更新：
            
            提交：{len(activities['activities']['commits'])}个
            议题：{len(activities['activities']['issues'])}个
            PR：{len(activities['activities']['pull_requests'])}个
            发布：{len(activities['activities']['releases'])}个
            
            主要更新内容：
            
            1. 提交：
            {chr(10).join(f'- {c["message"]}' for c in activities['activities']['commits'][:5])}
            
            2. 议题：
            {chr(10).join(f'- {i["title"]}' for i in activities['activities']['issues'][:5])}
            
            3. PR：
            {chr(10).join(f'- {p["title"]}' for p in activities['activities']['pull_requests'][:5])}
            
            4. 发布：
            {chr(10).join(f'- {r["name"]}' for r in activities['activities']['releases'][:5])}
            """
            
            activities["summary"] = self.llm.summarize(activities_text)
            
            return activities
            
        return self._make_request(f"activities_{repo_name}_{days}", _get_activities) 