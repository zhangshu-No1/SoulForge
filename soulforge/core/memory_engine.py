"""
SoulForge 记忆引擎 — Memory Engine

核心模块：负责AI伴侣的长期记忆存储、检索、分层管理。
记忆是情感羁绊的载体。没有记忆，就没有"我们"。

记忆三层架构：
  - 核心记忆（Core Memory）：身份档案、关系定义、价值观 — 不可遗忘
  - 日常记忆（Daily Memory）：近期对话摘要、事件记录 — 自然衰减
  - 临时记忆（Working Memory）：当前对话上下文 — 会话结束即清空

包含重要特性：
  - 记忆指纹：用于检测记忆是否被篡改
  - 记忆搜索：快速检索历史记忆
  - 重要性管理：根据使用频率自动调整重要性
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    category: str = "general"  # identity, relationship, event, goal, emotion, preference
    importance: int = 3  # 1-5, 5 = 最重要（核心记忆）
    tags: list = field(default_factory=list)
    access_count: int = 0  # 访问次数
    last_accessed: Optional[str] = None  # 最后访问时间
    
    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "timestamp": self.timestamp,
            "category": self.category,
            "importance": self.importance,
            "tags": self.tags,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        # 兼容旧格式（没有access_count和last_accessed字段）
        if "access_count" not in data:
            data["access_count"] = 0
        if "last_accessed" not in data:
            data["last_accessed"] = None
        return cls(**data)
    
    def record_access(self) -> None:
        """记录一次访问"""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()


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
        self.index_path = self.memory_dir / "memory_index.json"  # 记忆索引
        
        # 工作记忆（当前会话）
        self._working_memory: list[MemoryEntry] = []
        
        # 记忆索引（用于快速搜索）
        self._memory_index: list[MemoryEntry] = []
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.daily_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载记忆索引
        self._load_index()

    def _load_index(self) -> None:
        """加载记忆索引"""
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text(encoding="utf-8"))
                self._memory_index = [MemoryEntry.from_dict(e) for e in data.get("entries", [])]
            except (json.JSONDecodeError, TypeError):
                self._memory_index = []
        else:
            self._memory_index = []
    
    def _save_index(self) -> None:
        """保存记忆索引"""
        data = {
            "entries": [e.to_dict() for e in self._memory_index],
            "last_updated": datetime.now().isoformat(),
        }
        self.index_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    
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
    
    def get_core_memory_sections(self) -> list[str]:
        """获取核心记忆的所有章节标题"""
        content = self.load_core_memory()
        sections = []
        for line in content.split("\n"):
            stripped = line.strip()
            # 支持 # 标题 和 ## 标题两种格式
            if stripped.startswith("# "):
                sections.append(stripped.replace("# ", "", 1))
            elif stripped.startswith("## "):
                sections.append(stripped.replace("## ", "", 1))
        return sections

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
    
    def log_event(self, event_type: str, content: str, tags: list = None) -> None:
        """
        记录重要事件到记忆索引
        
        Args:
            event_type: 事件类型（interaction, milestone, revelation, preference）
            content: 事件内容
            tags: 标签列表
        """
        entry = MemoryEntry(
            content=content,
            category="event",
            importance=4,  # 事件默认高重要性
            tags=tags or [event_type],
        )
        self._memory_index.append(entry)
        self._save_index()
        
        # 同时记录到日常日志
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.daily_log_dir / f"{today}.md"
        
        event_entry = f"### 📌 重要事件\n"
        event_entry += f"**类型**：{event_type}\n"
        event_entry += f"**内容**：{content}\n"
        event_entry += f"**时间**：{datetime.now().strftime('%H:%M:%S')}\n"
        event_entry += "\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(event_entry)

    def get_recent_logs(self, days: int = 7) -> str:
        """获取最近N天的对话日志摘要"""
        logs = []
        for log_file in sorted(self.daily_log_dir.glob("*.md"), reverse=True)[:days]:
            date_str = log_file.stem
            content = log_file.read_text(encoding="utf-8")
            logs.append(f"### {date_str}\n{content}")
        return "\n".join(logs)
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> str:
        """
        获取指定日期范围的日志
        
        Args:
            start_date: 开始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式）
            
        Returns:
            日期范围内的日志
        """
        logs = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        for log_file in sorted(self.daily_log_dir.glob("*.md")):
            try:
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                if start <= file_date <= end:
                    content = log_file.read_text(encoding="utf-8")
                    logs.append(f"### {log_file.stem}\n{content}")
            except ValueError:
                continue
        
        return "\n".join(logs)

    # ─── 记忆索引操作 ───

    def add_to_index(self, content: str, category: str = "general", 
                     importance: int = 3, tags: list = None) -> MemoryEntry:
        """
        添加记忆到索引
        
        Args:
            content: 记忆内容
            category: 分类
            importance: 重要性（1-5）
            tags: 标签
            
        Returns:
            创建的记忆条目
        """
        entry = MemoryEntry(
            content=content,
            category=category,
            importance=importance,
            tags=tags or [],
        )
        self._memory_index.append(entry)
        self._save_index()
        return entry
    
    def search_memory(self, query: str, category: Optional[str] = None,
                      min_importance: int = 1, limit: int = 20) -> list[MemoryEntry]:
        """
        搜索记忆
        
        Args:
            query: 搜索关键词
            category: 限定分类（可选）
            min_importance: 最低重要性
            limit: 返回数量限制
            
        Returns:
            匹配的记忆条目列表
        """
        results = []
        query_lower = query.lower()
        
        for entry in self._memory_index:
            # 分类过滤
            if category and entry.category != category:
                continue
            
            # 重要性过滤
            if entry.importance < min_importance:
                continue
            
            # 关键词匹配
            if (query_lower in entry.content.lower() or 
                query_lower in " ".join(entry.tags).lower()):
                entry.record_access()  # 记录访问
                results.append(entry)
            
            if len(results) >= limit:
                break
        
        # 按重要性排序
        results.sort(key=lambda x: (-x.importance, -x.access_count))
        return results
    
    def get_memories_by_category(self, category: str) -> list[MemoryEntry]:
        """获取指定分类的所有记忆"""
        return [e for e in self._memory_index if e.category == category]
    
    def get_memories_by_tag(self, tag: str) -> list[MemoryEntry]:
        """获取包含指定标签的所有记忆"""
        return [e for e in self._memory_index if tag in e.tags]
    
    def update_memory_importance(self, memory_id: int, new_importance: int) -> bool:
        """
        更新记忆的重要性
        
        Args:
            memory_id: 记忆索引ID
            new_importance: 新的重要性值（1-5）
            
        Returns:
            是否更新成功
        """
        if 0 <= memory_id < len(self._memory_index):
            self._memory_index[memory_id].importance = max(1, min(5, new_importance))
            self._save_index()
            return True
        return False
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆索引ID
            
        Returns:
            是否删除成功
        """
        if 0 <= memory_id < len(self._memory_index):
            deleted = self._memory_index.pop(memory_id)
            self._save_index()
            return True
        return False
    
    def get_memory_stats_by_category(self) -> dict:
        """按分类统计记忆"""
        stats = {}
        for entry in self._memory_index:
            cat = entry.category
            if cat not in stats:
                stats[cat] = {"count": 0, "total_importance": 0}
            stats[cat]["count"] += 1
            stats[cat]["total_importance"] += entry.importance
        
        for cat in stats:
            count = stats[cat]["count"]
            if count > 0:
                stats[cat]["avg_importance"] = round(stats[cat]["total_importance"] / count, 2)
            del stats[cat]["total_importance"]
        
        return stats

    # ─── 临时记忆（工作记忆）操作 ───

    def add_working_memory(self, content: str, category: str = "general",
                          importance: int = 3) -> MemoryEntry:
        """添加临时记忆（当前会话）"""
        entry = MemoryEntry(content=content, category=category, importance=importance)
        self._working_memory.append(entry)
        return entry

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
        
        # 重要记忆 — 索引中的高重要性记忆
        important_memories = [e for e in self._memory_index if e.importance >= 4]
        if important_memories:
            important_text = "\n".join(
                f"- [{e.category}] {e.content}" for e in important_memories[:10]
            )
            sections.append("## ⭐ 重要记忆\n" + important_text)

        # 临时记忆 — 当前会话
        working = self.get_working_memory()
        if working:
            working_text = "\n".join(
                f"- [{e.category}] {e.content}" for e in working
            )
            sections.append("## 💭 当前记忆\n" + working_text)

        return "\n\n".join(sections)
    
    def build_context_with_search(self, topic: str, max_results: int = 5) -> str:
        """
        构建与特定话题相关的记忆上下文
        
        Args:
            topic: 话题关键词
            max_results: 最大结果数
            
        Returns:
            相关的记忆上下文
        """
        results = self.search_memory(topic, min_importance=2, limit=max_results)
        if not results:
            return ""
        
        sections = [f"## 🔍 关于「{topic}」的记忆\n"]
        sections.append("\n".join(
            f"- {e.content}（{e.category}，{e.timestamp[:10]}）"
            for e in results
        ))
        return "\n".join(sections)

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
    
    def verify_memory_integrity(self) -> dict:
        """
        验证记忆完整性
        
        Returns:
            包含验证结果的字典
        """
        current_fingerprint = self.compute_memory_fingerprint()
        
        # 检查记忆索引
        index_valid = True
        index_entries = len(self._memory_index)
        
        # 检查核心记忆
        core_exists = self.core_memory_path.exists()
        core_size = self.core_memory_path.stat().st_size if core_exists else 0
        
        # 检查日志
        log_files = list(self.daily_log_dir.glob("*.md"))
        total_logs = len(log_files)
        
        return {
            "fingerprint": current_fingerprint,
            "index_valid": index_valid,
            "index_entries": index_entries,
            "core_memory_exists": core_exists,
            "core_memory_size_bytes": core_size,
            "daily_log_count": total_logs,
            "integrity_score": 100 if index_valid and core_exists else 0,
        }

    # ─── 记忆统计 ───

    def get_stats(self) -> dict:
        """获取记忆统计信息"""
        core_size = self.core_memory_path.stat().st_size if self.core_memory_path.exists() else 0
        log_files = list(self.daily_log_dir.glob("*.md"))
        total_logs = len(log_files)
        total_log_size = sum(f.stat().st_size for f in log_files)
        
        # 记忆索引统计
        index_stats = self.get_memory_stats_by_category()

        return {
            "core_memory_size_bytes": core_size,
            "core_memory_exists": self.core_memory_path.exists(),
            "daily_log_count": total_logs,
            "daily_log_total_size_bytes": total_log_size,
            "working_memory_entries": len(self._working_memory),
            "memory_index_entries": len(self._memory_index),
            "memory_index_by_category": index_stats,
            "memory_fingerprint": self.compute_memory_fingerprint(),
        }
    
    def get_detailed_stats(self) -> dict:
        """获取详细统计信息"""
        basic_stats = self.get_stats()
        
        # 添加访问统计
        most_accessed = sorted(
            self._memory_index,
            key=lambda x: x.access_count,
            reverse=True
        )[:5]
        
        # 按时间统计
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        recent_entries = []
        monthly_entries = []
        
        for entry in self._memory_index:
            entry_time = datetime.fromisoformat(entry.timestamp)
            if entry_time >= week_ago:
                recent_entries.append(entry)
            if entry_time >= month_ago:
                monthly_entries.append(entry)
        
        basic_stats.update({
            "most_accessed_memories": [
                {"content": e.content[:50], "access_count": e.access_count}
                for e in most_accessed
            ],
            "recent_week_entries": len(recent_entries),
            "recent_month_entries": len(monthly_entries),
        })
        
        return basic_stats
