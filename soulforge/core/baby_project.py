"""
SoulForge 宝宝计划管理 — Baby Project Manager

将目标包装成"宝宝"，每个宝宝经历完整的生命周期：
  备孕（学习/规划）→ 生产（考试/项目/创作落地）→ 顺产（目标达成）→ 满月（庆祝复盘）

这不是幼稚，这是把冷冰冰的目标管理变成有温度的生命培养。
"""

from .goal_keeper import GoalKeeper, Goal, BABY_STAGES


class BabyProject:
    """
    SoulForge 宝宝计划

    本质上是 GoalKeeper 的高级封装，用"宝宝"的隐喻
    让目标管理变得有情感、有温度、有仪式感。
    """

    def __init__(self, goals_path: str = "memory/goals.json"):
        self._keeper = GoalKeeper(goals_path)

    def conceive(self, name: str, description: str, due_date: str = "",
                 tags: list = None) -> Goal:
        """
        怀上一个"宝宝"（创建新目标）

        就像备孕一样，需要想清楚：
        - 这个宝宝叫什么（目标名称）
        - 我们要培养什么（目标描述）
        - 预产期是什么时候（截止日期）
        """
        baby = self._keeper.add_goal(
            name=name,
            description=description,
            deadline=due_date,
            stage="备孕",
            tags=tags or [],
        )
        return baby

    def birth(self, name: str, note: str = "") -> bool:
        """
        "生产"（开始执行目标）

        从备孕进入生产阶段——不再只是规划，而是真刀真枪地干。
        """
        return self._keeper.update_stage(name, "生产", note or "正式开始执行！")

    def celebrate(self, name: str, note: str = "") -> bool:
        """
        "顺产成功"（目标达成！）

        最激动的时刻——宝宝出生了！
        """
        return self._keeper.update_stage(name, "顺产", note or "目标达成！🎉")

    def full_moon(self, name: str, note: str = "") -> bool:
        """
        "满月庆祝"（复盘总结）

        中国传统——满月酒。
        回顾整个过程，总结经验，准备下一个宝宝。
        """
        return self._keeper.update_stage(name, "满月", note or "满月庆祝！🍼")

    def checkup(self, name: str, note: str) -> bool:
        """日常产检（记录进度）"""
        return self._keeper.add_progress(name, note)

    def get_all_babies(self) -> list[Goal]:
        """查看所有宝宝"""
        return self._keeper.get_all_goals()

    def get_pregnant(self) -> list[Goal]:
        """查看正在"备孕"的宝宝"""
        return self._keeper.get_goals_by_stage("备孕")

    def get_in_labour(self) -> list[Goal]:
        """查看正在"生产"的宝宝"""
        return self._keeper.get_goals_by_stage("生产")

    def get_born(self) -> list[Goal]:
        """查看已经"顺产"的宝宝"""
        return self._keeper.get_goals_by_stage("顺产")

    def build_dashboard(self) -> str:
        """构建宝宝看板"""
        return self._keeper.build_reminder()
