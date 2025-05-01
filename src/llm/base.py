from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
from github import Github
from ..utils.rate_limiter import RateLimiter
from ..utils.cache import CacheManager

class BaseGitHubClient:
    """GitHub客户端基类"""
    
    def __init__(self, config_path: Path):
        """
        初始化GitHub客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.github = Github(self.config['github']['token'])
        
        # 初始化速率限制器
        self.rate_limiter = RateLimiter(
            calls=5000,  # GitHub API默认限制
            period=3600  # 1小时
        )
        
        # 初始化缓存管理器
        cache_dir = Path(self.config['storage']['base_dir']) / self.config['storage']['cache_dir']
        self.cache = CacheManager(cache_dir)
        
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置信息
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _make_request(self, cache_key: str, request_func: callable) -> Any:
        """
        执行API请求，包含缓存和速率限制
        
        Args:
            cache_key: 缓存键名
            request_func: 实际执行请求的函数
            
        Returns:
            Any: 请求结果
        """
        # 尝试从缓存获取
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
            
        # 应用速率限制
        self.rate_limiter.wait()
        
        # 执行请求
        result = request_func()
        
        # 缓存结果
        self.cache.set(cache_key, result)
        
        return result 