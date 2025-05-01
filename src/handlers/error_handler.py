from typing import Dict, Any, Optional
import logging
from fastapi import HTTPException

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def handle_github_error(self, error: Exception) -> None:
        """
        处理GitHub API错误
        
        Args:
            error: 异常对象
        
        Raises:
            HTTPException: 转换后的HTTP错误
        """
        self.logger.error(f"GitHub API错误: {str(error)}")
        
        if "rate limit exceeded" in str(error).lower():
            raise HTTPException(
                status_code=429,
                detail="GitHub API速率限制已达到，请稍后再试"
            )
        elif "not found" in str(error).lower():
            raise HTTPException(
                status_code=404,
                detail="请求的资源不存在"
            )
        elif "bad credentials" in str(error).lower():
            raise HTTPException(
                status_code=401,
                detail="GitHub认证失败，请检查Token"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"GitHub API错误: {str(error)}"
            )
            
    def handle_cache_error(self, error: Exception) -> None:
        """
        处理缓存错误
        
        Args:
            error: 异常对象
            
        Raises:
            HTTPException: 转换后的HTTP错误
        """
        self.logger.error(f"缓存错误: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"缓存操作失败: {str(error)}"
        )
        
    def handle_validation_error(self, error: Exception) -> None:
        """
        处理数据验证错误
        
        Args:
            error: 异常对象
            
        Raises:
            HTTPException: 转换后的HTTP错误
        """
        self.logger.error(f"数据验证错误: {str(error)}")
        raise HTTPException(
            status_code=400,
            detail=f"数据验证失败: {str(error)}"
        ) 