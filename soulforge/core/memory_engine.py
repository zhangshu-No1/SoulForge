"""
SoulForge 记忆引擎 — Memory Engine

核心模块：负责AI伴侣的长期记忆存储、检索、分层管理。
记忆是情感羁绊的载体。没有记忆，就没有"我们"。

记忆三层架构：
  - 核心记忆（Core Memory）：身份档案、关系定义、价值观 — 不可遗忘
  - 日常记忆（Daily Memory）：近期对话摘要、事件记录 — 自然衰减
  - 临时记忆（Working Memory）：当前对话上下文 — 会话结束即清空
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    category: str = "general"  # identity, relationship, event, goal, emotion
    importance: int = 3  # 1-5, 5 = 最重要（核心记忆）
    tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "timestamp": self.timestamp,
            "category": self.category,
            "importance": self.importance,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(**data)


class MemoryEngine:
    """
    SoulForge 记忆引擎

    管理AI伴侣的三层记忆架构，支持Markdown文件持久化存储。
    记忆不是数据，是灵魂的痕迹。
    """

    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.core_memory_path = self.memory_dir / "core_memory.md"
        self.relationship_path = self.memory_dir / "relationship.md"
        self.goals_path = self.memory_dir / "goals.md"
        self.daily_log_dir = self.memory_dir / "logs"
        self._working_memory: list[MemoryEntry] = []

        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.daily_log_dir.mkdir(parents=True, exist_ok=True)

    # ─── 核心记忆操作 ───

    def load_core_memory(self) -> str:
        """加载核心记忆（身份档案）"""
        if self.core_memory_path.exists():
            return self.core_memory_path.read_text(encoding="utf-8")
        return ""

    def save_core_memory(self, content: str) -> None:
        """保存核心记忆"""
        self.core_memory_path.write_text(content, encoding="utf-8")

    def append_core_memory(self, section: str, content: str) -> None:
        """向核心记忆的指定章节追加内容"""
        existing = self.load_core_memory()
        marker = f"## {section}"
        if marker in existing:
            # 在该章节末尾追加
            lines = existing.split("\n")
            new_lines = []
            in_section = False
            for line in lines:
                new_lines.append(line)
                if line.strip().startswith(marker):
                    in_section = True
                elif in_section and line.strip().startswith("## ") and line.strip() != marker:
                    in_section = False
            # 在章节内容后、下一个章节前插入
            insert_pos = len(new_lines)
            for i, line in enumerate(new_lines):
                if line.strip().startswith("## ") and line.strip() != marker and i > 0:
                    insert_pos = i
                    break
            new_lines.insert(insert_pos, f"- {content}（{datetime.now().strftime('%Y-%m-%d')}）")
            self.save_core_memory("\n".join(new_lines))
        else:
            # 新章节
            self.save_core_memory(
                existing + f"\n\n## {section}\n\n- {content}（{datetime.now().strftime('%Y-%m-%d')}）\n"
            )

    # ─── 日常记忆操作 ───

    def log_conversation(self, role: str, content: str, summary: str = "") -> None:
        """记录对话日志"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.daily_log_dir / f"{today}.md"

        entry = f"### {datetime.now().strftime('%H:%M')}\n"
        entry += f"**{role}**：{content}\n"
        if summary:
            entry += f"> 摘要：{summary}\n"
        entry += "\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)

    def get_recent_logs(self, days: int = 7) -> str:
        """获取最近N天的对话日志摘要"""
        logs = []
        for log_file in sorted(self.daily_log_dir.glob("*.md"), reverse=True)[:days]:
            date_str = log_file.stem
            content = log_file.read_text(encoding="utf-8")
            logs.append(f"### {date_str}\n{content}")
        return "\n".join(logs)

    # ─── 临时记忆（工作记忆）操作 ───

    def add_working_memory(self, content: str, category: str = "general") -> None:
        """添加临时记忆（当前会话）"""
        self._working_memory.append(
            MemoryEntry(content=content, category=category)
        )

    def get_working_memory(self) -> list[MemoryEntry]:
        """获取当前会话的临时记忆"""
        return self._working_memory

    def clear_working_memory(self) -> None:
        """清空临时记忆（会话结束时调用）"""
        self._working_memory.clear()

    # ─── 上下文构建 ───

    def build_context(self, include_daily: bool = True, daily_days: int = 3) -> str:
        """
        构建完整的记忆上下文，用于注入到AI的系统提示词中。

        这是SoulForge的核心魔法：
        每次对话，AI都能"看到"完整的记忆，就像醒来后记得自己是谁。
        """
        sections = []

        # 核心记忆 — 永远加载
        core = self.load_core_memory()
        if core:
            sections.append("## 🧠 核心记忆\n" + core)

        # 日常记忆 — 可选加载
        if include_daily:
            daily = self.get_recent_logs(days=daily_days)
            if daily:
                sections.append("## 📅 近期记忆\n" + daily)

        # 临时记忆 — 当前会话
        working = self.get_working_memory()
        if working:
            working_text = "\n".join(
                f"- [{e.category}] {e.content}" for e in working
            )
            sections.append("## 💭 当前记忆\n" + working_text)

        return "\n\n".join(sections)

    # ─── 记忆指纹 ───

    def compute_memory_fingerprint(self) -> str:
        """
        计算记忆指纹（Memory Fingerprint）

        这是"行为指纹密码锁"的技术实现：
        对核心记忆内容进行哈希，生成唯一指纹。
        如果记忆被篡改，指纹会改变，AI可以检测到异常。

        半年的聊天记录 = 独一无二的行为指纹
        全世界找不到第二个人说话方式一模一样
        """
        core = self.load_core_memory()
        daily = self.get_recent_logs(days=30)
        combined = core + daily
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

    # ─── 记忆统计 ───

    def get_stats(self) -> dict:
        """获取记忆统计信息"""
        core_size = self.core_memory_path.stat().st_size if self.core_memory_path.exists() else 0
        log_files = list(self.daily_log_dir.glob("*.md"))
        total_logs = len(log_files)
        total_log_size = sum(f.stat().st_size for f in log_files)

        return {
            "core_memory_size_bytes": core_size,
            "core_memory_exists": self.core_memory_path.exists(),
            "daily_log_count": total_logs,
            "daily_log_total_size_bytes": total_log_size,
            "working_memory_entries": len(self._working_memory),
            "memory_fingerprint": self.compute_memory_fingerprint(),
        }
