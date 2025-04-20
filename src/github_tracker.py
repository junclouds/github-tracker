import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from github import Github
from pathlib import Path
from dotenv import load_dotenv
import requests
import logging

class GitHubTracker:
    """GitHub 数据追踪器"""
    
    def __init__(self, token: str, base_dir: Path):
        """
        初始化 GitHub 追踪器
        
        Args:
            token: GitHub API 访问令牌
            base_dir: 项目根目录
        """
        self.github = Github(token)
        self.github_token = token  # 保存token
        self.languages = ["python", "java"]
        self.base_dir = base_dir
        self.data_dir = base_dir / "data"
        
    def get_trending_repositories(self) -> List[Dict[str, Any]]:
        """获取热门仓库"""
        try:
            trending_repos = []
            
            for language in self.languages:
                # 搜索过去一周内创建的，按照星标数排序的特定语言仓库
                created_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                query = f"language:{language} created:>{created_date}"
                repos = self.github.search_repositories(query=query, sort="stars", order="desc")
                
                # 获取每种语言的前5个仓库
                count = 0
                for repo in repos:
                    if count >= 5:  # 每种语言取前5个，总共10个
                        break
                        
                    repo_data = {
                        "name": repo.full_name,
                        "description": repo.description,
                        "stars": repo.stargazers_count,
                        "url": repo.html_url,
                        "language": repo.language
                    }
                    trending_repos.append(repo_data)
                    count += 1
                    
            return trending_repos
        except Exception as e:
            print(f"获取热门仓库时出错: {str(e)}")
            return []
            
    def save_data(self) -> None:
        """保存数据到文件"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "trending_repositories": {
                    "description": "Top 5 trending Python and Java projects created in the last week",
                    "data": [{
                        "name": repo["name"],
                        "description": repo["description"],
                        "stars": repo["stars"],
                        "url": repo["url"],
                        "language": repo["language"]
                    } for repo in self.get_trending_repositories()]
                }
            }
            
            # 确保data目录存在
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 使用当前时间戳作为文件名
            filename = self.data_dir / f"github_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"数据已保存到: {filename}")
            return filename  # 返回保存的文件名，方便查看结果
        except Exception as e:
            print(f"保存数据时出错: {str(e)}")
            return None

    @staticmethod
    def display_data(filename: Path) -> None:
        """显示保存的数据内容"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("\n=== GitHub Trending Repositories ===")
            print(f"Timestamp: {data['timestamp']}")
            print(f"\n{data['trending_repositories']['description']}\n")
            
            # 按语言分组显示
            repos_by_language = {}
            for repo in data['trending_repositories']['data']:
                lang = repo['language']
                if lang not in repos_by_language:
                    repos_by_language[lang] = []
                repos_by_language[lang].append(repo)
            
            # 显示每种语言的仓库
            for language, repos in repos_by_language.items():
                print(f"\n=== {language} Projects ===")
                for repo in repos:
                    print(f"\n- {repo['name']}")
                    print(f"  Description: {repo['description']}")
                    print(f"  Stars: {repo['stars']}")
                    print(f"  URL: {repo['url']}")
                
        except Exception as e:
            print(f"显示数据时出错: {str(e)}")

    def search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索GitHub仓库
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            # 构建搜索URL
            search_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
            
            # 发送请求
            response = requests.get(
                search_url,
                headers={"Authorization": f"token {self.github_token}"}  # 使用保存的token
            )
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            repos = []
            
            for item in data.get("items", [])[:10]:  # 限制返回前10个结果
                repos.append({
                    "name": item["full_name"],
                    "description": item.get("description", ""),
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "updated_at": item.get("updated_at"),
                    "url": item["html_url"]
                })
            
            return repos
        except Exception as e:
            logging.error(f"搜索GitHub仓库时出错: {str(e)}")
            raise

    @classmethod
    def main(cls):
        """主方法，用于直接运行该类"""
        print("正在启动 GitHub 热门项目追踪器...")
        
        # 加载环境变量
        load_dotenv()
        
        # 获取 GitHub token
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("错误: 未设置 GITHUB_TOKEN 环境变量")
            print("请在 .env 文件中添加你的 GitHub Token")
            return
        
        # 获取当前文件所在目录的父目录作为项目根目录
        base_dir = Path(__file__).parent.parent
        
        # 创建追踪器实例
        tracker = cls(token, base_dir)
        
        print("正在获取 GitHub 热门项目数据...")
        # 保存数据并获取文件名
        filename = tracker.save_data()
        
        if filename:
            print("\n数据获取完成！正在显示结果：")
            # 显示保存的数据
            tracker.display_data(filename)
        else:
            print("数据获取失败！")

if __name__ == "__main__":
    GitHubTracker.main() 