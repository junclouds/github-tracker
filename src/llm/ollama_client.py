import aiohttp
import logging
from typing import Dict, Any
from pathlib import Path
from .base_llm import BaseLLM

class OllamaAI(BaseLLM):
    """Ollama客户端"""
    
    def __init__(self, config_path: Path):
        """
        初始化Ollama客户端
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.base_url = self.model_config['ollama'].get('base_url', 'http://localhost:11434')
        self.model = self.model_config['ollama'].get('model', 'llama2')
        self.logger = logging.getLogger(__name__)
        
    async def _call_model(self, prompt: str) -> str:
        """
        异步调用Ollama API
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 模型返回的文本
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['response']
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API调用失败: {error_text}")
        except Exception as e:
            self.logger.error(f"调用Ollama模型时出错: {str(e)}")
            raise 