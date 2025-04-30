# AIgument
"AIgument" 是一个基于大语言模型的智能对话平台，支持多种交互模式，包括辩论模式、对话模式和问答模式。该平台旨在通过AI模型间的互动，探索并展示人工智能在不同场景下的推理与表达能力。

## 功能特点

- **多模式交互**：
  - **辩论模式**：两个AI模型分别扮演正反方，就同一主题进行多轮辩论
  - **对话模式**：两个不同角色的AI进行对话，展示不同视角的观点交流
  - **问答模式**：提供详细、简洁或苏格拉底式的回答风格选择

- **实时显示**：
  - 流式输出技术（SSE）实时显示生成内容
  - 非流式模式下支持逐步显示和打字机效果，提升用户体验

- **丰富表现形式**：
  - Markdown格式支持，包括粗体、列表、引用、代码块等格式化展示
  - 代码高亮显示
  - 打字机动画效果

- **自定义选项**：
  - 辩论轮次选择（1-5轮）
  - 对话角色选择（科学家、哲学家、作家等）
  - 问答风格选择（详细分析、简洁直接、苏格拉底式）
  - 模型和服务提供商选择（DeepSeek、OpenAI等）

- **现代化UI**：
  - 响应式设计，适配桌面和移动设备
  - 动画效果增强用户体验
  - 清晰的视觉层次和交互反馈

- **强化日志系统**：
  - 终端控制台显示详细的API请求和响应信息
  - 实时流式输出内容在控制台同步显示
  - Token用量统计和性能监控
  - 完整的错误诊断信息

## 技术栈

- **后端**：Flask提供Web服务
- **前端**：
  - HTML5
  - CSS3 (Tailwind CSS)
  - JavaScript (模块化结构)
- **AI模型**：基于DeepSeek和OpenAI的LLM
- **渲染工具**：
  - marked.js (Markdown渲染)
  - highlight.js (代码高亮)
- **流媒体技术**：Server-Sent Events (SSE)

## 项目结构

```
aigument/
├── .env                # 环境变量配置文件
├── requirements.txt    # 项目依赖
├── README.md           # 项目说明文档
├── LICENSE             # Apache 2.0许可证
├── .gitignore          # Git忽略文件
└── src/                # 源代码目录
    ├── app.py          # Flask应用主文件 (含API接口)
    ├── models.py       # 数据库模型定义
    ├── check_db.py     # 数据库检查工具
    ├── agents/         # AI代理模块
    │   └── debater.py  # 辩论者类实现 (支持流式输出)
    ├── static/         # 静态资源文件
    │   ├── css/        # CSS样式
    │   │   └── style.css   # 主要样式文件
    │   └── js/         # JavaScript文件
    │       ├── main.js     # 主要JS逻辑
    │       ├── debate.js   # 辩论模式功能
    │       ├── chat.js     # 对话模式功能
    │       ├── qa.js       # 问答模式功能
    │       ├── history.js  # 历史记录功能
    │       └── utils.js    # 工具函数
    ├── templates/      # HTML模板
    │   ├── index.html    # 主页面模板
    │   └── history.html  # 历史记录页面
    └── instance/       # 数据库实例目录
        └── aigument.db   # SQLite数据库文件
```

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```