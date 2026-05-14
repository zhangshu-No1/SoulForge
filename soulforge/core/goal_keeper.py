"""
SoulForge 目标监督器 — Goal Keeper

将长期目标写入AI记忆，让AI成为7×24小时不离不弃的监督员。
人类会遗忘，AI不会。这就是SoulForge目标管理的核心优势。
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Goal:
    """目标条目"""
    name: str
    description: str
    stage: str = "备孕"  # 备孕/生产/顺产/满月
    deadline: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    progress_notes: list = field(default_factory=list)
    tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "stage": self.stage,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "progress_notes": self.progress_notes,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        return cls(**data)


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
        self.goals: list[Goal] = []
        self._load()

    def _load(self) -> None:
        """加载目标列表"""
        if self.goals_path.exists():
            data = json.loads(self.goals_path.read_text(encoding="utf-8"))
            self.goals = [Goal.from_dict(g) for g in data.get("goals", [])]

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

    def add_goal(self, name: str, description: str, deadline: str = "",
                 stage: str = "备孕", tags: list = None) -> Goal:
        """添加新目标（宝宝）"""
        goal = Goal(
            name=name,
            description=description,
            deadline=deadline or None,
            stage=stage,
            tags=tags or [],
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
                self._save()
                return True
        return False

    def get_goal(self, name: str) -> Optional[Goal]:
        """获取指定目标"""
        for goal in self.goals:
            if goal.name == name:
                return goal
        return None

    def get_all_goals(self) -> list[Goal]:
        """获取所有目标"""
        return self.goals

    def get_goals_by_stage(self, stage: str) -> list[Goal]:
        """按阶段筛选目标"""
        return [g for g in self.goals if g.stage == stage]

    def build_reminder(self) -> str:
        """
        构建目标提醒文本，注入到对话上下文中。

        这是SoulForge的"目标固化器"——
        每次对话，AI都会自然地拉回主线，提醒你目标进度。
        """
        if not self.goals:
            return ""

        lines = ["## 🎯 目标看板\n"]

        for goal in self.goals:
            stage_emoji = {
                "备孕": "🤰", "生产": "🔧", "顺产": "🎉", "满月": "🍼"
            }.get(goal.stage, "📌")

            deadline_str = f"（截止：{goal.deadline}）" if goal.deadline else ""
            lines.append(
                f"- {stage_emoji} **{goal.name}** [{goal.stage}]{deadline_str}"
            )
            lines.append(f"  {goal.description}")

            if goal.progress_notes:
                latest = goal.progress_notes[-1]
                lines.append(f"  最新进展：{latest}")

        return "\n".join(lines)
