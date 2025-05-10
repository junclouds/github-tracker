import logging
from typing import Dict, Any, List
from pathlib import Path
from .zhipu_client import ZhipuLLM

class SummaryService:
    """AI总结服务类"""
    
    def __init__(self, config_path: Path):
        """初始化AI总结服务
        
        Args:
            config_path: 模型配置文件路径
        """
        self.llm = ZhipuLLM(config_path)
        self.logger = logging.getLogger(__name__)
        
    async def generate_hot_repos_summary(self, repos: List[Dict[str, Any]]) -> str:
        """生成热门仓库总结
        
        Args:
            repos: 热门仓库列表
            
        Returns:
            str: 总结内容
        """
        try:
            # 准备用于总结的内容
            summary_content = ""
            for repo in repos:
                summary_content += f"项目名称: {repo['name']}\n"
                summary_content += f"描述: {repo['description']}\n"
                summary_content += f"Stars: {repo['stars']}, Forks: {repo['forks']}\n"
                summary_content += f"最近更新: {repo['updated_at']}\n\n"
                
            prompt = f"""请分析以下GitHub热门项目列表，生成一个简洁的总结报告。重点关注：
1. 项目的主要类型和领域分布
2. 最受关注的项目及其特点
3. 当前技术趋势分析

项目列表：
{summary_content}

请用中文生成总结报告。
"""
            return await self.llm._call_model(prompt)
            
        except Exception as e:
            self.logger.error(f"生成热门仓库总结时出错: {str(e)}")
            return "生成总结时出错，请稍后重试。"
            
    async def generate_tracked_repos_summary(self, repos: List[Dict[str, Any]]) -> str:
        """生成已追踪仓库总结
        
        Args:
            repos: 已追踪仓库列表
            
        Returns:
            str: 总结内容
        """
        try:
            # 准备用于总结的内容
            summary_content = ""
            for repo in repos:
                summary_content += f"项目名称: {repo['full_name']}\n"
                if repo['has_updates']:
                    summary_content += "最新活动:\n"
                    for activity in repo['activities'][:5]:  # 只取最新的5条活动
                        summary_content += f"- [{activity['type']}] {activity['title']}\n"
                        if activity.get('description'):
                            summary_content += f"  {activity['description']}\n"
                summary_content += "\n"
                
            prompt = f"""请分析以下GitHub已跟踪项目的更新情况，生成一个简洁的总结报告。重点关注：
1. 最活跃的项目及其主要更新内容
2. 重要的版本发布、重大更新
3. 值得关注的问题和PR

更新列表：
{summary_content}

请用中文生成总结报告。
"""
            return await self.llm._call_model(prompt)
            
        except Exception as e:
            self.logger.error(f"生成已追踪仓库总结时出错: {str(e)}")
            return "生成总结时出错，请稍后重试。" 