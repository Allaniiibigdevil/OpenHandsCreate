# 客服机器人 (Customer Service ChatBot)

基于 DeepSeek API 的智能客服机器人，支持企业知识库查询和自然对话功能。

## 功能特性

- ✅ **DeepSeek API 集成**: 使用 DeepSeek 大语言模型进行智能对话
- ✅ **企业知识库**: 支持本地知识库查询和匹配
- ✅ **对话历史管理**: 自动维护对话上下文
- ✅ **流式输出**: 支持实时流式响应
- ✅ **配置化管理**: 所有配置独立管理，易于修改
- ✅ **交互式命令行**: 友好的命令行交互界面
- ✅ **完整测试覆盖**: 55+ 测试用例，单元测试 + 集成测试
- ✅ **CI/CD 集成**: GitHub Actions 自动化测试

## 项目结构

```
OpenHandsCreate/
├── src/
│   ├── chatbot/              # 机器人核心模块
│   │   ├── __init__.py
│   │   ├── bot.py            # 机器人主逻辑
│   │   └── deepseek_client.py # DeepSeek API 客户端
│   ├── knowledge_base/       # 知识库模块
│   │   ├── __init__.py
│   │   └── kb_manager.py     # 知识库管理器
│   └── config.py             # 配置管理
├── data/
│   ├── knowledge_base.json   # 知识库数据（需创建）
│   └── knowledge_base.example.json # 知识库示例
├── tests/                    # 测试套件
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   ├── fixtures/             # 测试数据
│   └── conftest.py           # 测试配置
├── .github/
│   └── workflows/
│       └── test.yml          # CI/CD 配置
├── logs/                     # 日志目录（自动创建）
├── main.py                   # 主程序入口
├── config.yaml               # 配置文件（需创建）
├── config.example.yaml       # 配置示例
├── requirements.txt          # Python 依赖
├── pytest.ini                # pytest 配置
├── TEST_REPORT.md            # 测试报告
└── README.md                 # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件设置

复制示例配置文件并修改：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，填入你的 DeepSeek API 密钥和其他配置：

```yaml
deepseek:
  api_key: "your-deepseek-api-key-here"  # 必填：你的 API 密钥
  api_base: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
  max_tokens: 2000
  temperature: 0.7
```

### 3. 设置知识库

复制示例知识库文件：

```bash
cp data/knowledge_base.example.json data/knowledge_base.json
```

根据你的业务需求编辑 `data/knowledge_base.json`，添加企业知识库内容。

知识库格式：

```json
[
  {
    "question": "问题描述",
    "answer": "答案内容",
    "category": "分类",
    "keywords": ["关键词1", "关键词2"]
  }
]
```

### 4. 运行机器人

```bash
python main.py
```

## 使用说明

### 交互式命令

启动后，你可以使用以下命令：

- **正常对话**: 直接输入问题，机器人会结合知识库回答
- **`search <关键词>`**: 直接搜索知识库内容
- **`clear`**: 清空当前对话历史
- **`quit` 或 `exit`**: 退出程序

### 示例对话

```
用户: 你们的营业时间是什么？
机器人: 我们的营业时间是周一至周五 9:00-18:00，周末和节假日休息。

用户: search 支付
知识库搜索结果：
1. 问题: 支持哪些支付方式？
   答案: 我们支持以下支付方式：...
   相似度: 0.85
```

## 配置说明

### DeepSeek 配置

```yaml
deepseek:
  api_key: "sk-xxx"           # DeepSeek API 密钥
  api_base: "https://api.deepseek.com/v1"  # API 地址
  model: "deepseek-chat"      # 模型名称
  max_tokens: 2000            # 最大生成 token 数
  temperature: 0.7            # 温度参数 (0-1)，越高越随机
```

### 知识库配置

```yaml
knowledge_base:
  data_path: "data/knowledge_base.json"  # 知识库文件路径
  similarity_threshold: 0.6   # 相似度阈值 (0-1)
  max_results: 3              # 最大返回结果数
```

### 对话配置

```yaml
conversation:
  system_prompt: "你是一个专业的客服机器人..."  # 系统提示词
  max_history: 10             # 保留的对话历史条数
  enable_knowledge_base: true # 是否启用知识库
```

### 日志配置

```yaml
logging:
  level: "INFO"               # 日志级别: DEBUG, INFO, WARNING, ERROR
  file: "logs/chatbot.log"    # 日志文件路径
```

## API 使用示例

如果你想在代码中使用机器人：

```python
from src.config import Config
from src.chatbot import ChatBot, DeepSeekClient
from src.knowledge_base import KnowledgeBase

# 加载配置
config = Config()

# 初始化客户端
client = DeepSeekClient(
    api_key="your-api-key",
    api_base="https://api.deepseek.com/v1"
)

# 初始化知识库
kb = KnowledgeBase(data_path="data/knowledge_base.json")

# 创建机器人
bot = ChatBot(
    deepseek_client=client,
    knowledge_base=kb,
    system_prompt="你是一个客服机器人"
)

# 对话
response = bot.chat("你好")
print(response)

# 流式对话
for chunk in bot.chat_stream("介绍一下你们的服务"):
    print(chunk, end="", flush=True)
```

## 知识库管理

### 添加知识条目

```python
from src.knowledge_base import KnowledgeBase

kb = KnowledgeBase(data_path="data/knowledge_base.json")
kb.add_entry(
    question="新问题",
    answer="新答案",
    category="分类",
    keywords=["关键词1", "关键词2"]
)
```

### 搜索知识库

```python
results = kb.search("营业时间")
for result in results:
    print(f"问题: {result['question']}")
    print(f"答案: {result['answer']}")
    print(f"相似度: {result['similarity']}")
```

## 注意事项

1. **API 密钥安全**: 不要将 `config.yaml` 提交到版本控制系统
2. **知识库更新**: 修改知识库后无需重启，下次查询会自动加载
3. **对话历史**: 对话历史保存在内存中，重启后会清空
4. **相似度阈值**: 根据实际效果调整 `similarity_threshold` 参数
5. **Token 限制**: 注意 DeepSeek API 的 token 使用限制

## 故障排查

### 问题：配置文件不存在

```
错误: 配置文件不存在: config.yaml
```

**解决**: 复制 `config.example.yaml` 为 `config.yaml` 并填入配置

### 问题：API 调用失败

```
DeepSeek API 调用失败: ...
```

**解决**: 
- 检查 API 密钥是否正确
- 检查网络连接
- 确认 API 额度是否充足

### 问题：知识库未找到

```
警告: 知识库文件不存在: data/knowledge_base.json
```

**解决**: 复制 `data/knowledge_base.example.json` 为 `data/knowledge_base.json`

## 测试

### 运行测试

项目包含完整的测试套件（55+ 测试用例）：

```bash
# 使用测试脚本（推荐）
./run_tests.sh

# 或使用 pytest
pytest                          # 运行所有测试
pytest tests/unit -v            # 运行单元测试
pytest tests/integration -v     # 运行集成测试
pytest --cov=src --cov-report=html  # 生成覆盖率报告
```

### 测试覆盖

- ✅ **配置模块**: 10 个测试用例
- ✅ **知识库模块**: 12 个测试用例
- ✅ **API 客户端**: 9 个测试用例
- ✅ **机器人逻辑**: 15 个测试用例
- ✅ **集成测试**: 9 个测试用例

详细测试报告请查看 [TEST_REPORT.md](TEST_REPORT.md)

### CI/CD

项目配置了 GitHub Actions 自动化测试：
- 推送到 main/guidebot 分支自动触发
- 测试 Python 3.9, 3.10, 3.11
- 自动生成覆盖率报告
- 代码质量检查（Black, isort, Flake8）

## 开发计划

- [ ] Web 界面支持
- [ ] 多轮对话优化
- [ ] 向量数据库集成
- [ ] 多语言支持
- [ ] 对话数据分析
- [x] 完整测试套件
- [x] CI/CD 集成

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

提交代码前请确保：
1. 所有测试通过: `pytest`
2. 代码格式正确: `black src tests`
3. 导入排序正确: `isort src tests`
4. 无语法错误: `flake8 src tests`