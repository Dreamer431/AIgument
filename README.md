# AIgument
"AIgument" 是一个基于大语言模型的对抗性辩论平台，旨在通过两个AI模型围绕某一话题展开激烈辩论，探索并展示人工智能在复杂问题上的推理与辩证能力。项目将通过模拟AI间的对话与思维碰撞，呈现不同视角下的观点冲突与共识，揭示AI在道德、哲学、科技等多个领域的多维度思考方式。

## 功能特点

- **实时辩论生成**：利用流式输出技术（SSE）实时显示AI辩论内容
- **Markdown格式支持**：辩论内容以格式化的方式呈现，包括粗体、列表、引用等
- **多轮辩论**：支持1-5轮的辩论，可根据需要选择
- **自定义主题**：用户可以自由输入任何辩论主题
- **响应式设计**：适配桌面和移动设备的现代化界面

## 技术栈

- **后端**：Flask提供Web服务
- **前端**：HTML5, CSS3 (Tailwind CSS), JavaScript
- **AI模型**：基于DeepSeek LLM的辩论系统
- **Markdown渲染**：marked.js库
- **代码高亮**：highlight.js
- **流式输出**：Server-Sent Events (SSE)技术

## 项目结构

```
aigument/
├── .env                # 环境变量配置文件
├── requirements.txt    # 项目依赖
├── README.md          # 项目说明文档
└── src/               # 源代码目录
    ├── app.py         # Flask应用主文件 (含API接口)
    ├── agents/        # AI代理模块
    │   └── debater.py # 辩论者类实现 (支持流式输出)
    ├── static/        # 静态资源文件
    └── templates/     # HTML模板
        └── index.html # 主页面模板 (含Markdown渲染)
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

1. 在首页输入辩论主题（例如："人工智能是否会取代人类工作"）
2. 选择辩论轮数（1-5轮）
3. 决定是否启用流式输出（实时显示）
4. 点击"开始辩论"按钮
5. 欣赏AI辩手进行的精彩辩论，支持Markdown格式显示

## 系统要求

- Python 3.8+
- 现代浏览器（支持SSE和ES6）
- DeepSeek API访问权限

## 项目更新

最近更新：
- 添加了流式输出功能，实现实时显示辩论内容
- 增加了Markdown格式支持，使辩论内容更加清晰
- 优化了用户界面，提供更好的交互体验

## 许可证

本项目采用Apache License 2.0许可证。详情请参见[LICENSE](LICENSE)文件。
