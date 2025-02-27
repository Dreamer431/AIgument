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

- **现代化UI**：
  - 响应式设计，适配桌面和移动设备
  - 动画效果增强用户体验
  - 清晰的视觉层次和交互反馈

## 技术栈

- **后端**：Flask提供Web服务
- **前端**：
  - HTML5
  - CSS3 (Tailwind CSS)
  - JavaScript (模块化结构)
- **AI模型**：基于DeepSeek LLM
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
    ├── main.py         # 入口文件
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
    │       └── utils.js    # 工具函数
    └── templates/      # HTML模板
        └── index.html  # 主页面模板
```

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
在`.env`文件中设置：
```
DEEPSEEK_API_KEY=你的API密钥
```

3. 运行应用：
```bash
cd src
python app.py
```

4. 访问应用：
打开浏览器访问 http://localhost:5000

## 使用指南

1. 选择交互模式：辩论模式、对话模式或问答模式
2. 输入主题或问题
3. 根据所选模式配置相应参数（轮次、角色、风格等）
4. 选择是否启用流式输出
5. 点击相应按钮开始交互
6. 查看生成的内容，支持Markdown格式显示

## 系统要求

- Python 3.8+
- 现代浏览器（支持SSE和ES6）
- DeepSeek API访问权限

## 最近更新

- 添加了多模式交互功能（辩论、对话、问答）
- 重构前端代码，实现HTML、CSS和JavaScript的分离
- 优化用户界面，增强视觉效果和用户体验
- 修复流式输出切换按钮和加载动画
- 改进非流式模式下的内容展示逻辑

## 许可证

本项目采用Apache License 2.0许可证。详情请参见[LICENSE](LICENSE)文件。

## 贡献

欢迎提交问题和改进建议。如果您想为项目做出贡献，请遵循以下步骤：
1. Fork 项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request
