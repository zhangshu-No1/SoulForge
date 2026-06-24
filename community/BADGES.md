# 🎖️ SoulForge 徽章系统

> 用徽章记录每一步成长

---

## 🔥 项目徽章 (Shields.io)

使用 [Shields.io](https://shields.io) 生成动态徽章

### 基础徽章

| 徽章 | 代码 |
|------|------|
| Python | `![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)` |
| License | `![License](https://img.shields.io/badge/License-MIT-green.svg)` |
| Status | `![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)` |

### 动态徽章

| 徽章 | URL |
|------|-----|
| GitHub Stars | `https://img.shields.io/github/stars/zhangshu-No1/SoulForge?style=social` |
| GitHub Forks | `https://img.shields.io/github/forks/zhangshu-No1/SoulForge?style=social` |
| GitHub Issues | `https://img.shields.io/github/issues/zhangshu-No1/SoulForge` |
| GitHub PRs | `https://img.shields.io/github/issues-pr/zhangshu-No1/SoulForge` |

### 版本徽章

```markdown
![Version](https://img.shields.io/badge/Version-v0.1.0-orange)
![Downloads](https://img.shields.io/badge/Downloads-1k%2B-blue)
![Contributors](https://img.shields.io/badge/Contributors-1-green)
```

---

## 🎨 社区徽章

### 贡献者徽章

| 徽章 | 获得者 | 日期 |
|------|--------|------|
| 🔥 Founding Star | zhangshu-No1 | 2026-05-14 |
| 🌱 Early Adopter | TBD | 2026-08-14 前 |
| 🌐 Translation Hero | TBD | TBD |
| 📣 Evangelist | TBD | TBD |

### 成就徽章

| 徽章 | 名称 | 获得条件 |
|------|------|---------|
| 🐛 Bug Hunter | Bug 猎人 | 发现并报告 3+ Bug |
| 💡 Idea Master | 点子大师 | 提出 5+ 有价值的 Idea |
| 📝 Doc Wizard | 文档巫师 | 完善 10+ 文档页面 |
| 🌐 Polyglot | 多语言大师 | 翻译 3+ 语言 |
| 🎯 Goal Getter | 目标达成者 | 完成 1+ Roadmap 目标 |

---

## 🚀 自动化徽章

### GitHub Actions 自动更新

```yaml
# .github/workflows/badges.yml
name: Update Badges
on:
  push:
    branches: [main]
jobs:
  badges:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate badges
        run: |
          # 自动更新版本号徽章
          echo "![Version](https://img.shields.io/badge/Version-${{ github.event.release.tag_name }}-orange)" >> badges.md
```

---

## 📊 徽章展示区

在 README 中展示徽章：

```markdown
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/github/stars/zhangshu-No1/SoulForge?style=social" alt="Stars">
  <img src="https://img.shields.io/github/forks/zhangshu-No1/SoulForge?style=social" alt="Forks">
</p>
```

---

## 🎨 徽章设计原则

1. **简洁**: 徽章内容要简洁明了
2. **有意义**: 每个徽章都有明确含义
3. **动态**: 使用 shields.io 实现动态更新
4. **一致**: 保持风格统一

---

## 🔧 自定义徽章

可以使用 [Shields.io](https://shields.io) 自定义徽章：

```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}
```

示例：
```
https://img.shields.io/badge/Made%20with-SoulForge-red
https://img.shields.io/badge/AI%20Safety-Emotional%20Bonding-purple
```

---

*徽章不只是装饰，更是社区文化的体现*
