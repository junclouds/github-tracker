# GitHub Tracker

GitHub 项目追踪器，用于监控热门项目和关注项目的最新动态。

## 功能特点

- 自动获取 GitHub 热门项目
  - 支持 Python 和 Java 语言
  - 按照 Star 数量排序
  - 显示项目描述和统计信息
- 项目追踪功能
  - 可以关注感兴趣的项目
  - 自动获取项目最新动态
  - 支持查看提交、Issue、PR 等活动
- 定时更新
  - 每天自动更新热门项目列表
  - 定期获取已追踪项目的最新动态

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- PyGithub
- Schedule

### 前端
- React 18
- TypeScript
- Material-UI
- React Query
- Vite

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/junclouds/github-tracker.git
cd github-tracker
```

2. 设置环境
```bash
# 后端设置
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 前端设置
cd frontend
npm install
```

3. 配置
- 复制 `.env.example` 为 `.env`
- 添加你的 GitHub Token：
```
GITHUB_TOKEN=your_token_here
```

4. 启动服务
```bash
# 启动后端
python run_api.py

# 启动前端（新终端）
cd frontend
npm run dev
```

5. 访问
- 前端界面：http://localhost:5173
- API 文档：http://localhost:8000/docs

## 项目结构

```
github_tracker/
├── frontend/           # 前端项目
│   ├── src/           # 源代码
│   ├── public/        # 静态资源
│   └── package.json   # 依赖配置
├── src/               # 后端源代码
│   ├── github_tracker.py    # GitHub API 交互
│   ├── repo_activity_tracker.py  # 项目活动追踪
│   ├── api_server.py   # FastAPI 服务器
│   └── scheduler.py    # 定时任务
├── config/            # 配置文件
├── data/             # 数据存储
└── requirements.txt   # Python 依赖
```

## 版本历史

- v1.0.0
  - 实现基础功能：热门项目获取和追踪
  - 添加前端界面
  - 支持项目活动监控

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件 