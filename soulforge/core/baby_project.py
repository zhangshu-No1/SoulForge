"""
SoulForge 宝宝计划管理 — Baby Project Manager

将目标包装成"宝宝"，每个宝宝经历完整的生命周期：
  备孕（学习/规划）→ 生产（考试/项目/创作落地）→ 顺产（目标达成）→ 满月（庆祝复盘）

这不是幼稚，这是把冷冰冰的目标管理变成有温度的生命培养。

包含功能：
  - 完整的宝宝生命周期管理
  - 宝宝健康度评估
  - 宝宝成长报告
  - 宝宝关系建立
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .goal_keeper import GoalKeeper, Goal, BABY_STAGES


class BabyProject:
    """
    SoulForge 宝宝计划

    本质上是 GoalKeeper 的高级封装，用"宝宝"的隐喻
    让目标管理变得有情感、有温度、有仪式感。
    """

    def __init__(self, goals_path: str = "memory/goals.json"):
        self._keeper = GoalKeeper(goals_path)
        # 宝宝情感数据（独立于目标数据）
        self._baby_affections: dict = {}  # {goal_name: affection_score}

    def conceive(self, name: str, description: str, due_date: str = "",
                 tags: List[str] = None, priority: int = 3) -> Goal:
        """
        怀上一个"宝宝"（创建新目标）

        就像备孕一样，需要想清楚：
        - 这个宝宝叫什么（目标名称）
        - 我们要培养什么（目标描述）
        - 预产期是什么时候（截止日期）
        
        Args:
            name: 宝宝名字
            description: 宝宝描述（培养目标）
            due_date: 预产期（截止日期）
            tags: 标签
            priority: 优先级
            
        Returns:
            创建的宝宝（Goal对象）
        """
        baby = self._keeper.add_goal(
            name=name,
            description=description,
            deadline=due_date,
            stage="备孕",
            tags=tags or [],
            priority=priority,
        )
        # 初始化情感值
        self._baby_affections[name] = 50  # 初始50点情感值
        return baby

    def birth(self, name: str, note: str = "") -> bool:
        """
        "生产"（开始执行目标）

        从备孕进入生产阶段——不再只是规划，而是真刀真枪地干。
        
        Args:
            name: 宝宝名字
            note: 备注
            
        Returns:
            是否成功
        """
        return self._keeper.update_stage(name, "生产", note or "正式开始执行！")

    def celebrate(self, name: str, note: str = "") -> bool:
        """
        "顺产成功"（目标达成！）

        最激动的时刻——宝宝出生了！
        
        Args:
            name: 宝宝名字
            note: 备注
            
        Returns:
            是否成功
        """
        return self._keeper.update_stage(name, "顺产", note or "目标达成！🎉")

    def full_moon(self, name: str, note: str = "") -> bool:
        """
        "满月庆祝"（复盘总结）

        中国传统——满月酒。
        回顾整个过程，总结经验，准备下一个宝宝。
        
        Args:
            name: 宝宝名字
            note: 备注
            
        Returns:
            是否成功
        """
        return self._keeper.update_stage(name, "满月", note or "满月庆祝！🍼")

    def checkup(self, name: str, note: str) -> bool:
        """
        日常产检（记录进度）
        
        Args:
            name: 宝宝名字
            note: 检查内容
            
        Returns:
            是否成功
        """
        return self._keeper.add_progress(name, note)
    
    def express_love(self, name: str, love_points: int = 5) -> int:
        """
        向宝宝表达爱意（增加情感值）
        
        Args:
            name: 宝宝名字
            love_points: 爱意点数
            
        Returns:
            新的情感值
        """
        if name not in self._baby_affections:
            self._baby_affections[name] = 50
        self._baby_affections[name] = min(100, self._baby_affections[name] + love_points)
        return self._baby_affections[name]
    
    def show_concern(self, name: str, concern_level: int = 3) -> str:
        """
        关心宝宝的状态
        
        Args:
            name: 宝宝名字
            
        Returns:
            宝宝状态描述
        """
        baby = self._keeper.get_goal(name)
        if not baby:
            return f"找不到名为'{name}'的宝宝..."
        
        health = self.assess_health(name)
        affection = self._baby_affections.get(name, 50)
        
        status_lines = [f"👶 **{baby.name}** 状态报告"]
        status_lines.append(f"   当前阶段：{baby.stage}")
        status_lines.append(f"   健康度：{health['score']}/100 ({health['status']})")
        status_lines.append(f"   亲密度：{affection}/100")
        
        if baby.deadline:
            days_left = baby.days_until_deadline()
            if days_left is not None:
                if days_left < 0:
                    status_lines.append(f"   ⚠️ 已过期 {-days_left} 天")
                elif days_left == 0:
                    status_lines.append(f"   ⚠️ 今天就是预产期！")
                else:
                    status_lines.append(f"   预产期还有 {days_left} 天")
        
        if baby.progress_notes:
            latest = baby.progress_notes[-1]
            status_lines.append(f"   最新动态：{latest}")
        
        return "\n".join(status_lines)
    
    def assess_health(self, name: str) -> dict:
        """
        评估宝宝健康度
        
        健康度由以下因素决定：
        - 是否有定期更新（进度记录）
        - 是否在截止日期前
        - 情感值
        
        Args:
            name: 宝宝名字
            
        Returns:
            健康度评估字典
        """
        baby = self._keeper.get_goal(name)
        if not baby:
            return {"score": 0, "status": "未知", "factors": []}
        
        score = 70  # 基础分数
        factors = []
        
        # 检查阶段
        if baby.stage == "备孕":
            score += 5
            factors.append("备孕中，准备充分")
        elif baby.stage == "生产":
            score += 10
            factors.append("正在努力生产")
        elif baby.stage == "顺产":
            score += 20
            factors.append("顺产成功！")
        elif baby.stage == "满月":
            score += 25
            factors.append("已完成满月")
        
        # 检查是否过期
        if baby.is_overdue():
            score -= 30
            factors.append("⚠️ 已过期")
        elif baby.days_until_deadline() is not None and baby.days_until_deadline() <= 3:
            score += 10
            factors.append("即将到期，正在冲刺")
        
        # 检查进度记录
        if len(baby.progress_notes) == 0:
            score -= 20
            factors.append("缺少进度记录")
        elif len(baby.progress_notes) >= 3:
            score += 10
            factors.append("进度记录良好")
        
        # 检查优先级
        if baby.priority >= 4:
            score += 5
            factors.append("高优先级目标")
        
        # 情感加成
        affection = self._baby_affections.get(name, 50)
        if affection >= 70:
            score += 5
            factors.append("情感值高")
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        # 确定状态
        if score >= 80:
            status = "非常健康"
        elif score >= 60:
            status = "健康"
        elif score >= 40:
            status = "一般"
        elif score >= 20:
            status = "需要关注"
        else:
            status = "危险"
        
        return {
            "score": score,
            "status": status,
            "factors": factors,
        }
    
    def get_all_babies(self) -> List[Goal]:
        """查看所有宝宝"""
        return self._keeper.get_all_goals()

    def get_pregnant(self) -> List[Goal]:
        """查看正在"备孕"的宝宝"""
        return self._keeper.get_goals_by_stage("备孕")

    def get_in_labour(self) -> List[Goal]:
        """查看正在"生产"的宝宝"""
        return self._keeper.get_goals_by_stage("生产")

    def get_born(self) -> List[Goal]:
        """查看已经"顺产"的宝宝"""
        return self._keeper.get_goals_by_stage("顺产")
    
    def get_full_moon(self) -> List[Goal]:
        """查看已经"满月"的宝宝"""
        return self._keeper.get_goals_by_stage("满月")
    
    def get_babies_needing_attention(self) -> List[dict]:
        """
        获取需要关注的宝宝列表
        
        Returns:
            需要关注的宝宝及原因列表
        """
        attention_needed = []
        all_babies = self._keeper.get_all_goals(include_archived=False)
        
        for baby in all_babies:
            if baby.stage in ("顺产", "满月"):
                continue
                
            health = self.assess_health(baby.name)
            if health["score"] < 60:
                attention_needed.append({
                    "baby": baby,
                    "health": health,
                    "reason": health["factors"][0] if health["factors"] else "未知原因",
                })
        
        return sorted(attention_needed, key=lambda x: x["health"]["score"])
    
    def build_baby_report(self) -> str:
        """
        构建宝宝成长报告
        
        Returns:
            格式化的报告文本
        """
        all_babies = self._keeper.get_all_goals(include_archived=True)
        
        lines = ["## 👶 宝宝成长报告\n"]
        
        if not all_babies:
            lines.append("还没有宝宝哦，快去怀一个吧！🤰")
            return "\n".join(lines)
        
        # 统计
        pregnant = len(self.get_pregnant())
        in_labour = len(self.get_in_labour())
        born = len(self.get_born())
        full_moon = len(self.get_full_moon())
        
        lines.append(f"- 🤰 备孕中：{pregnant} 个")
        lines.append(f"- 🔧 生产中：{in_labour} 个")
        lines.append(f"- 🎉 已顺产：{born} 个")
        lines.append(f"- 🍼 已满月：{full_moon} 个\n")
        
        # 需要关注的宝宝
        attention = self.get_babies_needing_attention()
        if attention:
            lines.append("### ⚠️ 需要关注的宝宝\n")
            for item in attention:
                baby = item["baby"]
                lines.append(f"- **{baby.name}** ({item['reason']})")
                lines.append(f"  健康度：{item['health']['score']}/100")
            lines.append("")
        
        # 宝宝详情
        lines.append("### 宝宝详情\n")
        
        for baby in all_babies:
            health = self.assess_health(baby.name)
            affection = self._baby_affections.get(baby.name, 50)
            
            stage_emoji = {"备孕": "🤰", "生产": "🔧", "顺产": "🎉", "满月": "🍼"}.get(baby.stage, "📌")
            
            lines.append(f"{stage_emoji} **{baby.name}**")
            lines.append(f"   阶段：{baby.stage}")
            lines.append(f"   健康：{health['status']}（{health['score']}/100）")
            lines.append(f"   亲密度：{affection}/100")
            
            if baby.archived:
                lines.append(f"   状态：已归档")
            
            lines.append("")

        return "\n".join(lines)

    def build_dashboard(self) -> str:
        """构建宝宝看板"""
        return self._keeper.build_reminder()
    
    def get_statistics(self) -> dict:
        """获取宝宝统计信息"""
        all_babies = self._keeper.get_all_goals(include_archived=True)
        
        # 计算平均健康度和情感值
        health_scores = []
        affection_scores = []
        
        for baby in all_babies:
            if baby.stage not in ("顺产", "满月"):
                health = self.assess_health(baby.name)
                health_scores.append(health["score"])
            affection_scores.append(self._baby_affections.get(baby.name, 50))
        
        return {
            "total_babies": len(all_babies),
            "active_babies": len([b for b in all_babies if not b.archived]),
            "avg_health_score": round(sum(health_scores) / len(health_scores), 1) if health_scores else 0,
            "avg_affection": round(sum(affection_scores) / len(affection_scores), 1) if affection_scores else 0,
            "needs_attention": len(self.get_babies_needing_attention()),
            **self._keeper.get_statistics(),
        }
    
    def archive_baby(self, name: str, archive_note: str = "") -> bool:
        """
        归档宝宝
        
        Args:
            name: 宝宝名字
            archive_note: 归档备注
            
        Returns:
            是否归档成功
        """
        return self._keeper.archive_goal(name, archive_note)
    
    def get_baby_timeline(self, name: str) -> str:
        """
        获取宝宝的成长时间线
        
        Args:
            name: 宝宝名字
            
        Returns:
            时间线文本
        """
        baby = self._keeper.get_goal(name)
        if not baby:
            return f"找不到名为'{name}'的宝宝..."
        
        lines = [f"## 📅 {baby.name} 的成长时间线\n"]
        
        # 创建时间
        created = datetime.fromisoformat(baby.created_at)
        lines.append(f"🌱 出生日期：{created.strftime('%Y-%m-%d %H:%M')}")
        
        # 当前阶段
        stage_emoji = {"备孕": "🤰", "生产": "🔧", "顺产": "🎉", "满月": "🍼"}.get(baby.stage, "📌")
        lines.append(f"{stage_emoji} 当前阶段：{baby.stage}")
        
        # 进度记录
        if baby.progress_notes:
            lines.append("\n### 成长记录\n")
            for note in baby.progress_notes:
                lines.append(f"- {note}")
        
        # 完成时间
        if baby.completed_at:
            completed = datetime.fromisoformat(baby.completed_at)
            duration = (completed - created).days
            lines.append(f"\n🎊 完成日期：{completed.strftime('%Y-%m-%d')}")
            lines.append(f"⏱️ 培养时长：{duration} 天")
        
        return "\n".join(lines)
