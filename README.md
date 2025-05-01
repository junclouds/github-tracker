# GitHub Tracker

一个用于追踪 GitHub 仓库动态的应用程序。

## 项目结构

```
github_tracker/
├── config/                 # 配置文件
│   ├── model_config.yaml  # 模型配置
│   └── logging_config.yaml # 日志配置
├── src/                    # 源代码
│   ├── llm/               # GitHub客户端
│   ├── utils/             # 工具类
│   └── handlers/          # 错误处理
├── data/                   # 数据存储
│   ├── cache/             # 缓存数据
│   ├── prompts/           # 提示模板
│   └── outputs/           # 输出结果
└── examples/              # 示例代码
```

## 主要功能

- 获取热门仓库列表
- 追踪指定仓库的活动
- 搜索GitHub仓库
- 查看仓库动态更新

## 开发环境设置

1. 克隆仓库：
```bash
git clone <repository-url>
cd github_tracker
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并添加：
```
GITHUB_TOKEN=your_github_token
```

5. 运行应用：
```bash
uvicorn src.api_server:app --reload
```

## 最佳实践

- 使用YAML进行配置管理
- 实现适当的错误处理
- 使用速率限制保护API
- 实现缓存机制
- 保持代码文档更新
- 使用类型注解
- 遵循模块化设计

## 开发提示

- 遵循PEP 8编码规范
- 编写单元测试
- 使用版本控制
- 保持文档更新
- 监控API使用情况

## 许可证

MIT
