import os
from pathlib import Path
from dotenv import load_dotenv
from src.github_tracker import GitHubTracker
from src.scheduler import ScheduleManager

def main():
    """主函数"""
    # 获取项目根目录
    base_dir = Path(__file__).parent

    # 加载环境变量
    load_dotenv(base_dir / '.env')
    
    # 获取 GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("请设置 GITHUB_TOKEN 环境变量")
        
    # 创建 GitHub 追踪器
    tracker = GitHubTracker(token, base_dir)
    
    # 创建并运行定时任务管理器
    scheduler = ScheduleManager(tracker)
    scheduler.setup_schedule()
    scheduler.run()

if __name__ == "__main__":
    main() 