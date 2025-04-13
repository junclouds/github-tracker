import schedule
import time
from pathlib import Path
from .github_tracker import GitHubTracker
from .repo_activity_tracker import RepoActivityTracker

class ScheduleManager:
    """定时任务管理器"""
    
    def __init__(self, github_token: str, base_dir: Path):
        """
        初始化定时任务管理器
        
        Args:
            github_token: GitHub API 访问令牌
            base_dir: 项目根目录
        """
        self.github_token = github_token
        self.base_dir = base_dir
        self.tracker = GitHubTracker(github_token, base_dir)
        self.activity_tracker = RepoActivityTracker(github_token, base_dir)
        
    def run_all_tasks(self) -> None:
        """运行所有追踪任务"""
        print("\n=== 运行热门仓库追踪 ===")
        self.tracker.save_data()
        
        print("\n=== 运行仓库活动追踪 ===")
        self.activity_tracker.track_all_repos()
        
    def setup_schedule(self) -> None:
        """设置定时任务"""
        # 每天早8点和晚8点运行热门仓库追踪
        schedule.every().day.at("08:00").do(self.tracker.save_data)
        schedule.every().day.at("20:00").do(self.tracker.save_data)
        
        # 每天早9点和晚9点运行仓库活动追踪
        schedule.every().day.at("09:00").do(self.activity_tracker.track_all_repos)
        schedule.every().day.at("21:00").do(self.activity_tracker.track_all_repos)
        
    def run(self) -> None:
        """运行定时任务"""
        print("GitHub 追踪器已启动...")
        
        # 立即运行一次
        self.run_all_tasks()
        
        # 保持程序运行
        while True:
            schedule.run_pending()
            time.sleep(60) 