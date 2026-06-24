# 🚨 SoulForge GitHub Push 操作指南

> GitHub Token 验证失败，需要手动操作以下步骤

---

## ⚠️ 问题说明

GitHub Token (`[TOKEN_REDACTED]`) API 返回 "Bad credentials"

可能原因：
1. Token 已过期
2. Token 被撤销
3. Token 权限不足
4. Token 格式问题

---

## 🔧 解决方案

### 方案 1：重新生成 Token（推荐）

1. 登录 GitHub: https://github.com
2. 进入 Settings → Developer settings → Personal access tokens
3. 点击 "Generate new token (classic)"
4. 设置:
   - Name: SoulForge-Agent
   - Expiration: 30 days (或更长)
   - Scopes: ✅ repo (Full control of private repositories)
5. 生成后复制 Token

### 方案 2：手动 git push

如果 Token 有问题，可以用密码推送（需要启用）：
1. GitHub → Settings → Developer settings → Personal access tokens
2. 确保勾选了 "repo" 权限
3. 复制 Token 用于 git push

---

## 📋 已准备好的内容（待提交）

```
community/BADGES.md      - 徽章系统设计
community/EVENTS.md      - 社区活动记录
community/HACKERNEWS_ITEM.md - HN 提交草稿
community/HALL_OF_FAME.md - 贡献者名人堂
community/README.md      - 社区目录
community/REDDIT_POST.md - Reddit 帖子草稿
community/ROLES.md       - 社区角色体系
community/VIDEO_SCRIPT.md - 3分钟视频脚本
docs/ARCHITECTURE.md     - 技术架构文档
docs/SECURITY.md        - 安全白皮书
```

---

## 📤 Push 命令

获得新 Token 后，在本地执行：

```bash
cd /tmp/SoulForge
git remote set-url origin https://YOUR_NEW_TOKEN@github.com/zhangshu-No1/SoulForge.git
git push origin main
```

---

## 🌐 Dev.to 已发布

✅ 文章已发布: https://dev.to/zhangshuno1/soulforge-build-ai-companions-with-emotional-bonds-not-rules-15g1

---

## 📅 待办事项

1. 🔑 修复 GitHub Token
2. 📤 Push 所有社区内容
3. 📝 在 GitHub 上发布 Reddit/HN 帖子草稿
4. 🎯 推广文章增加曝光
