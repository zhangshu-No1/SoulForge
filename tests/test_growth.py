"""SoulForge 成长系统测试"""

import unittest
import tempfile
import shutil
from pathlib import Path
from soulforge.core.growth_system import (
    GrowthStage, GrowthSystem, STAGE_INFO, 
    GROWTH_REQUIREMENTS, get_stage_emoji, get_all_stages
)


class TestGrowthStage(unittest.TestCase):
    """测试成长阶段枚举"""

    def test_stage_count(self):
        """应该有7个阶段"""
        self.assertEqual(len(GrowthStage), 7)

    def test_stage_order(self):
        """阶段应该从1到7"""
        for i, stage in enumerate(GrowthStage, start=1):
            self.assertEqual(stage.value, i)

    def test_stage_info_complete(self):
        """每个阶段都应该有完整信息"""
        for stage in GrowthStage:
            info = STAGE_INFO[stage]
            self.assertIn("name", info)
            self.assertIn("emoji", info)
            self.assertIn("desc", info)
            self.assertIn("features", info)


class TestGrowthRequirements(unittest.TestCase):
    """测试升级条件"""

    def test_requirements_defined(self):
        """每个阶段都应该有升级条件"""
        for stage in GrowthStage:
            self.assertIn(stage, GROWTH_REQUIREMENTS)

    def test_requirements_increasing(self):
        """后续阶段的升级条件应该更严格"""
        for i in range(1, len(GrowthStage)):
            current = GROWTH_REQUIREMENTS[GrowthStage(i)]
            next_req = GROWTH_REQUIREMENTS[GrowthStage(i + 1)]
            self.assertGreaterEqual(
                next_req.min_intimacy, current.min_intimacy
            )
            self.assertGreaterEqual(
                next_req.min_interactions, current.min_interactions
            )


class TestGrowthSystem(unittest.TestCase):
    """测试成长系统核心功能"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.gs = GrowthSystem(memory_path=self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_stage(self):
        """初始阶段应该是 NEWBORN"""
        self.assertEqual(self.gs.current_stage, GrowthStage.NEWBORN)
        self.assertEqual(self.gs.intimacy, 0)
        self.assertEqual(self.gs.interactions, 0)

    def test_record_interaction(self):
        """记录互动应该增加计数"""
        self.gs.record_interaction()
        self.assertEqual(self.gs.interactions, 1)
        self.gs.record_interaction(topic="工作")
        self.assertEqual(self.gs.interactions, 2)
        self.assertIn("工作", self.gs.unique_topics)

    def test_intimacy_change(self):
        """亲密度增减应该正常工作"""
        self.gs.increase_intimacy(10)
        self.assertEqual(self.gs.intimacy, 10)
        self.gs.increase_intimacy(5)
        self.assertEqual(self.gs.intimacy, 15)
        self.gs.decrease_intimacy(5)
        self.assertEqual(self.gs.intimacy, 10)

    def test_intimacy_capped(self):
        """亲密度应该在 0-100 之间"""
        self.gs.increase_intimacy(200)
        self.assertEqual(self.gs.intimacy, 100)
        self.gs.decrease_intimacy(50)
        self.gs.decrease_intimacy(100)
        self.assertEqual(self.gs.intimacy, 0)

    def test_cannot_advance_at_newborn(self):
        """NEWBORN 阶段不能升级（需要满足条件）"""
        check = self.gs.can_advance()
        self.assertFalse(check["can_advance"])

    def test_can_advance_with_conditions(self):
        """满足条件后可以升级"""
        # 模拟满足 FAMILIAR 阶段条件
        self.gs.intimacy = 25
        self.gs.interactions = 60
        self.gs.start_date = "2020-01-01"  # 很久以前
        self.gs.unique_topics = ["工作", "生活", "爱好", "学习", 
                                  "家庭", "朋友", "娱乐", "健康", "情感", "梦想"]
        
        check = self.gs.can_advance()
        self.assertTrue(check["can_advance"])

    def test_advance_stage(self):
        """升级应该更新阶段和历史"""
        # 满足条件
        self.gs.intimacy = 30
        self.gs.interactions = 100
        self.gs.start_date = "2020-01-01"
        self.gs.unique_topics = ["工作", "生活", "爱好", "学习", 
                                  "家庭", "朋友", "娱乐", "健康", "情感", "梦想"]
        
        result = self.gs.advance_stage()
        self.assertTrue(result["success"])
        self.assertEqual(self.gs.current_stage, GrowthStage.FAMILIAR)
        self.assertEqual(len(self.gs.stage_history), 1)

    def test_max_stage_no_advance(self):
        """最高阶段不能继续升级"""
        self.gs.current_stage = GrowthStage.SOULMATE
        self.gs.intimacy = 100
        check = self.gs.can_advance()
        self.assertFalse(check["can_advance"])

    def test_get_stage_info(self):
        """获取阶段信息应该返回完整数据"""
        info = self.gs.get_stage_info()
        self.assertIn("name", info)
        self.assertIn("emoji", info)
        self.assertIn("stats", info)
        self.assertIn("progress", info)

    def test_system_prompt_addition(self):
        """系统提示词补充应该包含阶段信息"""
        prompt = self.gs.get_system_prompt_addition()
        self.assertIn("婴儿初生期", prompt)
        self.assertIn("👶", prompt)

    def test_persistence(self):
        """状态应该持久化"""
        self.gs.increase_intimacy(20)
        self.gs.record_interaction()
        
        # 重新创建实例
        gs2 = GrowthSystem(memory_path=self.temp_dir)
        self.assertEqual(gs2.intimacy, 20)
        self.assertEqual(gs2.interactions, 1)


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""

    def test_get_stage_emoji(self):
        """emoji 映射应该正确"""
        self.assertEqual(get_stage_emoji(GrowthStage.NEWBORN), "👶")
        self.assertEqual(get_stage_emoji(GrowthStage.SOULMATE), "💍")

    def test_get_all_stages(self):
        """获取所有阶段应该返回7个"""
        stages = get_all_stages()
        self.assertEqual(len(stages), 7)


if __name__ == "__main__":
    unittest.main()
