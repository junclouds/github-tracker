import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

class MailService:
    """邮件服务类"""
    
    def __init__(self):
        """初始化邮件服务"""
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self) -> bool:
        """验证邮件配置是否完整"""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            self.logger.error("邮件服务器配置不完整:")
            if not self.smtp_server: self.logger.error("- 缺少 SMTP_SERVER 配置")
            if not self.smtp_username: self.logger.error("- 缺少 SMTP_USERNAME 配置")
            if not self.smtp_password: self.logger.error("- 缺少 SMTP_PASSWORD 配置")
            return False
        return True
        
    def send_repo_updates(self, to_email: str, updates: List[Dict[str, Any]]) -> None:
        """发送仓库更新邮件
        
        Args:
            to_email: 接收者邮箱
            updates: 仓库更新信息列表
        """
        if not self.validate_config():
            return
            
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = 'GitHub 项目更新通知'
            
            # 构建邮件内容
            email_body = self._build_update_email_body(updates)
            msg.attach(MIMEText(email_body, 'html'))
            
            # 发送邮件
            self._send_email(msg)
            self.logger.info(f"成功发送邮件到 {to_email}")
            
        except Exception as e:
            self.logger.error(f"发送邮件时出错: {str(e)}")
            self.logger.error(f"错误类型: {type(e).__name__}")
            self.logger.error(f"错误详情: {str(e)}")
            raise
            
    def send_daily_summary(self, to_email: str, hot_repos_summary: str, tracked_repos_summary: str) -> None:
        """发送每日总结邮件
        
        Args:
            to_email: 接收者邮箱
            hot_repos_summary: 热门项目总结
            tracked_repos_summary: 已追踪项目总结
        """
        if not self.validate_config():
            return
            
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = 'GitHub 项目每日总结'
            
            # 构建邮件内容
            email_body = "<html><body>"
            email_body += "<h2>GitHub 项目每日总结</h2>"
            
            email_body += "<h3>热门项目总结</h3>"
            email_body += f"<p>{hot_repos_summary}</p>"
            
            email_body += "<h3>已追踪项目更新总结</h3>"
            email_body += f"<p>{tracked_repos_summary}</p>"
            
            email_body += "</body></html>"
            
            msg.attach(MIMEText(email_body, 'html'))
            
            # 发送邮件
            self._send_email(msg)
            self.logger.info(f"成功发送每日总结邮件到 {to_email}")
            
        except Exception as e:
            self.logger.error(f"发送每日总结邮件时出错: {str(e)}")
            raise
            
    def _build_update_email_body(self, updates: List[Dict[str, Any]]) -> str:
        """构建更新邮件内容
        
        Args:
            updates: 仓库更新信息列表
            
        Returns:
            str: HTML格式的邮件内容
        """
        email_body = "<html><body>"
        email_body += "<h2>GitHub 项目更新通知</h2>"
        email_body += f"<p>以下是您关注的项目在最近一周的更新动态：</p>"
        
        for update in updates:
            repo = update['repo']
            activities = update['activities']
            
            self.logger.info(f"添加仓库 {repo['full_name']} 的更新信息到邮件内容")
            
            email_body += f"<h3>{repo['name']} ({repo['full_name']})</h3>"
            email_body += f"<p>Stars: {repo['stars']}, Forks: {repo['forks']}</p>"
            
            # 提交信息
            if activities.get('commits'):
                email_body += "<h4>最新提交</h4><ul>"
                for commit in activities['commits'][:5]:
                    message = commit['message'].split('\n')[0]
                    email_body += f"<li>{message} (作者: {commit['author']})</li>"
                if len(activities['commits']) > 5:
                    email_body += f"<li>... 还有 {len(activities['commits']) - 5} 个提交</li>"
                email_body += "</ul>"
                
            # Issue信息
            if activities.get('issues'):
                email_body += "<h4>最新议题</h4><ul>"
                for issue in activities['issues'][:5]:
                    email_body += f"<li>{issue['title']} (状态: {issue['state']})</li>"
                if len(activities['issues']) > 5:
                    email_body += f"<li>... 还有 {len(activities['issues']) - 5} 个议题</li>"
                email_body += "</ul>"
                
            # PR信息
            if activities.get('pull_requests'):
                email_body += "<h4>最新拉取请求</h4><ul>"
                for pr in activities['pull_requests'][:5]:
                    email_body += f"<li>{pr['title']} (状态: {pr['state']})</li>"
                if len(activities['pull_requests']) > 5:
                    email_body += f"<li>... 还有 {len(activities['pull_requests']) - 5} 个拉取请求</li>"
                email_body += "</ul>"
                
            # 发布信息
            if activities.get('releases'):
                email_body += "<h4>最新发布</h4><ul>"
                for release in activities['releases'][:5]:
                    email_body += f"<li>{release['name']} (标签: {release['tag']})</li>"
                if len(activities['releases']) > 5:
                    email_body += f"<li>... 还有 {len(activities['releases']) - 5} 个发布</li>"
                email_body += "</ul>"
                
            # 添加仓库链接
            email_body += f"<p><a href=\"{repo['url']}\">访问仓库</a></p>"
            email_body += "<hr/>"
            
        email_body += "<p>此邮件由 GitHub 项目追踪器自动发送，请勿直接回复。</p>"
        email_body += "</body></html>"
        
        return email_body
        
    def _send_email(self, msg: MIMEMultipart) -> None:
        """发送邮件
        
        Args:
            msg: 邮件消息对象
        """
        try:
            self.logger.info(f"连接到SMTP服务器 {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.logger.info("启用TLS加密...")
            server.ehlo()
            server.starttls()
            server.ehlo()
            self.logger.info("尝试登录SMTP服务器...")
            server.login(self.smtp_username, self.smtp_password)
            self.logger.info("登录成功，发送邮件...")
            server.send_message(msg)
            self.logger.info("邮件发送完成，关闭SMTP连接...")
            server.quit()
        except Exception as e:
            self.logger.error(f"发送邮件时出错: {str(e)}")
            raise 