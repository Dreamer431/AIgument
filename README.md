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
  - 深色模式支持

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
    │   ├── js/         # JavaScript文件
    │   │   ├── main.js     # 主要JS逻辑
    │   │   ├── debate.js   # 辩论模式功能
    │   │   ├── chat.js     # 对话模式功能
    │   │   ├── qa.js       # 问答模式功能
    │   │   ├── history.js  # 历史记录功能
    │   │   ├── ui.js       # UI交互和动画
    │   │   └── utils.js    # 工具函数
    │   └── img/        # 图片资源
    ├── templates/      # HTML模板
    │   ├── index.html    # 主页面模板
    │   └── history.html  # 历史记录页面
    └── instance/       # 数据库实例目录
        └── aigument.db   # SQLite数据库文件
```

## 安装和运行

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/aigument.git
cd aigument
```

2. 创建并激活虚拟环境(可选)：
```bash
# 使用venv
python -m venv venv
# Windows激活
venv\Scripts\activate
# Linux/Mac激活
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建`.env`文件并添加以下内容：
```
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

5. 运行应用：
```bash
cd src
python app.py
```

6. 打开浏览器访问：http://127.0.0.1:5000

## 使用说明

### 辩论模式

1. 选择"辩论模式"
2. 输入辩论主题，如"人工智能是否会超越人类智能"
3. 设置辩论轮次（1-5轮）
4. 选择是否开启流式输出
5. 选择模型提供商和具体模型
6. 点击"开始辩论"
7. 系统将生成正反双方的辩论内容

### 对话模式

1. 选择"AI对话模式"
2. 输入对话主题
3. 选择两个角色（如科学家和哲学家）
4. 设置对话轮次
5. 点击"开始对话"
6. 系统将生成两个角色间的对话内容

### 问答模式

1. 选择"问答模式"
2. 输入您的问题
3. 选择回答风格（详细分析、简洁直接或苏格拉底式）
4. 点击"提交问题"
5. 系统将根据选择的风格生成回答

## API文档

AIgument提供了以下API接口：

### 辩论API

#### 初始化辩论
- **端点**: `/api/debate/init`
- **方法**: POST
- **参数**:
  - `topic` (必填): 辩论主题
  - `rounds`: 辩论轮次，默认为3
  - `provider`: 模型提供商，默认为'deepseek'
  - `model`: 模型名称，默认为'deepseek-chat'
- **返回**: 会话ID和设置信息

#### 流式辩论
- **端点**: `/api/debate/stream`
- **方法**: GET
- **参数**:
  - `topic` (必填): 辩论主题
  - `rounds`: 辩论轮次，默认为3
  - `provider`: 模型提供商
  - `model`: 模型名称
- **返回**: Server-Sent Events流式内容

#### 单次辩论
- **端点**: `/api/debate/single`
- **方法**: POST
- **参数**:
  - `topic` (必填): 主题或上一轮回应
  - `side` (必填): '正方'或'反方'
  - `round`: 当前轮次，默认为1
  - `provider`: 模型提供商
  - `model`: 模型名称
  - `session_id`: 会话ID
- **返回**: 生成的单轮辩论内容

### 历史记录API

#### 获取历史列表
- **端点**: `/api/history`
- **方法**: GET
- **参数**:
  - `type`: 会话类型（'all', 'debate', 'chat', 'qa'）
- **返回**: 历史会话列表

#### 获取会话详情
- **端点**: `/api/history/<session_id>`
- **方法**: GET
- **返回**: 特定会话的详细消息内容

#### 导出会话
- **端点**: `/api/history/<session_id>/export`
- **方法**: GET
- **参数**:
  - `format`: 导出格式（'json'或'markdown'）
- **返回**: 导出的会话内容

#### 删除会话
- **端点**: `/api/history/<session_id>`
- **方法**: DELETE
- **返回**: 操作结果

## 最新优化 🚀

项目已完成全面性能优化，主要改进包括：

- ⚡ **性能提升**：API响应速度提升 30-97%，数据库查询速度提升 50-80%
- 🔒 **安全增强**：完整的输入验证和错误处理
- 📊 **监控系统**：新增性能监控端点 `/api/stats`
- 🎯 **缓存机制**：智能响应缓存，显著减少重复查询
- 🔧 **配置管理**：集中化配置，便于环境切换

**查看详情**：
- [优化说明文档](OPTIMIZATION.md) - 详细的优化内容和性能测试
- [快速开始指南](QUICKSTART.md) - 如何使用新功能

## 后续开发计划

1. **功能扩展**：
   - 多语言支持
   - 语音输入和输出
   - 更多自定义角色和模板

2. **技术提升**：
   - 增加更多模型和提供商支持
   - 改进流式输出性能
   - 添加更多数据可视化功能

3. **用户体验**：
   - 保存用户偏好设置
   - 增加更多主题样式
   - 支持更丰富的导出功能

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

1. 提交Bug报告
2. 提出新功能建议
3. 添加或改进文档
4. 提交代码改进和新功能

**贡献步骤**：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 许可证

本项目采用Apache 2.0许可证。详情请参阅[LICENSE](LICENSE)文件。