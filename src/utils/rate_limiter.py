import time
from typing import Optional, Dict
from datetime import datetime, timedelta

class RateLimiter:
    """API请求速率限制器"""
    
    def __init__(self, calls: int, period: int):
        """
        初始化速率限制器
        
        Args:
            calls: 在指定时间段内允许的最大调用次数
            period: 时间段（秒）
        """
        self.calls = calls
        self.period = period
        self.timestamps = []
        
    def wait(self) -> None:
        """
        在必要时等待以遵守速率限制
        """
        now = time.time()
        
        # 移除过期的时间戳
        self.timestamps = [ts for ts in self.timestamps if ts > now - self.period]
        
        if len(self.timestamps) >= self.calls:
            # 计算需要等待的时间
            wait_time = self.timestamps[0] - (now - self.period)
            if wait_time > 0:
                time.sleep(wait_time)
            # 移除最早的时间戳
            self.timestamps.pop(0)
            
        self.timestamps.append(now) 