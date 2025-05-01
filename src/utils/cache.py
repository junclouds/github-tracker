import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional
from pathlib import Path

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Path, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            ttl: 缓存有效期（秒），默认1小时
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.json"
        
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 检查是否过期
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > timedelta(seconds=self.ttl):
                self.delete(key)
                return None
                
            return data['value']
        except Exception:
            return None
            
    def set(self, key: str, value: Any) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键名
            value: 要缓存的数据
        """
        cache_path = self._get_cache_path(key)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def delete(self, key: str) -> None:
        """
        删除缓存数据
        
        Args:
            key: 缓存键名
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            os.remove(cache_path)
            
    def clear(self) -> None:
        """清除所有缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            os.remove(cache_file) 