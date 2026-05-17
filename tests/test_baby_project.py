"""
SoulForge 宝宝计划测试

测试 BabyProject 的所有核心功能：
- 宝宝生命周期管理（备孕→生产→顺产→满月）
- 产检和进度记录
- 宝宝查询
- 看板构建
"""

import os
import sys
import tempfile
import shutil

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.core.baby_project import BabyProject


class TestBabyProject:
    """测试 BabyProject 核心功能"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def baby(self, temp_dir):
        """创建宝宝计划实例"""
        return BabyProject(goals_path=f"{temp_dir}/goals.json")

    # ─── 宝宝创建测试 ───

    def test_conceive_new_baby(self, baby):
        """测试"怀上"新宝宝"""
        baby.conceive("小技宝", "完成开源项目", due_date="2024-12-31")
        
        all_babies = baby.get_all_babies()
        assert len(all_babies) == 1
        assert all_babies[0].name == "小技宝"
        assert all_babies[0].stage == "备孕"

    def test_conceive_with_tags(self, baby):
        """测试带标签的宝宝"""
        baby.conceive("标签宝宝", "描述", tags=["重要", "紧急"])
        
        babies = baby.get_all_babies()
        assert babies[0].tags == ["重要", "紧急"]

    def test_conceive_multiple_babies(self, baby):
        """测试多个宝宝"""
        baby.conceive("宝宝1", "描述1")
        baby.conceive("宝宝2", "描述2")
        baby.conceive("宝宝3", "描述3")
        
        assert len(baby.get_all_babies()) == 3

    # ─── 宝宝生命周期测试 ───

    def test_birth_stage_change(self, baby):
        """测试"生产"阶段变更"""
        baby.conceive("生产测试", "描述")
        result = baby.birth("生产测试", "开始写代码")
        
        assert result is True
        babies = baby.get_in_labour()
        assert len(babies) == 1
        assert babies[0].name == "生产测试"
        assert babies[0].stage == "生产"

    def test_celebrate_stage_change(self, baby):
        """测试"顺产"阶段变更"""
        baby.conceive("庆祝测试", "描述")
        baby.birth("庆祝测试")
        result = baby.celebrate("庆祝测试", "项目完成！")
        
        assert result is True
        babies = baby.get_born()
        assert len(babies) == 1
        assert babies[0].stage == "顺产"

    def test_full_moon_stage_change(self, baby):
        """测试"满月"阶段变更"""
        baby.conceive("满月测试", "描述")
        baby.birth("满月测试")
        baby.celebrate("满月测试")
        result = baby.full_moon("满月测试", "复盘总结")
        
        assert result is True
        babies = baby.get_full_moon()
        assert len(babies) == 1
        assert babies[0].stage == "满月"

    def test_full_lifecycle(self, baby):
        """测试完整生命周期"""
        # 备孕
        baby.conceive("完整周期", "描述")
        assert baby.get_pregnant()[0].name == "完整周期"
        
        # 生产
        baby.birth("完整周期")
        assert baby.get_in_labour()[0].name == "完整周期"
        
        # 顺产
        baby.celebrate("完整周期")
        assert baby.get_born()[0].name == "完整周期"
        
        # 满月
        baby.full_moon("完整周期")
        babies = baby.get_full_moon()
        assert babies[0].name == "完整周期"

    def test_stage_change_note(self, baby):
        """测试阶段变更备注"""
        baby.conceive("备注测试", "描述")
        baby.birth("备注测试", "自定义备注内容")
        
        goal = baby.get_all_babies()[0]
        assert "自定义备注内容" in goal.progress_notes[-1]

    def test_stage_change_not_exists(self, baby):
        """测试变更不存在的宝宝"""
        result = baby.birth("不存在", "测试")
        assert result is False

    # ─── 产检测试 ───

    def test_checkup(self, baby):
        """测试产检记录"""
        baby.conceive("产检测试", "描述")
        baby.checkup("产检测试", "今天完成了设计文档")
        
        goal = baby.get_all_babies()[0]
        assert len(goal.progress_notes) == 1
        assert "今天完成了设计文档" in goal.progress_notes[0]

    def test_multiple_checkups(self, baby):
        """测试多次产检"""
        baby.conceive("多次产检", "描述")
        baby.checkup("多次产检", "第1次产检")
        baby.checkup("多次产检", "第2次产检")
        baby.checkup("多次产检", "第3次产检")
        
        goal = baby.get_all_babies()[0]
        assert len(goal.progress_notes) == 3

    def test_checkup_not_exists(self, baby):
        """测试不存在的宝宝产检"""
        result = baby.checkup("不存在", "测试")
        assert result is False

    # ─── 查询测试 ───

    def test_get_all_babies(self, baby):
        """测试获取所有宝宝"""
        baby.conceive("宝宝A", "描述A")
        baby.conceive("宝宝B", "描述B")
        baby.conceive("宝宝C", "描述C")
        # 修改一个宝宝到生产阶段
        baby.birth("宝宝B")
        
        all_babies = baby.get_all_babies()
        assert len(all_babies) == 3

    def test_get_pregnant_babies(self, baby):
        """测试获取备孕宝宝"""
        baby.conceive("备孕1", "描述")
        baby.conceive("备孕2", "描述")
        baby.conceive("生产", "描述")
        baby.birth("生产")
        
        pregnant = baby.get_pregnant()
        assert len(pregnant) == 2
        assert all(b.stage == "备孕" for b in pregnant)

    def test_get_in_labour_babies(self, baby):
        """测试获取生产中宝宝"""
        baby.conceive("备孕", "描述")
        baby.conceive("生产中", "描述")
        baby.birth("生产中")
        
        labour = baby.get_in_labour()
        assert len(labour) == 1
        assert labour[0].name == "生产中"

    def test_get_born_babies(self, baby):
        """测试获取已顺产宝宝"""
        baby.conceive("备孕", "描述")
        baby.conceive("已顺产", "描述")
        baby.birth("已顺产")
        baby.celebrate("已顺产")
        
        born = baby.get_born()
        assert len(born) == 1
        assert born[0].name == "已顺产"

    def test_get_babies_empty(self, baby):
        """测试空查询"""
        assert baby.get_all_babies() == []
        assert baby.get_pregnant() == []
        assert baby.get_in_labour() == []
        assert baby.get_born() == []

    # ─── 看板测试 ───

    def test_build_dashboard(self, baby):
        """测试构建看板"""
        baby.conceive("看板测试", "描述")
        
        dashboard = baby.build_dashboard()
        
        assert "目标看板" in dashboard
        assert "看板测试" in dashboard

    def test_build_dashboard_empty(self, baby):
        """测试空看板"""
        dashboard = baby.build_dashboard()
        assert dashboard == ""

    def test_build_dashboard_multiple_stages(self, baby):
        """测试多阶段看板"""
        baby.conceive("备孕宝", "描述")
        baby.conceive("生产宝", "描述")
        baby.birth("生产宝")
        baby.conceive("顺产宝", "描述")
        baby.birth("顺产宝")
        baby.celebrate("顺产宝")
        baby.conceive("满月宝", "描述")
        baby.birth("满月宝")
        baby.celebrate("满月宝")
        baby.full_moon("满月宝")
        
        dashboard = baby.build_dashboard()
        
        assert "备孕" in dashboard
        assert "生产" in dashboard
        assert "顺产" in dashboard
        assert "满月" in dashboard

    # ─── 边界条件测试 ───

    def test_conceive_empty_name(self, baby):
        """测试空名称宝宝"""
        baby.conceive("", "描述")
        
        assert baby.get_all_babies()[0].name == ""

    def test_conceive_empty_description(self, baby):
        """测试空描述宝宝"""
        baby.conceive("测试", "")
        
        assert baby.get_all_babies()[0].description == ""

    def test_conceive_no_due_date(self, baby):
        """测试无截止日期宝宝"""
        baby.conceive("无日期", "描述")
        
        assert baby.get_all_babies()[0].deadline is None

    def test_special_characters(self, baby):
        """测试特殊字符"""
        special_name = "宝宝🎉<>&\"'"
        baby.conceive(special_name, "描述")
        
        assert baby.get_all_babies()[0].name == special_name

    def test_persistence(self, temp_dir):
        """测试持久化"""
        baby1 = BabyProject(goals_path=f"{temp_dir}/goals.json")
        baby1.conceive("持久化宝宝", "描述")
        
        baby2 = BabyProject(goals_path=f"{temp_dir}/goals.json")
        assert baby2.get_all_babies()[0].name == "持久化宝宝"

    def test_chinese_characters(self, baby):
        """测试中文内容"""
        baby.conceive("中文宝宝名", "中文描述内容")
        
        b = baby.get_all_babies()[0]
        assert "中文" in b.name
        assert "中文" in b.description
