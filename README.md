# GitHub Tracker

> 🚀 **GitHub Tracker** —— 帮助你实时追踪最热门与最关心的开源项目，掌握开源动态，紧跟技术趋势。

---

## 🧭 项目定位

GitHub Tracker 是一个 GitHub 项目监控工具，支持查看热门项目、关注感兴趣的项目并追踪其更新动态（提交、Issue、PR 等）。适合开发者、开源爱好者、技术观察者使用。

---

## 🎯 功能特性

### 🔥 热门项目浏览
- 支持语言：Python、Java
- 基于 Star 数量排序
- 可按时间/语言/关键词筛选
- 显示项目描述与核心指标（Star、Fork 等）

### 🌟 项目追踪
- 支持搜索并关注任意 GitHub 项目
- 自动拉取项目的最新活动（提交、Issue、PR）
- 支持跳转查看项目详情

### ⏱ 定时更新
- 每日自动刷新热门项目榜单
- 定期更新已关注项目的动态信息

---

## 👥 适用人群

- 开源技术爱好者
- 想快速发现优质项目的开发者
- 参与二次开发、寻找灵感的工程师
- 技术媒体或竞品追踪分析者

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/junclouds/github-tracker.git
cd github-tracker
```

### 2. 安装依赖

#### ✅ 后端设置
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

#### ✅ 前端设置
```bash
cd frontend
npm install
```

### 3. 配置环境变量

- 复制 `.env.example` 为 `.env`
- 添加你的 GitHub Token（用于 API 授权）
- 获取方法见：[GitHub 官方文档](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

```env
GITHUB_TOKEN=your_token_here
```

### 4. 启动服务

#### 启动后端
```bash
python run_api.py
```

#### 启动前端（新终端窗口）
```bash
cd frontend
npm run dev
```

### 5. 访问界面

- 前端入口：[http://localhost:5173](http://localhost:5173)

---

## 📁 项目结构

```
github_tracker/
├── frontend/               # 前端代码
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
├── src/                    # 后端代码
│   ├── github_tracker.py           # GitHub API 封装
│   ├── repo_activity_tracker.py    # 项目动态追踪模块
│   ├── api_server.py               # FastAPI 服务入口
│   └── scheduler.py                # 定时任务调度器
├── config/                # 配置文件
├── data/                  # 数据缓存与存储
└── requirements.txt       # Python 依赖列表
```

---

## 🐞 常见问题

### Q1. 为什么项目启动不成功？
- 请确保 Node.js 版本 ≥ **18.x**
- 检查 `.env` 文件中是否配置了合法的 GitHub Token

### Q2. 添加追踪项目时页面卡顿？
- 请检查浏览器控制台是否有请求失败或错误日志
- 当前版本异步加载尚在优化中，建议少量操作观察响应情况

---

## 📈 Roadmap

- [ ] 项目搜索结果优化（多维度筛选）
- [ ] 提交记录分页展示
- [ ] 前端响应式适配

---

## 🤝 贡献指南

1. Fork 本项目  
2. 创建分支：`git checkout -b feature/YourFeature`  
3. 提交修改：`git commit -m 'Add YourFeature'`  
4. 推送分支：`git push origin feature/YourFeature`  
5. 提交 Pull Request 🎉

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。
