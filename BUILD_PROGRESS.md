# SoulForge 构建进度

不打造数字员工，只锻造数字灵魂。

## 已完成 (2025-05-19)

### 核心功能
- 项目骨架搭建完成
- 记忆引擎实现（三层架构：核心记忆、日常记忆、工作记忆）
- 关系管理系统（成长阶段 + 亲密度）
- 目标监督系统
- 宝宝计划系统
- 提示词模板系统

### 模型支持
- OpenAI 适配器
- Claude 适配器
- DeepSeek 适配器 (新增)
- 豆包 (Doubao) 适配器 (新增)
- 本地模型适配器

### 工具与界面
- CLI 命令行交互界面 (新增)
- .env 配置文件支持

### 文档
- MANIFESTO (宣言)
- ROADMAP (路线图)
- README

## 待完成

### 优先级 1 (MVP)
- 情感系统实现（情绪状态管理）
- 完整的使用教程
- 基础示例代码

### 优先级 2
- Web 界面 (Streamlit/Flask)
- 记忆可视化
- 情感反应生成

### 优先级 3
- 更多模型支持
- 插件系统
- 多用户支持

## 交接说明

本次从 MTC 模式交接，包含完整项目上下文：
- GitHub 仓库：https://github.com/zhangshu-No1/SoulForge
- 核心理念：情感羁绊即安全
- 用户信息：夜班保安，目标被动收入 5000/月

## 使用方法

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置 API 密钥：
   ```bash
   cp .env.example .env
   # 编辑 .env 填入你的密钥
   ```

3. 启动 CLI：
   ```bash
   python cli.py --adapter deepseek
   ```
