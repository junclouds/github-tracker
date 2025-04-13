import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from github import Github

class RepoActivityTracker:
    """追踪特定GitHub仓库的活动"""
    
    def __init__(self, token: str, base_dir: Path):
        """
        初始化仓库活动追踪器
        
        Args:
            token: GitHub API 访问令牌
            base_dir: 项目根目录
        """
        self.github = Github(token)
        self.base_dir = base_dir
        self.data_dir = base_dir / "data" / "repo_activities"
        self.config_file = base_dir / "config" / "tracked_repos.json"
        self.tracked_repos = self._load_tracked_repos()
        
    def _load_tracked_repos(self) -> List[Dict[str, str]]:
        """加载要追踪的仓库列表"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('repositories', [])
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_file}")
            return []
        except json.JSONDecodeError:
            print(f"配置文件格式错误: {self.config_file}")
            return []
            
    def get_repo_activities(self, repo_full_name: str, days: int = 7) -> Dict[str, Any]:
        """获取仓库的最新活动"""
        try:
            print(f"\n=== 开始获取 {repo_full_name} 的活动 ===")
            print(f"获取近 {days} 天的活动")
            
            repo = self.github.get_repo(repo_full_name)
            recent_time = datetime.now(timezone.utc) - timedelta(days=days)
            print(f"时间范围: {recent_time.isoformat()} -> {datetime.now(timezone.utc).isoformat()}")
            
            # 获取最近的提交
            print("\n正在获取提交...")
            commits = []
            for commit in repo.get_commits(since=recent_time):
                commit_date = commit.commit.author.date.replace(tzinfo=timezone.utc)
                print(f"找到提交: {commit.sha[:7]} - {commit_date.isoformat()} - {commit.commit.message.splitlines()[0]}")
                if commit_date > recent_time:
                    commits.append({
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": commit.commit.author.name,
                        "date": commit.commit.author.date.isoformat(),
                        "url": commit.html_url
                    })
            print(f"共获取到 {len(commits)} 个提交")
            
            # 获取最近的发布
            print("\n正在获取发布...")
            releases = []
            for release in repo.get_releases():
                if release.published_at:
                    print(f"找到发布: {release.tag_name} - {release.published_at.isoformat()}")
                    if release.published_at > recent_time:
                        releases.append({
                            "tag": release.tag_name,
                            "name": release.title,
                            "body": release.body,
                            "date": release.published_at.isoformat(),
                            "url": release.html_url
                        })
            print(f"共获取到 {len(releases)} 个发布")
            
            # 获取最近的议题
            print("\n正在获取议题...")
            issues = []
            for issue in repo.get_issues(state='all', since=recent_time):
                print(f"找到议题: #{issue.number} - 更新于 {issue.updated_at.isoformat()} - {issue.title}")
                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "url": issue.html_url
                })
            print(f"共获取到 {len(issues)} 个议题")
            
            # 获取最近的 PR
            print("\n正在获取 PR...")
            pull_requests = []
            for pr in repo.get_pulls(state='all', sort='updated', direction='desc'):
                if pr.updated_at > recent_time:
                    print(f"找到 PR: #{pr.number} - 更新于 {pr.updated_at.isoformat()} - {pr.title}")
                    pull_requests.append({
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "created_at": pr.created_at.isoformat(),
                        "updated_at": pr.updated_at.isoformat(),
                        "url": pr.html_url
                    })
                else:
                    print(f"PR #{pr.number} 更新时间 {pr.updated_at.isoformat()} 超出范围，停止获取")
                    break
            print(f"共获取到 {len(pull_requests)} 个 PR")
            
            result = {
                "repository": repo_full_name,
                "timestamp": datetime.now().isoformat(),
                "activities": {
                    "commits": commits,
                    "releases": releases,
                    "issues": issues,
                    "pull_requests": pull_requests,
                    "stats": {
                        "commit_count": len(commits),
                        "release_count": len(releases),
                        "issue_count": len(issues),
                        "pr_count": len(pull_requests)
                    }
                }
            }
            
            print("\n=== 活动获取完成 ===")
            print(f"总计: {len(commits)} 提交, {len(releases)} 发布, {len(issues)} 议题, {len(pull_requests)} PR")
            return result
            
        except Exception as e:
            print(f"\n获取仓库 {repo_full_name} 活动时出错: {str(e)}")
            return {}
            
    def save_activities(self, activities: Dict[str, Any]) -> Optional[Path]:
        """保存仓库活动数据"""
        try:
            if not activities:
                return None
                
            # 确保目录存在
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用仓库名和时间戳创建文件名
            repo_name = activities['repository'].replace('/', '_')
            filename = self.data_dir / f"{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(activities, f, ensure_ascii=False, indent=2)
                
            return filename
        except Exception as e:
            print(f"保存活动数据时出错: {str(e)}")
            return None
            
    def display_activities(self, activities: Dict[str, Any]) -> None:
        """显示仓库活动摘要"""
        if not activities:
            print("没有活动数据")
            return
            
        print(f"\n=== {activities['repository']} 活动摘要 ===")
        print(f"统计时间: {activities['timestamp']}")
        
        stats = activities['activities']['stats']
        print(f"\n活动统计:")
        print(f"- 提交数: {stats['commit_count']}")
        print(f"- 发布数: {stats['release_count']}")
        print(f"- 议题数: {stats['issue_count']}")
        print(f"- PR数: {stats['pr_count']}")
        
        if activities['activities']['commits']:
            print("\n最新提交:")
            for commit in activities['activities']['commits'][:5]:  # 显示前5条
                print(f"- {commit['message'].splitlines()[0]}")
                print(f"  作者: {commit['author']}, 时间: {commit['date']}")
                
        if activities['activities']['releases']:
            print("\n最新发布:")
            for release in activities['activities']['releases']:
                print(f"- {release['name']} ({release['tag']})")
                print(f"  发布时间: {release['date']}")
                
        if activities['activities']['issues']:
            print("\n最新议题:")
            for issue in activities['activities']['issues'][:5]:  # 显示前5条
                print(f"- #{issue['number']} {issue['title']}")
                print(f"  状态: {issue['state']}, 更新时间: {issue['updated_at']}")
                
        if activities['activities']['pull_requests']:
            print("\nPR活动:")
            for pr in activities['activities']['pull_requests'][:5]:  # 显示前5条
                print(f"- #{pr['number']} {pr['title']}")
                print(f"  状态: {pr['state']}, 更新时间: {pr['updated_at']}")
                
    def track_all_repos(self, days: int = 7) -> None:
        """追踪所有配置的仓库
        
        Args:
            days: 获取最近几天的活动，默认为 7 天
        """
        if not self.tracked_repos:
            print("没有配置要追踪的仓库")
            return
            
        for repo in self.tracked_repos:
            print(f"\n正在获取 {repo['full_name']} 的活动...")
            activities = self.get_repo_activities(repo['full_name'], days)
            
            if activities:
                filename = self.save_activities(activities)
                if filename:
                    print(f"活动数据已保存到: {filename}")
                    self.display_activities(activities)
            else:
                print(f"未能获取 {repo['full_name']} 的活动数据")
                
    @classmethod
    def main(cls):
        """主方法，用于直接运行该类"""
        from dotenv import load_dotenv
        import os
        
        print("正在启动仓库活动追踪器...")
        
        # 加载环境变量
        load_dotenv()
        
        # 获取 GitHub token
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("错误: 未设置 GITHUB_TOKEN 环境变量")
            print("请在 .env 文件中添加你的 GitHub Token")
            return
            
        # 获取当前文件所在目录的父目录作为项目根目录
        base_dir = Path(__file__).parent.parent
        
        # 创建追踪器实例
        tracker = cls(token, base_dir)
        
        # 追踪所有配置的仓库
        tracker.track_all_repos()

if __name__ == "__main__":
    RepoActivityTracker.main()