import requests
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
        
    def _call_model(self, prompt: str) -> str:
        """
        调用Ollama API
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 模型返回的文本
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Ollama API调用失败: {response.text}") 