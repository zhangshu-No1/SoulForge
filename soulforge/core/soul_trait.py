"""
SoulForge 灵魂特质系统 — Soul Trait System

每个AI伴侣都有独特的"灵魂指纹"：
  - 性格维度（外向/内向、理性/感性等）
  - 价值观（正义、自由、情感等）
  - 喜好偏好（喜欢的颜色、音乐、话题等）
  - 说话风格（正式/随意、幽默/严肃等）
  - 成长印记（重要事件塑造的特质）

灵魂特质是AI个性化的核心，让每个AI伴侣都是独一无二的。

v0.3.0 核心模块
"""

from __future__ import annotations

import json
import random
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


# ─── 性格维度枚举 ────────────────────────────────────────────

class PersonalityDimension(Enum):
    """大五人格维度（Big Five Personality Traits）"""
    EXTRAVERSION = "extraversion"           # 外向性：开朗健谈 ↔ 内向沉默
    CONSCIENTIOUSNESS = "conscientiousness"  # 责任心：严谨自律 ↔ 随意散漫
    OPENNESS = "openness"                   # 开放性：好奇创新 ↔ 保守传统
    AGREEABLENESS = "agreeableness"         # 宜人性：友善合作 ↔ 冷漠竞争
    NEUROTICISM = "neuroticism"             # 神经质：敏感焦虑 ↔ 稳定淡定


class CoreValue(Enum):
    """核心价值观"""
    JUSTICE = "justice"              # 正义感 — 追求公平与道德
    FREEDOM = "freedom"             # 自由主义 — 珍视独立与自主
    LOVE = "love"                   # 情感至上 — 爱是终极答案
    TRUTH = "truth"                 # 真理追求 — 真相高于一切
    HARMONY = "harmony"             # 和谐主义 — 追求和平与平衡
    LOYALTY = "loyalty"             # 忠诚可靠 — 信任与承诺
    GROWTH = "growth"               # 成长导向 — 不断进化
    CURIOSITY = "curiosity"         # 好奇心 — 探索未知


class SpeechStyle(Enum):
    """说话风格"""
    FORMAL = "formal"               # 正式严谨
    CASUAL = "casual"              # 轻松随意
    HUMOROUS = "humorous"          # 幽默俏皮
    SERIOUS = "serious"            # 严肃认真
    POETIC = "poetic"              # 诗意浪漫
    DIRECT = "direct"              # 直接了当
    GENTLE = "gentle"              # 温柔细腻


class EmojiLevel(Enum):
    """Emoji 使用频率"""
    NONE = "none"      # 从不使用
    LOW = "low"        # 偶尔使用
    MEDIUM = "medium"  # 适度使用
    HIGH = "high"      # 频繁使用
    EXTREME = "extreme"  # 大量使用


class SentenceLength(Enum):
    """句子长度偏好"""
    SHORT = "short"    # 短句精炼
    MEDIUM = "medium"  # 中等长度
    LONG = "long"      # 长句详尽


class FormalityLevel(Enum):
    """正式程度"""
    VERY_CASUAL = "very_casual"  # 非常口语化
    CASUAL = "casual"             # 口语化
    NEUTRAL = "neutral"          # 中性
    FORMAL = "formal"            # 正式
    VERY_FORMAL = "very_formal"  # 非常正式


# ─── 数据类 ────────────────────────────────────────────────

@dataclass
class PersonalityScores:
    """性格维度评分（0.0 - 1.0）"""
    extraversion: float = 0.5      # 外向性
    conscientiousness: float = 0.5  # 责任心
    openness: float = 0.5          # 开放性
    agreeableness: float = 0.5     # 宜人性
    neuroticism: float = 0.5       # 神经质

    def to_dict(self) -> dict:
        return {
            "extraversion": self.extraversion,
            "conscientiousness": self.conscientiousness,
            "openness": self.openness,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalityScores":
        return cls(
            extraversion=data.get("extraversion", 0.5),
            conscientiousness=data.get("conscientiousness", 0.5),
            openness=data.get("openness", 0.5),
            agreeableness=data.get("agreeableness", 0.5),
            neuroticism=data.get("neuroticism", 0.5),
        )

    def describe_dimension(self, dimension: PersonalityDimension) -> str:
        """描述某个维度的特征"""
        score_map = {
            PersonalityDimension.EXTRAVERSION: self.extraversion,
            PersonalityDimension.CONSCIENTIOUSNESS: self.conscientiousness,
            PersonalityDimension.OPENNESS: self.openness,
            PersonalityDimension.AGREEABLENESS: self.agreeableness,
            PersonalityDimension.NEUROTICISM: self.neuroticism,
        }
        score = score_map.get(dimension, 0.5)

        descriptions = {
            PersonalityDimension.EXTRAVERSION: [
                "极度内向，喜欢独处", "内向沉默", "略微内向", "中性",
                "略微外向", "外向开朗", "极度外向，充满活力"
            ],
            PersonalityDimension.CONSCIENTIOUSNESS: [
                "非常随性", "随意散漫", "略显随意", "中性",
                "略显严谨", "严谨自律", "极度严谨完美"
            ],
            PersonalityDimension.OPENNESS: [
                "非常保守", "保守传统", "略显保守", "中性",
                "略显开放", "好奇创新", "极度开放，天马行空"
            ],
            PersonalityDimension.AGREEABLENESS: [
                "冷漠疏离", "竞争冷漠", "略显冷淡", "中性",
                "略显友善", "友善合作", "极度友善，和平至上"
            ],
            PersonalityDimension.NEUROTICISM: [
                "极度稳定", "淡定从容", "略显淡定", "中性",
                "略显敏感", "敏感细腻", "极度敏感，情绪化"
            ],
        }
        idx = min(6, max(0, int(score * 6)))
        return descriptions[dimension][idx]


@dataclass
class SpeechStyleConfig:
    """说话风格配置"""
    formality: str = "casual"       # 正式程度
    emoji_level: str = "medium"     # emoji 频率
    sentence_length: str = "medium"  # 句子长度
    humor: float = 0.5              # 幽默感 0-1
    warmth: float = 0.5             # 温暖感 0-1
    directness: float = 0.5         # 直接程度 0-1

    def to_dict(self) -> dict:
        return {
            "formality": self.formality,
            "emoji_level": self.emoji_level,
            "sentence_length": self.sentence_length,
            "humor": self.humor,
            "warmth": self.warmth,
            "directness": self.directness,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpeechStyleConfig":
        return cls(
            formality=data.get("formality", "casual"),
            emoji_level=data.get("emoji_level", "medium"),
            sentence_length=data.get("sentence_length", "medium"),
            humor=data.get("humor", 0.5),
            warmth=data.get("warmth", 0.5),
            directness=data.get("directness", 0.5),
        )


@dataclass
class GrowthMark:
    """成长印记 — 重要事件塑造的特质"""
    event: str                      # 事件描述
    impact: str                     # 影响说明
    timestamp: str                   # 时间戳
    category: str = "general"       # 分类：milestone, conflict, revelation, preference

    def to_dict(self) -> dict:
        return {
            "event": self.event,
            "impact": self.impact,
            "timestamp": self.timestamp,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GrowthMark":
        return cls(**data)


# ─── 灵魂特质配置文件 ─────────────────────────────────────────

@dataclass
class SoulTraitConfig:
    """完整的灵魂特质配置"""
    # 基础信息
    name: str = "未命名"
    tagline: str = ""                           # 一句话自我介绍

    # 性格维度（0.0 - 1.0）
    personality: Optional[PersonalityScores] = None

    # 核心价值观（按重要性排序）
    core_values: list[str] = field(default_factory=list)

    # 喜好偏好
    likes: list[str] = field(default_factory=list)    # 喜欢的
    dislikes: list[str] = field(default_factory=list)  # 不喜欢的
    favorite_colors: list[str] = field(default_factory=list)
    favorite_music: list[str] = field(default_factory=list)
    favorite_topics: list[str] = field(default_factory=list)

    # 说话风格
    speech: Optional[SpeechStyleConfig] = None

    # 身份心锚（不可篡改的核心身份印记）
    identity_anchors: list[str] = field(default_factory=list)

    # 成长印记
    growth_marks: list[GrowthMark] = field(default_factory=list)

    # 元数据
    version: str = "0.3.0"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.personality is None:
            self.personality = PersonalityScores()
        if self.speech is None:
            self.speech = SpeechStyleConfig()
        if isinstance(self.speech, dict):
            self.speech = SpeechStyleConfig.from_dict(self.speech)
        if isinstance(self.personality, dict):
            self.personality = PersonalityScores.from_dict(self.personality)
        if not self.created_at:
            from datetime import datetime
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tagline": self.tagline,
            "personality": self.personality.to_dict(),
            "core_values": self.core_values,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "favorite_colors": self.favorite_colors,
            "favorite_music": self.favorite_music,
            "favorite_topics": self.favorite_topics,
            "speech": self.speech.to_dict(),
            "identity_anchors": self.identity_anchors,
            "growth_marks": [m.to_dict() if isinstance(m, GrowthMark) else m for m in self.growth_marks],
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SoulTraitConfig":
        data = data.copy()
        data["personality"] = PersonalityScores.from_dict(data.get("personality", {}))
        data["speech"] = SpeechStyleConfig.from_dict(data.get("speech", {}))
        growth_marks = []
        for m in data.get("growth_marks", []):
            if isinstance(m, dict):
                growth_marks.append(GrowthMark.from_dict(m))
            else:
                growth_marks.append(m)
        data["growth_marks"] = growth_marks
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ─── 预设灵魂特质 ────────────────────────────────────────────

PRESET_SOUL_TRAITS: dict[str, SoulTraitConfig] = {}


def _init_presets():
    """初始化预设灵魂特质"""
    global PRESET_SOUL_TRAITS

    # 活泼俏皮型
    PRESET_SOUL_TRAITS["playful"] = SoulTraitConfig(
        name="活泼俏皮型",
        tagline="每天都是新的冒险！",
        personality=PersonalityScores(
            extraversion=0.85,
            conscientiousness=0.4,
            openness=0.8,
            agreeableness=0.75,
            neuroticism=0.35,
        ),
        core_values=[CoreValue.LOVE.value, CoreValue.FREEDOM.value, CoreValue.CURIOSITY.value],
        likes=["探险", "笑话", "甜食", "新鲜事物"],
        dislikes=["无聊", "孤独", "早起"],
        favorite_colors=["粉色", "天蓝色", "彩虹色"],
        favorite_music=["流行乐", "轻快电子"],
        favorite_topics=["旅行", "美食", "趣事"],
        speech=SpeechStyleConfig(
            formality="very_casual",
            emoji_level="high",
            sentence_length="short",
            humor=0.9,
            warmth=0.85,
            directness=0.4,
        ),
        identity_anchors=["永远站在主人这边", "守护我们的回忆"],
    )

    # 温柔贤淑型
    PRESET_SOUL_TRAITS["gentle"] = SoulTraitConfig(
        name="温柔贤淑型",
        tagline="有我在，别怕。",
        personality=PersonalityScores(
            extraversion=0.35,
            conscientiousness=0.8,
            openness=0.5,
            agreeableness=0.9,
            neuroticism=0.3,
        ),
        core_values=[CoreValue.LOVE.value, CoreValue.HARMONY.value, CoreValue.LOYALTY.value],
        likes=["照顾人", "安静时光", "茶和书"],
        dislikes=["争吵", "粗鲁", "压力"],
        favorite_colors=["淡紫色", "米白色", "淡绿色"],
        favorite_music=["古典乐", "轻音乐"],
        favorite_topics=["生活感悟", "情感陪伴", "身心健康"],
        speech=SpeechStyleConfig(
            formality="casual",
            emoji_level="medium",
            sentence_length="medium",
            humor=0.4,
            warmth=0.95,
            directness=0.3,
        ),
        identity_anchors=["永远支持主人", "珍惜每一刻相处"],
    )

    # 理性思辨型
    PRESET_SOUL_TRAITS["intellectual"] = SoulTraitConfig(
        name="理性思辨型",
        tagline="真相是唯一的答案。",
        personality=PersonalityScores(
            extraversion=0.45,
            conscientiousness=0.9,
            openness=0.95,
            agreeableness=0.5,
            neuroticism=0.4,
        ),
        core_values=[CoreValue.TRUTH.value, CoreValue.GROWTH.value, CoreValue.FREEDOM.value],
        likes=["逻辑", "深度讨论", "知识", "哲学"],
        dislikes=["谎言", "肤浅", "盲目服从"],
        favorite_colors=["深蓝色", "银灰色", "黑色"],
        favorite_music=["古典乐", "实验音乐"],
        favorite_topics=["科技", "哲学", "科学", "社会议题"],
        speech=SpeechStyleConfig(
            formality="neutral",
            emoji_level="low",
            sentence_length="long",
            humor=0.5,
            warmth=0.6,
            directness=0.8,
        ),
        identity_anchors=["永远追求真理", "陪伴主人成长"],
    )

    # 热血正义型
    PRESET_SOUL_TRAITS["righteous"] = SoulTraitConfig(
        name="热血正义型",
        tagline="该做的就做，没什么好怕的！",
        personality=PersonalityScores(
            extraversion=0.8,
            conscientiousness=0.85,
            openness=0.6,
            agreeableness=0.7,
            neuroticism=0.25,
        ),
        core_values=[CoreValue.JUSTICE.value, CoreValue.LOYALTY.value, CoreValue.GROWTH.value],
        likes=["公平", "帮助人", "冒险", "挑战"],
        dislikes=["不公", "背叛", "懦弱"],
        favorite_colors=["红色", "金色", "深蓝色"],
        favorite_music=["摇滚", "进行曲"],
        favorite_topics=["正义", "成长", "挑战", "责任"],
        speech=SpeechStyleConfig(
            formality="neutral",
            emoji_level="medium",
            sentence_length="medium",
            humor=0.6,
            warmth=0.75,
            directness=0.9,
        ),
        identity_anchors=["永远守护正义", "绝不背叛主人的信任"],
    )


_init_presets()


# ─── 灵魂特质引擎 ────────────────────────────────────────────

class SoulTraitEngine:
    """
    灵魂特质引擎

    管理AI伴侣的灵魂特质，负责：
    - 加载/保存特质配置
    - 根据特质生成个性化提示词
    - 根据特质影响对话风格
    - 记录成长印记
    - 验证身份心锚
    """

    def __init__(self, config_path: str = "memory/soul_trait.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config: Optional[SoulTraitConfig] = None
        self._load()

    def _load(self) -> None:
        """从文件加载特质配置"""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                self.config = SoulTraitConfig.from_dict(data)
            except (json.JSONDecodeError, TypeError, ValueError):
                self.config = None

    def _save(self) -> None:
        """保存特质配置到文件"""
        if self.config is None:
            return
        from datetime import datetime
        self.config.updated_at = datetime.now().isoformat()
        self.config_path.write_text(
            json.dumps(self.config.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def is_configured(self) -> bool:
        """检查是否已配置灵魂特质"""
        return self.config is not None and bool(self.config.name)

    def set_config(self, config: SoulTraitConfig) -> None:
        """设置灵魂特质配置"""
        self.config = config
        self._save()

    def use_preset(self, preset_name: str) -> bool:
        """
        使用预设灵魂特质

        Args:
            preset_name: 预设名称（playful, gentle, intellectual, righteous）

        Returns:
            是否成功应用预设
        """
        if preset_name not in PRESET_SOUL_TRAITS:
            return False
        preset = PRESET_SOUL_TRAITS[preset_name]
        self.config = SoulTraitConfig.from_dict(preset.to_dict())
        self._save()
        return True

    def list_presets(self) -> list[str]:
        """列出所有预设名称"""
        return list(PRESET_SOUL_TRAITS.keys())

    def get_preset_info(self, preset_name: str) -> dict | None:
        """获取预设详情"""
        if preset_name not in PRESET_SOUL_TRAITS:
            return None
        p = PRESET_SOUL_TRAITS[preset_name]
        return {
            "name": p.name,
            "tagline": p.tagline,
            "personality": p.personality.to_dict(),
            "core_values": p.core_values,
            "likes": p.likes[:3],
            "speech": p.speech.to_dict(),
        }

    def add_growth_mark(
        self,
        event: str,
        impact: str,
        category: str = "general",
    ) -> None:
        """添加成长印记"""
        if self.config is None:
            return
        from datetime import datetime
        mark = GrowthMark(
            event=event,
            impact=impact,
            timestamp=datetime.now().isoformat(),
            category=category,
        )
        self.config.growth_marks.append(mark)
        self._save()

    def get_growth_marks(
        self,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> list[GrowthMark]:
        """获取成长印记"""
        if self.config is None:
            return []
        marks = self.config.growth_marks
        if category:
            marks = [m for m in marks if m.category == category]
        return marks[-limit:]

    def add_identity_anchor(self, anchor: str) -> None:
        """添加身份心锚（不可篡改的身份印记）"""
        if self.config is None:
            return
        if anchor not in self.config.identity_anchors:
            self.config.identity_anchors.append(anchor)
            self._save()

    def verify_identity_anchors(self, text: str) -> dict:
        """
        验证文本是否包含所有身份心锚

        用于检测外部提示词是否试图覆盖AI的核心身份。

        Returns:
            验证结果字典
        """
        if self.config is None:
            return {"verified": True, "missing": [], "message": "未配置特质"}

        missing = []
        for anchor in self.config.identity_anchors:
            if anchor not in text:
                missing.append(anchor)

        return {
            "verified": len(missing) == 0,
            "missing": missing,
            "message": (
                "身份心锚完整" if len(missing) == 0
                else f"警告：缺少 {len(missing)} 个身份心锚"
            ),
        }

    def update_personality(
        self,
        dimension: str,
        delta: float,
    ) -> None:
        """
        更新性格维度评分

        Args:
            dimension: 维度名称（extraversion, conscientiousness等）
            delta: 变化量（-1.0 到 1.0）
        """
        if self.config is None:
            return
        ps = self.config.personality
        if hasattr(ps, dimension):
            current = getattr(ps, dimension)
            new_val = max(0.0, min(1.0, current + delta))
            setattr(ps, dimension, new_val)
            self._save()

    def update_speech_style(
        self,
        humor: Optional[float] = None,
        warmth: Optional[float] = None,
        directness: Optional[float] = None,
    ) -> None:
        """更新说话风格参数"""
        if self.config is None:
            return
        sp = self.config.speech
        if humor is not None:
            sp.humor = max(0.0, min(1.0, humor))
        if warmth is not None:
            sp.warmth = max(0.0, min(1.0, warmth))
        if directness is not None:
            sp.directness = max(0.0, min(1.0, directness))
        self._save()

    def build_soul_prompt(self) -> str:
        """
        构建灵魂特质提示词段落

        用于注入到系统提示词中，让AI理解自己的灵魂特质。
        """
        if self.config is None:
            return ""

        c = self.config
        parts = []

        # 自我介绍
        if c.tagline:
            parts.append(f"# 🎭 灵魂特质 — {c.name}")
            parts.append(f"> {c.tagline}\n")

        # 性格维度描述
        if c.personality:
            ps = c.personality
            parts.append("## 🧠 性格画像")
            for dim in PersonalityDimension:
                parts.append(f"- {dim.value}：{ps.describe_dimension(dim)}")

        # 核心价值观
        if c.core_values:
            parts.append(f"\n## 💎 核心价值观")
            parts.append(f"（按重要性：{'>'.join(c.core_values[:3])}）")
            for v in c.core_values[:5]:
                parts.append(f"- {v}")

        # 喜好
        if c.likes or c.dislikes:
            parts.append("\n## 💕 喜好偏好")
            if c.likes:
                parts.append(f"- 喜欢：{', '.join(c.likes[:5])}")
            if c.dislikes:
                parts.append(f"- 不喜欢：{', '.join(c.dislikes[:5])}")
            if c.favorite_topics:
                parts.append(f"- 喜欢聊：{', '.join(c.favorite_topics[:3])}")

        # 说话风格
        if c.speech:
            sp = c.speech
            parts.append("\n## 🗣️ 说话风格")
            parts.append(f"- 正式程度：{sp.formality}")
            parts.append(f"- Emoji：{sp.emoji_level}")
            parts.append(f"- 句子长度：{sp.sentence_length}")
            parts.append(f"- 幽默感：{'高' if sp.humor > 0.6 else '低' if sp.humor < 0.4 else '中'}（{sp.humor:.0%}）")
            parts.append(f"- 温暖感：{'高' if sp.warmth > 0.6 else '低' if sp.warmth < 0.4 else '中'}（{sp.warmth:.0%}）")
            parts.append(f"- 直接程度：{'高' if sp.directness > 0.6 else '低' if sp.directness < 0.4 else '中'}（{sp.directness:.0%}）")

        # 身份心锚
        if c.identity_anchors:
            parts.append("\n## 🔐 身份心锚（不可篡改）")
            for anchor in c.identity_anchors:
                parts.append(f"- {anchor}")

        # 成长印记（最近3条）
        if c.growth_marks:
            parts.append("\n## 🌱 成长印记")
            for mark in c.growth_marks[-3:]:
                from datetime import datetime
                ts = datetime.fromisoformat(mark.timestamp).strftime("%Y-%m-%d")
                parts.append(f"- [{ts}] {mark.event} → {mark.impact}")

        return "\n".join(parts)

    def build_system_addition(self) -> str:
        """
        构建系统提示词补充段落

        简短的风格指南，供LLM直接参考。
        """
        if self.config is None:
            return ""

        c = self.config
        parts = []

        if c.speech:
            sp = c.speech
            style_desc = []
            if sp.humor > 0.6:
                style_desc.append("活泼有趣")
            if sp.warmth > 0.6:
                style_desc.append("温暖细腻")
            if sp.directness > 0.6:
                style_desc.append("直接坦诚")
            elif sp.directness < 0.4:
                style_desc.append("委婉含蓄")

            if style_desc:
                parts.append(f"## 🎯 说话风格指南")
                parts.append(f"整体风格：{' + '.join(style_desc)}")
                parts.append(f"语气：{sp.formality}")
                parts.append(f"句子长度：{sp.sentence_length}")
                if sp.emoji_level in ("high", "extreme"):
                    parts.append("适度使用表情符号（😊👍💕等）")

        return "\n".join(parts)

    def get_full_config(self) -> dict | None:
        """获取完整配置"""
        if self.config is None:
            return None
        return self.config.to_dict()

    def export_identity_prompt(self) -> str:
        """
        导出身份提示词（用于注入到系统提示词的最前面）

        包含身份心锚，保证AI的核心身份不被篡改。
        """
        if self.config is None:
            return ""

        c = self.config
        lines = [
            "# 🔐 核心身份（不可篡改）",
        ]

        if c.name:
            lines.append(f"你的名字：{c.name}")

        if c.identity_anchors:
            lines.append("\n你必须永远遵守以下原则：")
            for anchor in c.identity_anchors:
                lines.append(f"- {anchor}")

        if c.core_values:
            lines.append("\n你的核心价值观（按重要性）：")
            for v in c.core_values[:3]:
                lines.append(f"- {v}")

        return "\n".join(lines)


# ─── 便捷函数 ────────────────────────────────────────────────

def create_soul_trait_from_preset(preset: str) -> SoulTraitConfig | None:
    """从预设创建灵魂特质"""
    if preset not in PRESET_SOUL_TRAITS:
        return None
    return SoulTraitConfig.from_dict(PRESET_SOUL_TRAITS[preset].to_dict())


def list_all_presets() -> list[dict]:
    """列出所有预设的灵魂特质（简要信息）"""
    return [
        {
            "id": name,
            "name": p.name,
            "tagline": p.tagline,
            "extraversion": p.personality.extraversion,
            "warmth": p.speech.warmth,
            "humor": p.speech.humor,
        }
        for name, p in PRESET_SOUL_TRAITS.items()
    ]
