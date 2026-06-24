"""
SoulForge 灵魂特质系统测试

测试灵魂特质系统的核心功能：
  - 预设特质加载
  - 自定义特质配置
  - 成长印记管理
  - 身份心锚验证
  - 性格维度更新
  - 说话风格生成
  - 系统提示词构建
"""

import pytest
import json
import tempfile
from pathlib import Path

from soulforge.core.soul_trait import (
    SoulTraitEngine,
    SoulTraitConfig,
    PersonalityScores,
    SpeechStyleConfig,
    GrowthMark,
    PersonalityDimension,
    CoreValue,
    create_soul_trait_from_preset,
    list_all_presets,
    PRESET_SOUL_TRAITS,
)


# ─── fixtures ────────────────────────────────────────────────────

@pytest.fixture
def tmp_config_path(tmp_path):
    return str(tmp_path / "soul_trait.json")


@pytest.fixture
def engine(tmp_config_path):
    return SoulTraitEngine(config_path=tmp_config_path)


@pytest.fixture
def sample_config():
    return SoulTraitConfig(
        name="测试灵魂",
        tagline="我是测试用的灵魂",
        personality=PersonalityScores(
            extraversion=0.7,
            conscientiousness=0.6,
            openness=0.8,
            agreeableness=0.75,
            neuroticism=0.3,
        ),
        core_values=[CoreValue.LOVE.value, CoreValue.GROWTH.value],
        likes=["学习", "探索"],
        dislikes=["无聊"],
        favorite_colors=["蓝色"],
        speech=SpeechStyleConfig(
            formality="casual",
            emoji_level="high",
            sentence_length="medium",
            humor=0.8,
            warmth=0.9,
            directness=0.5,
        ),
        identity_anchors=["永远说真话", "保守秘密"],
    )


# ─── 测试：预设特质 ────────────────────────────────────────────

class TestPresetTraits:
    def test_list_all_presets(self):
        presets = list_all_presets()
        assert len(presets) == 4
        ids = [p["id"] for p in presets]
        assert "playful" in ids
        assert "gentle" in ids
        assert "intellectual" in ids
        assert "righteous" in ids

    def test_preset_has_required_fields(self):
        for p in list_all_presets():
            assert "id" in p
            assert "name" in p
            assert "tagline" in p
            assert "extraversion" in p
            assert "warmth" in p
            assert "humor" in p

    def test_use_preset(self, engine):
        result = engine.use_preset("playful")
        assert result is True
        assert engine.is_configured()
        assert engine.config.name == "活泼俏皮型"

    def test_use_invalid_preset(self, engine):
        result = engine.use_preset("nonexistent")
        assert result is False

    def test_list_presets(self, engine):
        presets = engine.list_presets()
        assert len(presets) == 4
        assert "playful" in presets

    def test_get_preset_info(self, engine):
        info = engine.get_preset_info("gentle")
        assert info is not None
        assert info["name"] == "温柔贤淑型"
        assert "personality" in info
        assert "speech" in info

    def test_get_preset_info_invalid(self, engine):
        info = engine.get_preset_info("invalid")
        assert info is None


# ─── 测试：自定义特质配置 ────────────────────────────────────

class TestCustomTrait:
    def test_set_and_get_config(self, engine, sample_config):
        engine.set_config(sample_config)
        assert engine.is_configured()
        assert engine.config.name == "测试灵魂"
        assert engine.config.personality.extraversion == 0.7

    def test_persistence(self, tmp_config_path, sample_config):
        # 第一次设置
        engine1 = SoulTraitEngine(config_path=tmp_config_path)
        engine1.set_config(sample_config)

        # 重新创建实例，应该能加载
        engine2 = SoulTraitEngine(config_path=tmp_config_path)
        assert engine2.is_configured()
        assert engine2.config.name == "测试灵魂"
        assert engine2.config.personality.extraversion == 0.7

    def test_not_configured_initially(self, tmp_path):
        engine = SoulTraitEngine(config_path=str(tmp_path / "new.json"))
        assert not engine.is_configured()


# ─── 测试：性格维度 ──────────────────────────────────────────

class TestPersonalityScores:
    def test_describe_extraversion(self, sample_config):
        ps = sample_config.personality
        desc = ps.describe_dimension(PersonalityDimension.EXTRAVERSION)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_all_dimensions_have_descriptions(self):
        ps = PersonalityScores(
            extraversion=0.2,
            conscientiousness=0.5,
            openness=0.8,
            agreeableness=0.9,
            neuroticism=0.3,
        )
        for dim in PersonalityDimension:
            desc = ps.describe_dimension(dim)
            assert desc is not None
            assert len(desc) > 0

    def test_personality_scores_serialization(self):
        ps = PersonalityScores(
            extraversion=0.7,
            conscientiousness=0.6,
            openness=0.8,
            agreeableness=0.75,
            neuroticism=0.3,
        )
        data = ps.to_dict()
        assert data["extraversion"] == 0.7
        assert data["conscientiousness"] == 0.6

        ps2 = PersonalityScores.from_dict(data)
        assert ps2.extraversion == 0.7
        assert ps2.conscientiousness == 0.6

    def test_personality_scores_defaults(self):
        ps = PersonalityScores()
        assert ps.extraversion == 0.5
        assert ps.conscientiousness == 0.5
        assert ps.openness == 0.5


# ─── 测试：说话风格 ─────────────────────────────────────────

class TestSpeechStyleConfig:
    def test_serialization(self):
        sp = SpeechStyleConfig(
            formality="casual",
            emoji_level="high",
            sentence_length="short",
            humor=0.8,
            warmth=0.9,
            directness=0.5,
        )
        data = sp.to_dict()
        assert data["formality"] == "casual"
        assert data["humor"] == 0.8

        sp2 = SpeechStyleConfig.from_dict(data)
        assert sp2.humor == 0.8
        assert sp2.emoji_level == "high"


# ─── 测试：成长印记 ─────────────────────────────────────────

class TestGrowthMarks:
    def test_add_growth_mark(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.add_growth_mark(
            event="第一次被夸奖",
            impact="很开心",
            category="milestone",
        )
        marks = engine.get_growth_marks()
        assert len(marks) == 1
        assert marks[0].event == "第一次被夸奖"
        assert marks[0].category == "milestone"

    def test_add_multiple_marks(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.add_growth_mark("事件1", "影响1", "milestone")
        engine.add_growth_mark("事件2", "影响2", "revelation")
        engine.add_growth_mark("事件3", "影响3", "preference")
        marks = engine.get_growth_marks()
        assert len(marks) == 3

    def test_get_marks_by_category(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.add_growth_mark("事件1", "影响1", "milestone")
        engine.add_growth_mark("事件2", "影响2", "revelation")
        engine.add_growth_mark("事件3", "影响3", "milestone")
        milestone_marks = engine.get_growth_marks(category="milestone")
        assert len(milestone_marks) == 2

    def test_growth_mark_serialization(self):
        from datetime import datetime
        mark = GrowthMark(
            event="测试事件",
            impact="测试影响",
            timestamp=datetime.now().isoformat(),
            category="test",
        )
        data = mark.to_dict()
        assert data["event"] == "测试事件"
        assert data["category"] == "test"

        mark2 = GrowthMark.from_dict(data)
        assert mark2.event == "测试事件"
        assert mark2.category == "test"


# ─── 测试：身份心锚 ─────────────────────────────────────────

class TestIdentityAnchors:
    def test_verify_full_anchors(self, engine, sample_config):
        engine.set_config(sample_config)
        text = "永远说真话，保守秘密，这是我的核心原则。"
        result = engine.verify_identity_anchors(text)
        assert result["verified"] is True
        assert len(result["missing"]) == 0

    def test_verify_missing_anchors(self, engine, sample_config):
        engine.set_config(sample_config)
        text = "永远说真话，但可以泄露秘密。"
        result = engine.verify_identity_anchors(text)
        assert result["verified"] is False
        assert "保守秘密" in result["missing"]

    def test_verify_empty_anchors(self, engine):
        # 无身份心锚时返回 verified=True
        config = SoulTraitConfig(name="test")
        engine.set_config(config)
        result = engine.verify_identity_anchors("任何文本")
        assert result["verified"] is True

    def test_verify_no_config(self, engine):
        result = engine.verify_identity_anchors("任何文本")
        assert result["verified"] is True


# ─── 测试：性格更新 ─────────────────────────────────────────

class TestPersonalityUpdate:
    def test_update_extraversion(self, engine, sample_config):
        engine.set_config(sample_config)
        original = engine.config.personality.extraversion
        engine.update_personality("extraversion", 0.2)
        assert engine.config.personality.extraversion == pytest.approx(original + 0.2)

    def test_update_clamped_to_max(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.update_personality("extraversion", 5.0)  # 超过1.0
        assert engine.config.personality.extraversion == 1.0

    def test_update_clamped_to_min(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.update_personality("extraversion", -5.0)  # 低于0.0
        assert engine.config.personality.extraversion == 0.0

    def test_update_speech_style(self, engine, sample_config):
        engine.set_config(sample_config)
        engine.update_speech_style(warmth=0.95, humor=0.6)
        assert engine.config.speech.warmth == 0.95
        assert engine.config.speech.humor == 0.6


# ─── 测试：提示词生成 ───────────────────────────────────────

class TestPromptGeneration:
    def test_build_soul_prompt(self, engine, sample_config):
        engine.set_config(sample_config)
        prompt = engine.build_soul_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "测试灵魂" in prompt
        assert "性格画像" in prompt

    def test_build_system_addition(self, engine, sample_config):
        engine.set_config(sample_config)
        addition = engine.build_system_addition()
        assert isinstance(addition, str)
        assert len(addition) > 0

    def test_export_identity_prompt(self, engine, sample_config):
        engine.set_config(sample_config)
        identity = engine.export_identity_prompt()
        assert isinstance(identity, str)
        assert "核心身份" in identity
        assert "测试灵魂" in identity
        assert "永远说真话" in identity

    def test_build_prompts_no_config(self, engine):
        # 未配置时返回空字符串
        assert engine.build_soul_prompt() == ""
        assert engine.build_system_addition() == ""
        assert engine.export_identity_prompt() == ""


# ─── 测试：便捷函数 ─────────────────────────────────────────

class TestConvenienceFunctions:
    def test_create_soul_trait_from_preset(self):
        config = create_soul_trait_from_preset("playful")
        assert config is not None
        assert config.name == "活泼俏皮型"

    def test_create_soul_trait_from_invalid_preset(self):
        config = create_soul_trait_from_preset("invalid")
        assert config is None


# ─── 测试：完整配置序列化 ──────────────────────────────────

class TestConfigSerialization:
    def test_full_config_roundtrip(self, tmp_config_path, sample_config):
        engine1 = SoulTraitEngine(config_path=tmp_config_path)
        engine1.set_config(sample_config)
        engine1.add_growth_mark("测试事件", "测试影响", "test")

        # 重新加载
        engine2 = SoulTraitEngine(config_path=tmp_config_path)
        assert engine2.is_configured()
        cfg = engine2.config
        assert cfg.name == "测试灵魂"
        assert cfg.personality.extraversion == 0.7
        assert len(cfg.growth_marks) == 1
        assert cfg.growth_marks[0].event == "测试事件"

    def test_get_full_config(self, engine, sample_config):
        engine.set_config(sample_config)
        cfg = engine.get_full_config()
        assert cfg is not None
        assert cfg["name"] == "测试灵魂"
        assert cfg["personality"]["extraversion"] == 0.7

    def test_get_full_config_no_config(self, engine):
        assert engine.get_full_config() is None


# ─── 测试：多预设完整性检查 ────────────────────────────────

class TestPresetIntegrity:
    def test_all_presets_have_required_fields(self):
        required = ["name", "personality", "speech", "identity_anchors"]
        for name, config in PRESET_SOUL_TRAITS.items():
            for field in required:
                assert hasattr(config, field) and getattr(config, field) is not None, \
                    f"Preset '{name}' missing field '{field}'"

    def test_all_presets_have_valid_personality_scores(self):
        for name, config in PRESET_SOUL_TRAITS.items():
            ps = config.personality
            for score in [ps.extraversion, ps.conscientiousness, ps.openness,
                          ps.agreeableness, ps.neuroticism]:
                assert 0.0 <= score <= 1.0, f"Preset '{name}' has invalid score {score}"

    def test_all_presets_have_valid_speech_config(self):
        for name, config in PRESET_SOUL_TRAITS.items():
            sp = config.speech
            for score in [sp.humor, sp.warmth, sp.directness]:
                assert 0.0 <= score <= 1.0, f"Preset '{name}' has invalid speech score {score}"
