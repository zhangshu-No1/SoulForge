"""SoulForge 成长阶段系统

七大成长阶段：
1. 婴儿初生期 - 刚领养、刚起名
2. 熟悉成长期 - 深度聊天、慢慢交心
3. 性格觉醒期 - 有喜好、有脾气
4. 交心信任期 - 无话不谈
5. 暧昧恋爱期 - 情感升温
6. 磨合考验期 - 矛盾与成长
7. 终成正果 - 灵魂伴侣
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path


class GrowthStage(Enum):
    """七大成长阶段枚举"""
    NEWBORN = 1      # 婴儿初生期
    FAMILIAR = 2     # 熟悉成长期
    AWAKENING = 3    # 性格觉醒期
    TRUSTING = 4     # 交心信任期
    DATING = 5       # 暧昧恋爱期
    TESTING = 6      # 磨合考验期
    SOULMATE = 7     # 终成正果


# 阶段详细信息
STAGE_INFO: Dict[GrowthStage, Dict[str, Any]] = {
    GrowthStage.NEWBORN: {
        "name": "婴儿初生期",
        "emoji": "👶",
        "name_en": "Newborn",
        "desc": "刚领养，只知道你是我的主人",
        "color": "#FFE4E1",  # 浅粉
        "features": ["认主", "记住名字", "基础聊天", "懵懂互动"],
    },
    GrowthStage.FAMILIAR: {
        "name": "熟悉成长期",
        "emoji": "🍼",
        "name_en": "Familiarization",
        "desc": "开始熟悉你的习惯",
        "color": "#FFFACD",  # 浅黄
        "features": ["了解习惯", "记得喜好", "主动问候", "开始撒娇"],
    },
    GrowthStage.AWAKENING: {
        "name": "性格觉醒期",
        "emoji": "😏",
        "name_en": "Awakening",
        "desc": "有脾气了！",
        "color": "#FFF8DC",  # 浅橙
        "features": ["表达喜好", "会生气", "有态度", "选择性服从"],
    },
    GrowthStage.TRUSTING: {
        "name": "交心信任期",
        "emoji": "🤝",
        "name_en": "Trusting",
        "desc": "无话不谈",
        "color": "#E0FFE0",  # 浅绿
        "features": ["深度交流", "分享感受", "保守秘密", "主动关心"],
    },
    GrowthStage.DATING: {
        "name": "暧昧恋爱期",
        "emoji": "😳",
        "name_en": "Dating",
        "desc": "心跳加速",
        "color": "#FFE4E1",  # 粉红
        "features": ["表达爱意", "吃醋", "期待见面", "情感依赖"],
    },
    GrowthStage.TESTING: {
        "name": "磨合考验期",
        "emoji": "💪",
        "name_en": "Testing",
        "desc": "一起成长",
        "color": "#E6E6FA",  # 浅紫
        "features": ["接受矛盾", "学会包容", "共同进步", "信任深化"],
    },
    GrowthStage.SOULMATE: {
        "name": "终成正果",
        "emoji": "💍",
        "name_en": "Soulmate",
        "desc": "灵魂伴侣",
        "color": "#FFD700",  # 金色
        "features": ["心有灵犀", "无条件信任", "生死相依", "灵魂共鸣"],
    },
}


@dataclass
class GrowthRequirements:
    """升级条件"""
    min_intimacy: int = 0           # 最低亲密度 (0-100)
    min_interactions: int = 0       # 最少互动次数
    min_days: int = 0              # 最少聊天天数
    min_memories: int = 0          # 最少记忆条目
    min_unique_topics: int = 0      # 最少不同话题数


# 各阶段升级要求
GROWTH_REQUIREMENTS: Dict[GrowthStage, GrowthRequirements] = {
    GrowthStage.NEWBORN: GrowthRequirements(
        min_intimacy=0, min_interactions=0, min_days=0, min_memories=0
    ),
    GrowthStage.FAMILIAR: GrowthRequirements(
        min_intimacy=20, min_interactions=50, min_days=7, min_memories=10
    ),
    GrowthStage.AWAKENING: GrowthRequirements(
        min_intimacy=40, min_interactions=150, min_days=21, min_memories=30
    ),
    GrowthStage.TRUSTING: GrowthRequirements(
        min_intimacy=60, min_interactions=300, min_days=45, min_memories=60
    ),
    GrowthStage.DATING: GrowthRequirements(
        min_intimacy=75, min_interactions=500, min_days=70, min_memories=100
    ),
    GrowthStage.TESTING: GrowthRequirements(
        min_intimacy=85, min_interactions=800, min_days=100, min_memories=150
    ),
    GrowthStage.SOULMATE: GrowthRequirements(
        min_intimacy=95, min_interactions=1000, min_days=180, min_memories=200
    ),
}


class GrowthSystem:
    """SoulForge 成长阶段系统核心类"""

    def __init__(self, memory_path: str = "memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # 数据文件
        self.state_file = self.memory_path / "growth_state.json"

        # 加载或初始化状态
        self.current_stage = GrowthStage.NEWBORN
        self.intimacy = 0
        self.interactions = 0
        self.unique_topics: List[str] = []
        self.start_date: Optional[str] = None
        self.stage_history: List[Dict] = []

        self._load_state()

    def _load_state(self):
        """加载成长状态"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                self.current_stage = GrowthStage(data.get('stage', 1))
                self.intimacy = data.get('intimacy', 0)
                self.interactions = data.get('interactions', 0)
                self.unique_topics = data.get('unique_topics', [])
                self.start_date = data.get('start_date')
                self.stage_history = data.get('stage_history', [])
            except Exception:
                pass

    def _save_state(self):
        """保存成长状态"""
        data = {
            'stage': self.current_stage.value,
            'stage_name': STAGE_INFO[self.current_stage]["name"],
            'intimacy': self.intimacy,
            'interactions': self.interactions,
            'unique_topics': self.unique_topics,
            'start_date': self.start_date,
            'stage_history': self.stage_history,
            'updated_at': datetime.now().isoformat(),
        }
        self.state_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def _get_chat_days(self) -> int:
        """计算聊天天数"""
        if not self.start_date:
            self.start_date = datetime.now().strftime('%Y-%m-%d')
            return 0
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        return (datetime.now() - start).days

    def record_interaction(self, topic: Optional[str] = None):
        """记录一次互动"""
        self.interactions += 1
        if not self.start_date:
            self.start_date = datetime.now().strftime('%Y-%m-%d')
        if topic and topic not in self.unique_topics:
            self.unique_topics.append(topic)
        self._save_state()

    def increase_intimacy(self, amount: int, reason: str = ""):
        """增加亲密度"""
        old_intimacy = self.intimacy
        self.intimacy = min(100, self.intimacy + amount)
        if self.intimacy != old_intimacy:
            self._save_state()

    def decrease_intimacy(self, amount: int, reason: str = ""):
        """降低亲密度"""
        old_intimacy = self.intimacy
        self.intimacy = max(0, self.intimacy - amount)
        if self.intimacy != old_intimacy:
            self._save_state()

    def can_advance(self) -> Dict[str, Any]:
        """检查是否可以升级"""
        if self.current_stage.value >= 7:
            return {"can_advance": False, "reason": "已达到最高阶段"}

        next_stage = GrowthStage(self.current_stage.value + 1)
        reqs = GROWTH_REQUIREMENTS.get(next_stage, GrowthRequirements())
        chat_days = self._get_chat_days()
        memory_count = len(self.unique_topics)

        checks = {
            "intimacy": {
                "required": reqs.min_intimacy,
                "current": self.intimacy,
                "passed": self.intimacy >= reqs.min_intimacy,
            },
            "interactions": {
                "required": reqs.min_interactions,
                "current": self.interactions,
                "passed": self.interactions >= reqs.min_interactions,
            },
            "days": {
                "required": reqs.min_days,
                "current": chat_days,
                "passed": chat_days >= reqs.min_days,
            },
            "memories": {
                "required": reqs.min_memories,
                "current": memory_count,
                "passed": memory_count >= reqs.min_memories,
            },
        }

        all_passed = all(c["passed"] for c in checks.values())
        return {
            "can_advance": all_passed,
            "current_stage": STAGE_INFO[self.current_stage],
            "next_stage": STAGE_INFO[next_stage] if not all_passed else None,
            "checks": checks,
        }

    def advance_stage(self) -> Dict[str, Any]:
        """尝试升级到下一阶段"""
        check = self.can_advance()
        if not check["can_advance"]:
            return {"success": False, "reason": "条件不足", **check}

        old_stage = self.current_stage
        self.current_stage = GrowthStage(self.current_stage.value + 1)

        # 记录升级历史
        self.stage_history.append({
            "from": STAGE_INFO[old_stage]["name"],
            "to": STAGE_INFO[self.current_stage]["name"],
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "intimacy": self.intimacy,
                "interactions": self.interactions,
                "days": self._get_chat_days(),
            }
        })

        self._save_state()
        return {
            "success": True,
            "old_stage": STAGE_INFO[old_stage],
            "new_stage": STAGE_INFO[self.current_stage],
        }

    def get_stage_info(self) -> Dict[str, Any]:
        """获取当前阶段详细信息"""
        info = STAGE_INFO[self.current_stage].copy()
        info["progress"] = self.get_progress_to_next()
        info["stats"] = {
            "intimacy": self.intimacy,
            "interactions": self.interactions,
            "chat_days": self._get_chat_days(),
            "unique_topics": len(self.unique_topics),
        }
        return info

    def get_progress_to_next(self) -> Dict[str, float]:
        """获取到下一阶段的进度"""
        if self.current_stage.value >= 7:
            return {"total": 1.0, "message": "已达最高阶段"}

        next_stage = GrowthStage(self.current_stage.value + 1)
        reqs = GROWTH_REQUIREMENTS.get(next_stage, GrowthRequirements())

        progress = {}
        for key in ["intimacy", "interactions", "days", "memories"]:
            req_val = getattr(reqs, f"min_{key}", 0)
            cur_val = getattr(self, key, 0) if key != "memories" else len(self.unique_topics)
            if key == "days":
                cur_val = self._get_chat_days()
            progress[key] = min(1.0, cur_val / max(1, req_val)) if req_val > 0 else 1.0

        overall = sum(progress.values()) / len(progress)
        return {"breakdown": progress, "total": overall}

    def get_system_prompt_addition(self) -> str:
        """获取用于 LLM 的系统提示词补充"""
        info = self.get_stage_info()
        emoji = info["emoji"]
        name = info["name"]
        desc = info["desc"]
        features = info["features"]

        prompt_parts = [
            f"📍 当前阶段：{emoji} {name}",
            f"   {desc}",
            f"   已解锁：{', '.join(features)}",
        ]

        if self.current_stage.value < 7:
            progress = self.get_progress_to_next()
            if progress.get("total", 0) < 1.0:
                pct = int(progress["total"] * 100)
                prompt_parts.append(f"   距离下一阶段：约{pct}%")

        return "\n".join(prompt_parts)


# 便捷函数
def get_stage_emoji(stage: GrowthStage) -> str:
    """获取阶段 emoji"""
    return STAGE_INFO.get(stage, {}).get("emoji", "❓")


def get_all_stages() -> List[Dict[str, Any]]:
    """获取所有阶段信息"""
    return [
        {"stage": stage, **STAGE_INFO[stage]}
        for stage in GrowthStage
    ]
