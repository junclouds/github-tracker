from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import yaml

class BaseLLM(ABC):
    """LLM基类"""
    
    def __init__(self, config_path: Path):
        """
        初始化LLM客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.model_config = self.config.get('llm', {})
        self.prompt_dir = Path(__file__).parent.parent / 'prompt_engineering'
        
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _load_prompt(self, template_name: str) -> str:
        """加载提示词模板"""
        template_path = self.prompt_dir / f"{template_name}.txt"
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
            
    @abstractmethod
    def _call_model(self, prompt: str) -> str:
        """
        调用模型API
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 模型返回的文本
        """
        pass
            
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
        if not text:
            return ""
            
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
        if not text:
            return ""
            
        template = self._load_prompt("summarize")
        prompt = template.format(text=text)
        return self._call_model(prompt)
        
    def batch_translate(self, items: List[Tuple[str, str]], from_lang: str = "en", to_lang: str = "zh") -> List[Tuple[str, str]]:
        """
        批量翻译文本
        
        Args:
            items: 要翻译的文本列表，每个元素是(name, description)元组
            from_lang: 源语言
            to_lang: 目标语言
            
        Returns:
            List[Tuple[str, str]]: 翻译后的文本列表，每个元素是(translated_name, translated_description)元组
        """
        if not items:
            return []
            
        # 构建批量翻译的提示词
        texts = []
        for i, (name, desc) in enumerate(items, 1):
            if name:
                texts.append(f"项目{i}名称: {name}")
            if desc:
                texts.append(f"项目{i}描述: {desc}")
                
        if not texts:
            return [(None, None)] * len(items)
            
        template = self._load_prompt("translate")
        prompt = template.format(
            text="\n".join(texts),
            from_lang=from_lang,
            to_lang=to_lang
        )
        
        # 调用模型获取翻译结果
        response = self._call_model(prompt)
        
        # 解析翻译结果
        translations = []
        current_item = {"name": None, "desc": None}
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("项目") and "名称:" in line:
                if current_item["name"] is not None:
                    translations.append((current_item["name"], current_item["desc"]))
                    current_item = {"name": None, "desc": None}
                current_item["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("项目") and "描述:" in line:
                current_item["desc"] = line.split(":", 1)[1].strip()
                
        if current_item["name"] is not None or current_item["desc"] is not None:
            translations.append((current_item["name"], current_item["desc"]))
            
        # 确保返回结果数量与输入一致
        while len(translations) < len(items):
            translations.append((None, None))
            
        return translations[:len(items)] 