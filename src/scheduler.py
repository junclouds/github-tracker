import schedule
import time
from .github_tracker import GitHubTracker

class ScheduleManager:
    """定时任务管理器"""
    
    def __init__(self, tracker: GitHubTracker):
        """
        初始化定时任务管理器
        
        Args:
            tracker: GitHub 追踪器实例
        """
        self.tracker = tracker
        
    def setup_schedule(self) -> None:
        """设置定时任务"""
        schedule.every().day.at("08:00").do(self.tracker.save_data)
        schedule.every().day.at("20:00").do(self.tracker.save_data)
        
    def run(self) -> None:
        """运行定时任务"""
        print("GitHub 跟踪器已启动...")
        
        # 立即运行一次
        self.tracker.save_data()
        
        # 保持程序运行
        while True:
            schedule.run_pending()
            time.sleep(60) 