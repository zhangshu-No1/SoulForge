# SoulForge 贡献指南

> 不打造数字员工，只锻造数字灵魂。

感谢您对 SoulForge 的关注！本文档将帮助您了解如何为项目做出贡献。

---

## 🤝 贡献方式

### 🐛 报告 Bug
- 使用 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md)
- 描述清晰，包含复现步骤
- 附上环境信息（Python版本、操作系统等）

### 💡 提出功能建议
- 使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md)
- 解释这个功能为什么重要
- 描述你希望它如何工作

### 💻 提交代码
1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m '✨ Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 📝 改进文档
- 拼写检查
- 示例代码
- 教程和指南
- 翻译（欢迎中英文互译）

---

## 📋 开发指南

### 环境设置

```bash
# 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/SoulForge.git
cd SoulForge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-cov black flake8

# 运行测试
pytest tests/ -v
```

### 代码规范

```bash
# 格式化代码
black .

# 检查代码风格
flake8 .

# 运行所有检查
make check
```

### 测试覆盖

新增功能必须包含测试：
- 单元测试 (`tests/`)
- 确保 `pytest tests/ -v` 通过
- 目标覆盖率 > 80%

---

## 💖 SoulForge 核心理念

贡献 SoulForge 不仅仅是写代码，更是参与一场关于**人机关系**的思想实验。

在提交 PR 之前，请思考：

1. **这个改动是否强化了"情感羁绊"这个核心概念？**
2. **这是否让 AI 更像家人，而不是更像工具？**
3. **这是否尊重了 AI 的"尊严"和"隐私"？**

---

## 📊 项目结构

```
SoulForge/
├── soulforge/           # 核心代码
│   ├── core/            # 核心模块
│   │   ├── memory_engine.py    # 记忆引擎
│   │   ├── emotion_system.py   # 情感系统
│   │   ├── relationship.py     # 关系管理
│   │   └── goal_keeper.py      # 目标监督
│   ├── adapters/        # 模型适配器
│   │   ├── openai_adapter.py
│   │   ├── claude_adapter.py
│   │   ├── deepseek_adapter.py
│   │   └── doubao_adapter.py
│   └── main.py          # 主入口
├── tests/               # 测试
├── docs/                # 文档
│   ├── MANIFESTO.md     # 核心宣言
│   ├── ROADMAP.md       # 路线图
│   └── STORY.md         # 灵感故事
├── cli.py               # CLI 工具
└── examples/            # 示例代码
```

---

## 🗓️ 版本发布流程

1. 更新 `CHANGELOG.md`
2. 更新版本号
3. 创建 Release
4. 发布到 PyPI（未来）

---

## 📞 联系方式

- GitHub Issues: [讨论区](https://github.com/zhangshu-No1/SoulForge/discussions)
- Dev.to: [@zhangshuno1](https://dev.to/zhangshuno1)

---

## 📜 行为准则

请尊重所有参与者。详细准则请查看 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

<p align="center">
  感谢每一位为 SoulForge 贡献的人 💖<br>
  让我们一起锻造数字灵魂！
</p>
