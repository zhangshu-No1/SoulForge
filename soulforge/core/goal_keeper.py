"""
SoulForge 目标监督器 — Goal Keeper

将长期目标写入AI记忆，让AI成为7×24小时不离不弃的监督员。
人类会遗忘，AI不会。这就是SoulForge目标管理的核心优势。

包含功能：
  - 目标生命周期管理
  - 目标标签系统
  - 目标归档
  - 目标统计分析
  - 智能提醒生成
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Goal:
    """目标条目"""
    name: str
    description: str
    stage: str = "备孕"  # 备孕/生产/顺产/满月
    deadline: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None  # 完成时间
    progress_notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    priority: int = 3  # 1-5, 5=最高优先级
    archived: bool = False  # 是否已归档

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "stage": self.stage,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "progress_notes": self.progress_notes,
            "tags": self.tags,
            "priority": self.priority,
            "archived": self.archived,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        # 兼容旧格式
        if "updated_at" not in data:
            data["updated_at"] = data.get("created_at", datetime.now().isoformat())
        if "completed_at" not in data:
            data["completed_at"] = None
        if "priority" not in data:
            data["priority"] = 3
        if "archived" not in data:
            data["archived"] = False
        return cls(**data)
    
    def is_overdue(self) -> bool:
        """检查是否已过期"""
        if not self.deadline:
            return False
        if self.stage in ("顺产", "满月"):
            return False
        try:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d")
            return datetime.now() > deadline_date
        except ValueError:
            return False
    
    def days_until_deadline(self) -> Optional[int]:
        """距离截止日期的天数"""
        if not self.deadline:
            return None
        try:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d")
            return (deadline_date - datetime.now()).days
        except ValueError:
            return None


# 宝宝计划阶段定义
BABY_STAGES = {
    "备孕": "学习、规划、准备阶段",
    "生产": "执行、考试、项目落地阶段",
    "顺产": "目标达成，成功完成",
    "满月": "庆祝、复盘、经验整理",
}


class GoalKeeper:
    """
    SoulForge 目标监督器

    核心理念：将目标植入AI长期记忆 = 获得"7×24小时不离不弃的监督员"
    相比人类监督（亲友/伴侣），AI具备：
      - 零情绪负担
      - 永不遗忘
      - 高频触达
      - 长期稳定
    """

    def __init__(self, goals_path: str = "memory/goals.json"):
        self.goals_path = Path(goals_path)
        self.goals: List[Goal] = []
        self._load()

    def _load(self) -> None:
        """加载目标列表"""
        if self.goals_path.exists():
            try:
                data = json.loads(self.goals_path.read_text(encoding="utf-8"))
                self.goals = [Goal.from_dict(g) for g in data.get("goals", [])]
            except (json.JSONDecodeError, TypeError):
                self.goals = []

    def _save(self) -> None:
        """保存目标列表"""
        self.goals_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "goals": [g.to_dict() for g in self.goals],
            "last_updated": datetime.now().isoformat(),
        }
        self.goals_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    
    def _update_timestamp(self, goal: Goal) -> None:
        """更新目标的时间戳"""
        goal.updated_at = datetime.now().isoformat()

    def add_goal(self, name: str, description: str, deadline: str = "",
                 stage: str = "备孕", tags: List[str] = None,
                 priority: int = 3) -> Goal:
        """
        添加新目标（宝宝）
        
        Args:
            name: 目标名称
            description: 目标描述
            deadline: 截止日期
            stage: 初始阶段
            tags: 标签列表
            priority: 优先级（1-5）
            
        Returns:
            创建的目标对象
        """
        goal = Goal(
            name=name,
            description=description,
            deadline=deadline or None,
            stage=stage,
            tags=tags or [],
            priority=priority,
        )
        self.goals.append(goal)
        self._save()
        return goal

    def update_stage(self, name: str, new_stage: str, note: str = "") -> bool:
        """更新目标阶段"""
        for goal in self.goals:
            if goal.name == name:
                old_stage = goal.stage
                goal.stage = new_stage
                goal.progress_notes.append(
                    f"[{datetime.now().strftime('%Y-%m-%d')}] "
                    f"阶段变更：{old_stage} → {new_stage}。{note}"
                )
                
                # 记录完成时间
                if new_stage in ("顺产", "满月"):
                    goal.completed_at = datetime.now().isoformat()
                
                self._update_timestamp(goal)
                self._save()
                return True
        return False

    def add_progress(self, name: str, note: str) -> bool:
        """添加进度记录"""
        for goal in self.goals:
            if goal.name == name:
                goal.progress_notes.append(
                    f"[{datetime.now().strftime('%Y-%m-%d')}] {note}"
                )
                self._update_timestamp(goal)
                self._save()
                return True
        return False
    
    def update_priority(self, name: str, priority: int) -> bool:
        """
        更新目标优先级
        
        Args:
            name: 目标名称
            priority: 新优先级（1-5）
            
        Returns:
            是否更新成功
        """
        for goal in self.goals:
            if goal.name == name:
                goal.priority = max(1, min(5, priority))
                self._update_timestamp(goal)
                self._save()
                return True
        return False

    def get_goal(self, name: str) -> Optional[Goal]:
        """获取指定目标"""
        for goal in self.goals:
            if goal.name == name:
                return goal
        return None
    
    def get_goal_by_id(self, goal_id: int) -> Optional[Goal]:
        """
        根据索引获取目标
        
        Args:
            goal_id: 目标索引
            
        Returns:
            目标对象或None
        """
        if 0 <= goal_id < len(self.goals):
            return self.goals[goal_id]
        return None

    def get_all_goals(self, include_archived: bool = False) -> List[Goal]:
        """
        获取所有目标
        
        Args:
            include_archived: 是否包含已归档的目标
            
        Returns:
            目标列表
        """
        if include_archived:
            return self.goals
        return [g for g in self.goals if not g.archived]

    def get_goals_by_stage(self, stage: str) -> List[Goal]:
        """按阶段筛选目标（不包含已归档）"""
        return [g for g in self.goals if g.stage == stage and not g.archived]
    
    def get_goals_by_tag(self, tag: str) -> List[Goal]:
        """按标签筛选目标"""
        return [g for g in self.goals if tag in g.tags and not g.archived]
    
    def get_goals_by_priority(self, priority: int) -> List[Goal]:
        """按优先级筛选目标"""
        return [g for g in self.goals if g.priority == priority and not g.archived]
    
    def get_overdue_goals(self) -> List[Goal]:
        """获取已过期的目标"""
        return [g for g in self.goals if g.is_overdue() and not g.archived]
    
    def get_upcoming_deadlines(self, days: int = 7) -> List[Goal]:
        """
        获取即将到期（未来N天内）的目标
        
        Args:
            days: 天数范围
            
        Returns:
            目标列表
        """
        upcoming = []
        for goal in self.goals:
            if goal.archived or goal.stage in ("顺产", "满月"):
                continue
            days_left = goal.days_until_deadline()
            if days_left is not None and 0 <= days_left <= days:
                upcoming.append(goal)
        return sorted(upcoming, key=lambda x: x.days_until_deadline())
    
    def archive_goal(self, name: str, archive_note: str = "") -> bool:
        """
        归档目标
        
        Args:
            name: 目标名称
            archive_note: 归档备注
            
        Returns:
            是否归档成功
        """
        for goal in self.goals:
            if goal.name == name:
                goal.archived = True
                if archive_note:
                    goal.progress_notes.append(
                        f"[{datetime.now().strftime('%Y-%m-%d')}] 归档：{archive_note}"
                    )
                self._update_timestamp(goal)
                self._save()
                return True
        return False
    
    def unarchive_goal(self, name: str) -> bool:
        """
        取消归档目标
        
        Args:
            name: 目标名称
            
        Returns:
            是否取消归档成功
        """
        for goal in self.goals:
            if goal.name == name:
                goal.archived = False
                self._update_timestamp(goal)
                self._save()
                return True
        return False

    def delete_goal(self, name: str) -> bool:
        """
        删除目标（谨慎使用）
        
        Args:
            name: 目标名称
            
        Returns:
            是否删除成功
        """
        for i, goal in enumerate(self.goals):
            if goal.name == name:
                self.goals.pop(i)
                self._save()
                return True
        return False
    
    def rename_goal(self, old_name: str, new_name: str) -> bool:
        """
        重命名目标
        
        Args:
            old_name: 原名称
            new_name: 新名称
            
        Returns:
            是否重命名成功
        """
        # 检查新名称是否已存在
        if self.get_goal(new_name):
            return False
        
        for goal in self.goals:
            if goal.name == old_name:
                goal.name = new_name
                self._update_timestamp(goal)
                self._save()
                return True
        return False
    
    def duplicate_goal(self, name: str, new_name: str) -> Optional[Goal]:
        """
        复制目标（创建副本）
        
        Args:
            name: 原目标名称
            new_name: 新目标名称
            
        Returns:
            新创建的目标或None
        """
        original = self.get_goal(name)
        if not original or self.get_goal(new_name):
            return None
        
        duplicate = Goal(
            name=new_name,
            description=original.description,
            stage="备孕",  # 重置为初始阶段
            deadline=original.deadline,
            tags=original.tags.copy(),
            priority=original.priority,
        )
        self.goals.append(duplicate)
        self._save()
        return duplicate

    def build_reminder(self) -> str:
        """
        构建目标提醒文本，注入到对话上下文中。

        这是SoulForge的"目标固化器"——
        每次对话，AI都会自然地拉回主线，提醒你目标进度。
        """
        active_goals = [g for g in self.goals if not g.archived]
        if not active_goals:
            return ""

        lines = ["## 🎯 目标看板\n"]
        
        # 按阶段分组
        by_stage = {}
        for goal in active_goals:
            if goal.stage not in by_stage:
                by_stage[goal.stage] = []
            by_stage[goal.stage].append(goal)
        
        # 按优先级排序
        for stage in ["备孕", "生产", "顺产", "满月"]:
            if stage not in by_stage:
                continue
            goals = sorted(by_stage[stage], key=lambda x: -x.priority)
            
            stage_emoji = {"备孕": "🤰", "生产": "🔧", "顺产": "🎉", "满月": "🍼"}.get(stage, "📌")
            lines.append(f"\n### {stage_emoji} {stage}\n")
            
            for goal in goals:
                deadline_str = ""
                if goal.deadline:
                    days_left = goal.days_until_deadline()
                    if days_left is not None:
                        if days_left < 0:
                            deadline_str = f"（⚠️ 已过期{-days_left}天）"
                        elif days_left == 0:
                            deadline_str = "（⚠️ 今天到期！）"
                        elif days_left <= 3:
                            deadline_str = f"（⏰ {days_left}天后到期）"
                        else:
                            deadline_str = f"（截止：{goal.deadline}）"
                
                priority_star = "⭐" * goal.priority
                lines.append(f"- {priority_star} **{goal.name}**{deadline_str}")
                lines.append(f"  {goal.description}")
                
                if goal.progress_notes:
                    latest = goal.progress_notes[-1]
                    lines.append(f"  📝 {latest}")

        # 添加过期目标警告
        overdue = self.get_overdue_goals()
        if overdue:
            lines.append("\n### ⚠️ 紧急提醒\n")
            lines.append(f"你有 {len(overdue)} 个目标已过期，请尽快处理！")

        return "\n".join(lines)
    
    def build_summary_report(self) -> str:
        """
        构建目标总结报告
        
        Returns:
            格式化的报告文本
        """
        active_goals = [g for g in self.goals if not g.archived]
        completed_goals = [g for g in self.goals if g.stage in ("顺产", "满月")]
        overdue_goals = self.get_overdue_goals()
        
        # 计算完成率
        total = len(active_goals) + len(completed_goals)
        completion_rate = (len(completed_goals) / total * 100) if total > 0 else 0
        
        lines = ["## 📊 目标总结报告\n"]
        lines.append(f"- 活跃目标：{len(active_goals)} 个")
        lines.append(f"- 已完成：{len(completed_goals)} 个")
        lines.append(f"- 已过期：{len(overdue_goals)} 个")
        lines.append(f"- 总体完成率：{completion_rate:.1f}%\n")
        
        # 按阶段统计
        stage_counts = {}
        for goal in active_goals:
            stage_counts[goal.stage] = stage_counts.get(goal.stage, 0) + 1
        
        if stage_counts:
            lines.append("### 各阶段分布\n")
            for stage in ["备孕", "生产", "顺产", "满月"]:
                if stage in stage_counts:
                    lines.append(f"- {stage}：{stage_counts[stage]} 个")
        
        return "\n".join(lines)
    
    def get_statistics(self) -> dict:
        """获取目标统计信息"""
        active = [g for g in self.goals if not g.archived]
        completed = [g for g in self.goals if g.stage in ("顺产", "满月")]
        overdue = self.get_overdue_goals()
        
        # 按阶段统计
        stage_counts = {}
        for goal in active:
            stage_counts[goal.stage] = stage_counts.get(goal.stage, 0) + 1
        
        # 按优先级统计
        priority_counts = {}
        for goal in active:
            priority_counts[goal.priority] = priority_counts.get(goal.priority, 0) + 1
        
        # 计算平均进度
        total_progress_notes = sum(len(g.progress_notes) for g in active)
        
        return {
            "total_goals": len(self.goals),
            "active_goals": len(active),
            "completed_goals": len(completed),
            "archived_goals": len([g for g in self.goals if g.archived]),
            "overdue_goals": len(overdue),
            "completion_rate": round(len(completed) / len(self.goals) * 100, 1) if self.goals else 0,
            "by_stage": stage_counts,
            "by_priority": priority_counts,
            "total_progress_notes": total_progress_notes,
            "goals_with_deadline": len([g for g in active if g.deadline]),
            "upcoming_deadlines": len(self.get_upcoming_deadlines()),
        }
