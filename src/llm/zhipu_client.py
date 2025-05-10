from zhipuai import ZhipuAI
from typing import Dict, Any
from pathlib import Path
from .base_llm import BaseLLM
import os
import logging

class ZhipuLLM(BaseLLM):
    """智谱AI客户端"""
    
    def __init__(self, config_path: Path):
        """
        初始化智谱AI客户端
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.zhipuai_api_key = os.getenv('ZHIPU_API_KEY')
        self.model = self.model_config['zhipu'].get('model', 'chatglm_turbo')
        self.logger = logging.getLogger(__name__)
        
    async def _call_model(self, prompt: str) -> str:
        """
        异步调用智谱AI API
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 模型返回的文本
        """
        try:
            # 创建客户端实例
            client = ZhipuAI(api_key=self.zhipuai_api_key)
            
            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 调用智谱AI的chat API
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                top_p=0.7,
                temperature=0.95,
                max_tokens=1024,
                # tools=[{"type": "web_search", "web_search": {"search_result": True, "search_engine": "search-std"}}],
                stream=False
            )
            
            # 处理响应
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"调用智谱AI模型时出错: {str(e)}")
            raise
            
    def translate(self, text: str, from_lang: str = "en", to_lang: str = "zh") -> str:
        """
        文本翻译
        
        Args:
            text: 要翻译的文本
            from_lang: 源语言
            to_lang: 目标语言
            
        Returns:
            str: 翻译后的文本
        """
        template = self._load_prompt("translate")
        prompt = template.format(
            text=text,
            from_lang=from_lang,
            to_lang=to_lang
        )
        return self._call_model(prompt)
        
    def summarize(self, text: str) -> str:
        """
        文本总结
        
        Args:
            text: 要总结的文本
            
        Returns:
            str: 总结后的文本
        """
        template = self._load_prompt("summarize")
        prompt = template.format(text=text)
        return self._call_model(prompt) 