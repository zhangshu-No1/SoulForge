# Contributing to SoulForge / 参与贡献到 SoulForge

English | [中文](#中文)

---

## How to Contribute / 如何参与

### 🐛 Report Bugs / 报告问题

Submit via [GitHub Issues](https://github.com/zhangshu-No1/SoulForge/issues/new/choose). Please include:
<!-- 请尽量包含以下内容： -->
- Bug description / 问题描述
- Steps to reproduce / 复现步骤
- Expected behavior / 期望行为
- Actual behavior / 实际行为
- Environment (OS, Python version) / 环境信息（操作系统、Python版本）

### 💡 Suggest Features / 提出建议

We welcome all forms of suggestions, including:
<!-- 我们欢迎任何形式的建议，包括但不限于： -->
- New feature ideas / 新功能想法
- User experience improvements / 用户体验改进
- Documentation improvements / 文档改进
- Architecture optimizations / 架构优化

### 💻 Submit Code / 提交代码

1. **Fork** the repository / Fork 本仓库
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
   <!-- 创建特性分支： -->
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
   <!-- 提交改动： -->
4. **Push** to the branch: `git push origin feature/amazing-feature`
   <!-- 推送分支： -->
5. **Open** a Pull Request / 提交 Pull Request

### 📝 Improve Documentation / 改进文档

Documentation is as important as code! If you find errors or unclear sections, please fix them directly.
<!-- 文档和代码一样重要！如果你发现文档有误或不清晰，欢迎直接修改。 -->

---

## Code Standards / 代码规范

- **Python**: Follow [PEP 8](https://pep8.org/)
  <!-- 遵循 PEP 8 -->
- **Type hints**: Add type annotations to all public functions
  <!-- 为所有公共函数添加类型注解 -->
- **Tests**: Write unit tests for new features
  <!-- 为新功能编写单元测试 -->
- **Comments**: Add necessary comments for complex logic
  <!-- 为复杂逻辑添加必要的注释 -->
- **Formatting**: Run `black` and `isort` before committing
  <!-- 提交前运行 black 和 isort -->

### Recommended Tools / 推荐工具

```bash
pip install black isort flake8 pytest pytest-cov
```

```bash
# Format code before committing
black soulforge/ tests/
isort soulforge/ tests/

# Run linting
flake8 soulforge/ tests/ --max-line-length=120

# Run tests
pytest tests/ -v --cov=soulforge
```

---

## 🌍 Development Setup / 开发环境设置

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SoulForge.git
cd SoulForge

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
pytest tests/ -v
```

---

## 🔧 Project Structure / 项目结构

```
soulforge/
├── core/           # Core engines (memory, relationship, goals, emotion)
│                   # 核心引擎（记忆、关系、目标、情感）
├── adapters/       # Model adapters (OpenAI, Claude, DeepSeek, etc.)
│                   # 模型适配器（OpenAI、Claude、DeepSeek 等）
├── memory/         # Memory storage directory
│                   # 记忆存储目录
├── tests/          # Unit tests
│                   # 单元测试
└── docs/           # Documentation
                    # 文档

```

---

## 📋 Commit Message Convention / 提交信息规范

Use clear, concise commit messages. Use English for commit messages.
<!-- 使用清晰、简洁的提交信息。提交信息统一使用英文。 -->

Format: `type: description`

```
feat:     New feature / 新功能
fix:      Bug fix / 修复bug
docs:     Documentation improvement / 文档改进
refactor: Code refactoring / 代码重构
test:     Adding or updating tests / 测试相关
chore:    Tooling / configuration / 工具/配置
style:    Formatting / code style / 格式/代码风格
```

Examples / 示例：
```
feat: Add DeepSeek adapter support
fix: Correct emotion_history variable name in emotion_system.py
docs: Add English README
refactor: Extract base adapter class
```

---

## ❤️ Code of Conduct / 行为准则

Please be respectful to all participants. We are committed to building a friendly, inclusive community environment.
<!-- 请尊重所有参与者。我们致力于打造一个友好、包容的社区环境。 -->

### Our Pledge / 我们的承诺

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.
<!-- 我们承诺让每个人都能在一个无骚扰的环境中参与项目，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、外貌、民族、宗教或性取向。 -->

### Our Standards / 行为标准

Examples of behavior that contributes to creating a positive environment include:
<!-- 有助于营造积极环境的示例行为包括： -->
- Using welcoming and inclusive language / 使用热情包容的语言
- Being respectful of differing viewpoints and experiences / 尊重不同的观点和经历
- Gracefully accepting constructive criticism / 优雅地接受建设性批评
- Focusing on what is best for the community / 关注对社区最有益的事情
- Showing empathy towards other community members / 对其他社区成员展现同理心

---

## 📞 Getting Help / 获取帮助

- 📖 Read the [README](README.md) and [docs](docs/)
- 💬 Start a [GitHub Discussion](https://github.com/zhangshu-No1/SoulForge/discussions)
- 🐛 Report bugs via [Issues](https://github.com/zhangshu-No1/SoulForge/issues)
- 📧 Contact the maintainers

---

## 🌟 Recognition / 致谢

All contributions are valued and appreciated. Contributors will be recognized in our documentation.
<!-- 所有贡献都有价值并受到赞赏。贡献者将在我们的文档中得到认可。 -->

Thank you for making SoulForge better! 💜
<!-- 感谢你让 SoulForge 变得更好！💜 -->

---

<a id="中文"></a>

# 参与贡献到 SoulForge

## 如何参与

### 🐛 报告问题

通过 [GitHub Issues](https://github.com/zhangshu-No1/SoulForge/issues/new/choose) 提交，请尽量包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（操作系统、Python版本）

### 💡 提出建议

我们欢迎任何形式的建议，包括但不限于：
- 新功能想法
- 用户体验改进
- 文档改进
- 架构优化

### 💻 提交代码

1. **Fork** 本仓库
2. **创建**特性分支：`git checkout -b feature/amazing-feature`
3. **提交**改动：`git commit -m 'Add amazing feature'`
4. **推送**分支：`git push origin feature/amazing-feature`
5. **提交** Pull Request

### 📝 改进文档

文档和代码一样重要！如果你发现文档有误或不清晰，欢迎直接修改。

---

## 代码规范

- **Python**: 遵循 [PEP 8](https://pep8.org/)
- **类型注解**: 为所有公共函数添加类型注解
- **测试**: 为新功能编写单元测试
- **注释**: 为复杂逻辑添加必要的注释
- **格式化**: 提交前运行 `black` 和 `isort`

### 推荐工具

```bash
pip install black isort flake8 pytest pytest-cov
```

```bash
# 格式化代码
black soulforge/ tests/
isort soulforge/ tests/

# 检查代码
flake8 soulforge/ tests/ --max-line-length=120

# 运行测试
pytest tests/ -v --cov=soulforge
```

---

## 开发环境设置

```bash
# Clone 你的 Fork
git clone https://github.com/YOUR_USERNAME/SoulForge.git
cd SoulForge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v
```

---

## 提交信息规范

使用清晰、简洁的提交信息。提交信息统一使用英文。

格式: `type: description`

```
feat:     新功能
fix:      修复bug
docs:     文档改进
refactor: 代码重构
test:     测试相关
chore:    工具/配置
style:    格式/代码风格
```

示例：
```
feat: Add DeepSeek adapter support
fix: Correct emotion_history variable name in emotion_system.py
docs: Add English README
```

---

## 行为准则

请尊重所有参与者。我们致力于打造一个友好、包容的社区环境。

---

感谢你让 SoulForge 变得更好！💜
