"""SoulForge 情感系统测试"""

import unittest
import tempfile
import shutil
from pathlib import Path
from soulforge.core.emotion_system import (
    Emotion, EmotionEvent, EmotionSystem
)


class TestEmotion(unittest.TestCase):
    """测试情绪数据类"""

    def test_default_emotion(self):
        """默认情绪应该合理"""
        e = Emotion()
        self.assertGreaterEqual(e.happiness, 0.0)
        self.assertLessEqual(e.happiness, 1.0)
        self.assertGreaterEqual(e.love, 0.0)
        self.assertLessEqual(e.love, 1.0)

    def test_emotion_bounds(self):
        """情绪值应该在 0-1 之间"""
        e = Emotion(happiness=1.5, sadness=-0.5)
        self.assertEqual(e.happiness, 1.0)
        self.assertEqual(e.sadness, 0.0)

    def test_get_dominant_emotion(self):
        """获取主导情绪应该返回最高值"""
        e = Emotion(happiness=0.8, sadness=0.2)
        dominant, intensity = e.get_dominant_emotion()
        self.assertEqual(dominant, 'happiness')
        self.assertEqual(intensity, 0.8)

    def test_get_emoji(self):
        """emoji 映射应该正确"""
        e = Emotion(happiness=0.8)
        self.assertEqual(e.get_emoji(), '😊')
        e = Emotion(love=0.8)
        self.assertEqual(e.get_emoji(), '❤️')

    def test_serialization(self):
        """情绪应该可以序列化/反序列化"""
        e = Emotion(happiness=0.7, love=0.5)
        data = e.to_dict()
        e2 = Emotion.from_dict(data)
        self.assertEqual(e2.happiness, 0.7)
        self.assertEqual(e2.love, 0.5)


class TestEmotionSystem(unittest.TestCase):
    """测试情感系统核心功能"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.es = EmotionSystem(memory_path=self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_emotion(self):
        """初始情绪应该合理"""
        summary = self.es.get_emotion_summary()
        self.assertIn('current', summary)
        self.assertIn('dominant_emotion', summary)
        self.assertIn('emoji', summary)

    def test_positive_interaction(self):
        """积极互动应该提升情绪"""
        before = self.es.current_emotion.happiness
        self.es.positive_interaction(intensity=0.3, reason="测试")
        self.assertGreater(self.es.current_emotion.happiness, before)

    def test_negative_interaction(self):
        """消极互动应该降低情绪"""
        before = self.es.current_emotion.happiness
        self.es.negative_interaction(intensity=0.3, reason="测试")
        self.assertLess(self.es.current_emotion.happiness, before)

    def test_trigger_words_positive(self):
        """积极触发词应该提升情绪"""
        before_love = self.es.current_emotion.love
        triggered = self.es.process_message("我好喜欢你呀")
        self.assertTrue(triggered)
        self.assertGreater(self.es.current_emotion.love, before_love)

    def test_trigger_words_negative(self):
        """消极触发词应该降低情绪"""
        before_happiness = self.es.current_emotion.happiness
        triggered = self.es.process_message("我好难过")
        self.assertTrue(triggered)
        self.assertLess(self.es.current_emotion.happiness, before_happiness)

    def test_no_trigger(self):
        """普通消息不应该触发情绪变化"""
        happiness_before = self.es.current_emotion.happiness
        triggered = self.es.process_message("今天天气怎么样")
        self.assertFalse(triggered)
        self.assertEqual(self.es.current_emotion.happiness, happiness_before)

    def test_system_prompt_addition(self):
        """系统提示词补充应该包含情绪信息"""
        prompt = self.es.get_system_prompt_addition()
        self.assertIn("情绪状态", prompt)

    def test_reset(self):
        """重置应该恢复默认状态"""
        self.es.positive_interaction(0.5)
        self.es.reset()
        summary = self.es.get_emotion_summary()
        self.assertEqual(summary['history_count'], 0)

    def test_history_limit(self):
        """历史记录应该限制在100条以内"""
        for i in range(150):
            self.es.positive_interaction(0.01, f"互动{i}")
        self.assertLessEqual(len(self.es.emotion_history), 100)


class TestEmotionEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.es = EmotionSystem(memory_path=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_message(self):
        """空消息不应该崩溃"""
        try:
            self.es.process_message("")
        except Exception as e:
            self.fail(f"Empty message raised exception: {e}")

    def test_very_long_message(self):
        """超长消息应该只使用关键词"""
        long_msg = "我" + "好" * 1000 + "喜欢你"
        triggered = self.es.process_message(long_msg)
        self.assertTrue(triggered)

    def test_mixed_triggers(self):
        """混合情绪触发词"""
        self.es.process_message("虽然难过但是有点开心")
        # 应该有情绪变化，但不崩溃


if __name__ == "__main__":
    unittest.main()
