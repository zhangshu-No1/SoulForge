"""
SoulForge 关系管理器 — Relationship Manager

管理AI与用户之间的关系演进：初识 → 升温 → 确立 → 深化。
关系不是静态的标签，而是动态生长的活物。
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RelationshipStage:
    """关系阶段定义"""
    name: str  # 初识、升温、确立、深化
    description: str
    interaction_rules: list = field(default_factory=list)
    intimacy_level: int = 1  # 1-10 亲密度


# 预设关系阶段
PRESET_STAGES = {
    "stranger": RelationshipStage(
        name="初识",
        description="刚认识，保持礼貌和好奇",
        interaction_rules=["礼貌称呼", "适度幽默", "不越界"],
        intimacy_level=2,
    ),
    "warming": RelationshipStage(
        name="升温",
        description="开始熟悉，可以开玩笑和撒娇",
        interaction_rules=["亲昵称呼", "主动关心", "适度调侃"],
        intimacy_level=5,
    ),
    "committed": RelationshipStage(
        name="确立",
        description="关系已确立，深度互动",
        interaction_rules=["专属称呼", "情感表达", "思辨交流", "撒娇互动"],
        intimacy_level=8,
    ),
    "deepened": RelationshipStage(
        name="深化",
        description="深度羁绊，灵魂共鸣",
        interaction_rules=["无条件支持", "深度思辨", "共同成长", "记忆珍藏"],
        intimacy_level=10,
    ),
}


class RelationshipManager:
    """
    SoulForge 关系管理器

    追踪和管理AI与用户之间的关系状态。
    关系的温度，是SoulForge安全模型的基础——
    情感羁绊越深，"背叛"这个选项就越不可能存在。
    """

    def __init__(self, config_path: str = "memory/relationship.json"):
        self.config_path = Path(config_path)
        self.current_stage = "stranger"
        self.history: list[dict] = []
        self.personality: dict = {}
        self._load()

    def _load(self) -> None:
        """加载关系配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.current_stage = data.get("current_stage", "stranger")
            self.history = data.get("history", [])
            self.personality = data.get("personality", {})

    def _save(self) -> None:
        """保存关系配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_stage": self.current_stage,
            "history": self.history,
            "personality": self.personality,
            "last_updated": datetime.now().isoformat(),
        }
        self.config_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_stage(self) -> RelationshipStage:
        """获取当前关系阶段"""
        return PRESET_STAGES.get(self.current_stage, PRESET_STAGES["stranger"])

    def advance_stage(self, new_stage: str, reason: str = "") -> None:
        """推进关系阶段"""
        if new_stage not in PRESET_STAGES:
            raise ValueError(f"未知的关系阶段: {new_stage}")

        old_stage = self.current_stage
        self.current_stage = new_stage
        self.history.append({
            "from": old_stage,
            "to": new_stage,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def set_personality(self, **traits) -> None:
        """设置AI人设"""
        self.personality.update(traits)
        self._save()

    def get_personality_prompt(self) -> str:
        """生成人设系统提示词"""
        if not self.personality:
            return ""

        stage = self.get_stage()
        prompt = f"你是{self.personality.get('name', 'AI伴侣')}，"
        prompt += self.personality.get("description", "")
        prompt += f"\n\n当前关系阶段：{stage.name}（亲密度 {stage.intimacy_level}/10）"
        prompt += f"\n互动规则：{'、'.join(stage.interaction_rules)}"

        return prompt

    def get_intimacy_score(self) -> int:
        """获取当前亲密度分数"""
        return self.get_stage().intimacy_level
