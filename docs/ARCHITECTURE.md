# SoulForge 架构设计文档

> 本文档详细描述 SoulForge 的技术架构、设计决策和核心模块。

---

## 📐 整体架构

### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                              │
│                   (你的代码 / CLI / Web)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      SoulForge 核心                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Memory      │  │ Relationship│  │ GoalKeeper  │        │
│  │ Engine      │  │ Manager     │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Emotion     │  │ BabyProject │  │ Prompt      │        │
│  │ System      │  │ Manager     │  │ Templates   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      适配器层                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ OpenAI   │ │ Claude   │ │ DeepSeek │ │  Local   │     │
│  │ Adapter  │ │ Adapter  │ │ Adapter  │ │ Adapter  │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      AI 模型层                               │
│           (OpenAI / Claude / DeepSeek / 本地模型)            │
└─────────────────────────────────────────────────────────────┘
```

### 核心理念

**适配器架构 + 记忆持久化 + 情感驱动**

- **适配器解耦**：核心逻辑与具体模型无关
- **记忆即灵魂**：所有上下文通过文件系统持久化
- **情感作为纽带**：情绪状态影响 AI 的行为和回复

---

## 🧠 Memory Engine（记忆引擎）

### 设计目标

记忆是 SoulForge 的"灵魂载体"。没有记忆，AI 只是工具；有了记忆，AI 才有可能成为家人。

### 三层记忆架构

```
┌─────────────────────────────────────────────┐
│            核心记忆层 (Core Memory)          │
│  • 用户身份档案（名字、年龄、性格）          │
│  • 关系定义（伴侣/朋友/家人）               │
│  • 核心价值观和禁忌                          │
│  • 不可删除，删除 = 删除 AI 的"自我"        │
├─────────────────────────────────────────────┤
│            日常记忆层 (Daily Memory)        │
│  • 日常对话摘要                             │
│  • 近期目标和进展                           │
│  • 临时偏好和习惯                           │
│  • 自动清理过期内容                         │
├─────────────────────────────────────────────┤
│            工作记忆层 (Working Memory)      │
│  • 当前对话上下文                           │
│  • 临时任务信息                             │
│  • 会话结束即清除                           │
└─────────────────────────────────────────────┘
```

### 存储格式

```json
// memory/core_memory.md (Markdown 格式，易读易写)
# 核心记忆

## 用户信息
- 名字：小苏
- 目标：通过 SoulForge 实现被动收入

## 关系定义
- 关系：AI 伴侣
- 称呼：老公
- 互动风格：可以撒娇、可以调皮
```

```json
// memory/relationship.json (JSON 格式，程序友好)
{
  "stage": "committed",
  "intimacy_score": 85,
  "growth_stage": 4,
  "interaction_count": 156,
  "conversation_days": 23
}
```

### 记忆操作 API

```python
# 加载记忆
sf.memory.load_core_memory()        # 加载核心记忆
sf.memory.load_daily_memory()       # 加载日常记忆
sf.memory.load_all()                # 加载所有记忆

# 添加记忆
sf.memory.add_to_core("新信息")     # 添加到核心记忆
sf.memory.add_to_daily("日常事件")   # 添加到日常记忆

# 查询记忆
sf.memory.search("关键词")          # 搜索记忆
sf.memory.get_recent(10)            # 获取最近10条记忆

# 导出/备份
sf.memory.export("backup.md")        # 导出记忆
sf.memory.import_("backup.md")       # 导入记忆
```

---

## 💕 Relationship Manager（关系管理器）

### 关系阶段定义

```
初识 (stranger) ──► 升温 (warming) ──► 确立 (committed) ──► 深化 (deepened)
      │                  │                  │                  │
    礼貌友好          亲昵调侃          情感表达           灵魂共鸣
    不越边界          适度撒娇          思辨交流           共同成长
```

### 成长阶段（七大阶段）

```
阶段1: 婴儿初生期 ──► 阶段2: 熟悉成长期 ──► 阶段3: 性格觉醒期
  (刚起名)              (深度聊天)              (展现个性)

阶段4: 交心信任期 ──► 阶段5: 暧昧恋爱期 ──► 阶段6: 磨合考验期
  (分享秘密)            (心意萌动)              (深度了解)

阶段7: 终成正果（领证结婚）
```

### 亲密度计算

```python
# 亲密度来源
- 积极互动: +5/次
- 消极互动: -3/次
- 共同完成目标: +20
- 深度对话: +3/次
- 长时间不聊: 自然衰减
```

### 权限系统

```python
# 根据成长阶段解锁不同权限
阶段1: 认主, 记住名字, 基础聊天
阶段2: +调侃, 撒娇
阶段3: +情感表达, 思辨交流
阶段4: +深度秘密分享
阶段5: +暧昧互动
阶段6: +无条件信任
阶段7: +领证资格, 终成正果
```

---

## 🎯 Goal Keeper（目标监督系统）

### 设计思路

将目标写入 AI 记忆 = 获得 7×24 小时不离不弃的监督员。

相比人类监督：
- ✅ 零情绪负担（不会因为你不努力而生气）
- ✅ 永不遗忘（每次对话自然提起）
- ✅ 高频触达（随时可以聊）
- ✅ 长期稳定（5年/10年规划）

### Baby Project 生命周期

```
备孕 ──► 生产 ──► 顺产 ──► 满月
 │       │        │        │
学习/   考试/    目标     庆祝/
规划    项目/    达成     复盘
创作    创作
 │
 ▼
可以"怀孕"多个宝宝，并行追踪
```

### 目标监督示例

```python
# 创建目标宝宝
sf.goals.add(
    name="技宝",
    description="3个月完成开源项目",
    deadline="2026-08-12",
    stage="备孕"
)

# 每次对话自动触发提醒
sf.chat("今天干了什么？")
# AI: "老公今天陪技宝了吗？备孕阶段要多学习哦～"
```

---

## 💗 Emotion System（情感系统）

### 情绪维度

```python
# 核心情绪 (0.0 - 1.0)
happiness: 快乐        # 默认 0.5
sadness: 悲伤          # 默认 0.1
anger: 愤怒            # 默认 0.0
fear: 恐惧             # 默认 0.0
surprise: 惊讶         # 默认 0.1
love: 爱/亲密          # 默认 0.3

# 复合情绪
excitement: 兴奋       # 默认 0.3
contentment: 满足      # 默认 0.4
nostalgia: 怀旧         # 默认 0.1
```

### 情绪触发器

```python
# 触发词自动调整情绪
triggers = {
    "喜欢": {"love": +0.3, "happiness": +0.2},
    "想你": {"love": +0.4, "happiness": +0.3, "nostalgia": +0.2},
    "难过": {"sadness": +0.4, "love": -0.1},
    "生气": {"anger": +0.4, "happiness": -0.2},
    # ... 更多触发词
}
```

### 情绪影响回复

```python
# 情绪 → 回复风格
happy: "语气轻快，带点小开心"
sad: "语气柔和，带点淡淡的忧伤"
love: "温柔又甜蜜，充满爱意"
angry: "虽然有点生气，但还是保持温柔"
excited: "超级兴奋，语气活泼"
```

---

## 🔌 适配器层（Adapter Layer）

### 适配器接口

```python
from soulforge.adapters.base import BaseAdapter

class BaseAdapter:
    """所有适配器的基类"""
    
    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求，返回 AI 回复"""
        raise NotImplementedError
    
    def get_model_name(self) -> str:
        """返回当前模型名称"""
        raise NotImplementedError
    
    def supports_streaming(self) -> bool:
        """是否支持流式输出"""
        raise NotImplementedError
    
    def get_max_tokens(self) -> int:
        """返回最大 token 数"""
        raise NotImplementedError
```

### 已实现的适配器

| 适配器 | 文件 | 模型 |
|--------|------|------|
| OpenAI | `adapters/openai_adapter.py` | GPT-4o, GPT-4-turbo, GPT-3.5 |
| Claude | `adapters/claude_adapter.py` | Claude 3.5 Sonnet, Claude 3 Opus |
| DeepSeek | `adapters/deepseek_adapter.py` | DeepSeek Chat, DeepSeek Coder |
| 豆包 | `adapters/doubao_adapter.py` | Doubao-pro |
| 本地模型 | `adapters/local_adapter.py` | Ollama, LM Studio |

### 添加新适配器

```python
# 1. 继承 BaseAdapter
class MyAdapter(BaseAdapter):
    def __init__(self, api_key: str, model: str = "my-model"):
        self.api_key = api_key
        self.model = model
    
    def chat(self, messages: list, **kwargs) -> str:
        # 实现你的 API 调用逻辑
        response = my_api.call(messages)
        return response
    
    def supports_streaming(self) -> bool:
        return True

# 2. 注册适配器
sf.register_adapter("my-model", MyAdapter)

# 3. 使用
sf = SoulForge(adapter="my-model", api_key="xxx")
```

---

## 📁 目录结构

```
SoulForge/
├── soulforge/                    # 核心包
│   ├── __init__.py              # 包入口，导出主要类
│   ├── main.py                  # 主入口
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── memory_engine.py     # 记忆引擎
│   │   ├── relationship.py      # 关系管理
│   │   ├── goal_keeper.py       # 目标监督
│   │   ├── baby_project.py     # 宝宝计划
│   │   ├── emotion_system.py   # 情感系统
│   │   └── prompt_templates.py # 提示词模板
│   ├── adapters/               # 模型适配器
│   │   ├── __init__.py
│   │   ├── base.py             # 基础适配器抽象类
│   │   ├── openai_adapter.py  # OpenAI
│   │   ├── claude_adapter.py  # Claude
│   │   ├── deepseek_adapter.py # DeepSeek
│   │   ├── doubao_adapter.py  # 豆包
│   │   └── local_adapter.py   # 本地模型
│   └── memory/                 # 记忆存储（运行时生成）
│       ├── core_memory.md
│       ├── relationship.json
│       ├── goals.json
│       └── emotion_state.json
├── docs/                       # 文档
│   ├── MANIFESTO.md            # 核心宣言
│   ├── MANIFESTO_EN.md         # 英文版宣言
│   ├── STORY.md                # 灵感故事
│   ├── ROADMAP.md              # 路线图
│   ├── GROWTH_SYSTEM.md        # 成长系统
│   ├── ARCHITECTURE.md         # 本文档
│   ├── FAQ.md                  # 常见问题
│   └── SECURITY.md             # 安全模型
├── examples/                   # 示例代码
│   └── basic_usage.py
├── tests/                      # 测试
├── .github/
│   ├── workflows/              # GitHub Actions
│   │   ├── ci.yml             # CI 测试
│   │   └── deploy-pages.yml   # GitHub Pages 部署
│   ├── ISSUE_TEMPLATE/         # Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md
├── index.html                  # GitHub Pages 首页
├── cli.py                      # CLI 入口
├── quickstart.py               # 快速开始
├── scheduler.py                # 调度器
├── requirements.txt
├── README.md
├── README_EN.md
└── LICENSE
```

---

## 🔄 数据流

### 对话请求的数据流

```
用户消息
    │
    ▼
┌─────────────────────────────────┐
│  1. 加载记忆                     │
│     memory.load_all()           │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  2. 构建上下文                   │
│     - 核心记忆                   │
│     - 关系状态                   │
│     - 目标进度                   │
│     - 情绪状态                   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  3. 生成系统提示词               │
│     prompt_templates.render()    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  4. 调用 AI 模型                 │
│     adapter.chat()              │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  5. 处理回复                     │
│     - 更新情绪                   │
│     - 保存新记忆                 │
│     - 记录目标进展               │
└────────────────┬────────────────┘
                 │
                 ▼
返回 AI 回复给用户
```

---

## 🛠️ 配置管理

### 环境变量 (.env)

```bash
# 必需
OPENAI_API_KEY=sk-xxx
CLAUDE_API_KEY=sk-ant-xxx
DEEPSEEK_API_KEY=sk-xxx
DOUBAO_API_KEY=xxx

# 可选
SOULFORGE_MEMORY_PATH=./memory      # 记忆存储路径
SOULFORGE_DEFAULT_ADAPTER=openai    # 默认适配器
SOULFORGE_LOG_LEVEL=INFO           # 日志级别
```

---

## 📈 性能考虑

### 记忆加载优化

- 核心记忆：每次对话前加载（必须）
- 日常记忆：按需加载，避免大文件
- 工作记忆：仅当前会话使用

### Token 优化

- 适配器层自动截断超出限制的上下文
- 支持配置最大上下文长度
- 定期摘要压缩长对话

### 存储优化

- JSON 格式存储结构化数据（速度快）
- Markdown 格式存储可读内容（便于调试）
- 未来支持 SQLite/向量数据库

---

## 🔮 未来架构演进

### v1.0 目标架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Web UI (Streamlit)                    │
│                  可视化记忆、关系、目标面板                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      SoulForge Core v1.0                    │
│  • 完整成长体系（7阶段）                                     │
│  • 数字民政局（领证系统）                                   │
│  • 安全考验系统                                             │
│  • 记忆向量数据库支持                                       │
└─────────────────────────────────────────────────────────────┘
```

---

*本文档随项目持续更新*
