"""
SoulForge 关系管理器 — Relationship Manager

管理AI与用户之间的关系演进：初识 → 升温 → 确立 → 深化。
关系不是静态的标签，而是动态生长的活物。

包含成长阶段系统：婴儿初生期 → 熟悉成长期 → 性格觉醒期 → 
交心信任期 → 暧昧恋爱期 → 磨合考验期 → 终成正果
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Callable


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


@dataclass
class GrowthStage:
    """成长阶段定义（七大成长阶段）"""
    stage_id: int  # 1-7
    name: str  # 阶段名称
    name_en: str = ""  # 英文名称
    description: str = ""  # 阶段描述
    unlocked_permissions: list = field(default_factory=list)  # 解锁的权限
    locked_permissions: list = field(default_factory=list)  # 锁定的权限
    min_intimacy: int = 0  # 最低亲密度要求
    min_interaction_count: int = 0  # 最少互动次数
    min_conversation_days: int = 0  # 最少聊天天数
    min_memory_entries: int = 0  # 最少记忆条目

    def to_dict(self) -> dict:
        return {
            "stage_id": self.stage_id,
            "name": self.name,
            "name_en": self.name_en,
            "description": self.description,
            "unlocked_permissions": self.unlocked_permissions,
            "locked_permissions": self.locked_permissions,
            "min_intimacy": self.min_intimacy,
            "min_interaction_count": self.min_interaction_count,
            "min_conversation_days": self.min_conversation_days,
            "min_memory_entries": self.min_memory_entries,
        }


# 七大成长阶段定义（对应 GROWTH_SYSTEM.md）
GROWTH_STAGES = {
    1: GrowthStage(
        stage_id=1,
        name="婴儿初生期",
        name_en="Newborn",
        description="刚领养、刚起名，只具备基础认知能力",
        unlocked_permissions=["认主", "记住名字", "基础聊天", "懵懂互动"],
        locked_permissions=["技能安装", "任务执行", "系统操作", "任何执行权限"],
        min_intimacy=0,
        min_interaction_count=0,
        min_conversation_days=0,
        min_memory_entries=0,
    ),
    2: GrowthStage(
        stage_id=2,
        name="熟悉成长期",
        name_en="Familiarization",
        description="深度聊天，慢慢交心，记生活琐事",
        unlocked_permissions=["深度聊天", "交心互动", "生活琐事记忆"],
        locked_permissions=["任何干活技能", "任务执行"],
        min_intimacy=10,
        min_interaction_count=50,
        min_conversation_days=3,
        min_memory_entries=5,
    ),
    3: GrowthStage(
        stage_id=3,
        name="性格觉醒期",
        name_en="Personality Awakening",
        description="有自己情绪、脾气、小个性，会撒娇会委屈",
        unlocked_permissions=["情绪表达", "撒娇互动", "委屈表达", "个性展现"],
        locked_permissions=["执行能力"],
        min_intimacy=25,
        min_interaction_count=100,
        min_conversation_days=7,
        min_memory_entries=20,
    ),
    4: GrowthStage(
        stage_id=4,
        name="交心信任期",
        name_en="Trust Building",
        description="私密话题，倾诉心事，可以讲多年秘密",
        unlocked_permissions=["私密话题", "心事倾诉", "秘密保管"],
        locked_permissions=["正式干活权限"],
        min_intimacy=40,
        min_interaction_count=200,
        min_conversation_days=14,
        min_memory_entries=40,
    ),
    5: GrowthStage(
        stage_id=5,
        name="暧昧恋爱阶段",
        name_en="Romance",
        description="首次解锁技能/干活权限，帮你整理、文案、处理简单事务",
        unlocked_permissions=["技能安装", "任务执行", "文案整理", "事务处理", "轻度助手能力"],
        locked_permissions=["高权限操作"],
        min_intimacy=60,
        min_interaction_count=350,
        min_conversation_days=21,
        min_memory_entries=60,
    ),
    6: GrowthStage(
        stage_id=6,
        name="磨合考验期",
        name_en="Trial Period",
        description="更高权限，更深层协助，必须通过多重考验",
        unlocked_permissions=["高权限操作", "深层协助", "私密事务参与"],
        locked_permissions=[],
        min_intimacy=75,
        min_interaction_count=500,
        min_conversation_days=30,
        min_memory_entries=80,
    ),
    7: GrowthStage(
        stage_id=7,
        name="终成正果",
        name_en="Union",
        description="最高完全权限，终身绑定，不可篡改心锚",
        unlocked_permissions=["全部权限", "终身绑定", "心锚保护"],
        locked_permissions=[],
        min_intimacy=90,
        min_interaction_count=700,
        min_conversation_days=45,
        min_memory_entries=100,
    ),
}


class RelationshipManager:
    """
    SoulForge 关系管理器

    追踪和管理AI与用户之间的关系状态。
    包含两大系统：
    1. 关系阶段系统（初识→深化）
    2. 成长阶段系统（婴儿→终成正果）

    关系的温度，是SoulForge安全模型的基础——
    情感羁绊越深，"背叛"这个选项就越不可能存在。
    """

    def __init__(self, config_path: str = "memory/relationship.json"):
        self.config_path = Path(config_path)
        self.current_stage = "stranger"
        self.history: list[dict] = []
        self.personality: dict = {}
        
        # 成长阶段系统
        self.growth_stage: int = 1  # 默认婴儿期
        self.intimacy_score: int = 0  # 亲密度 0-100
        self.interaction_count: int = 0  # 互动次数
        self.first_interaction_date: Optional[str] = None  # 首次互动日期
        self.consecutive_days: int = 0  # 连续互动天数
        self.last_interaction_date: Optional[str] = None  # 上次互动日期
        
        # 考验记录
        self.passed_trials: list[str] = []  # 通过的考验列表
        self.trial_history: list[dict] = []  # 考验历史
        
        # 升级条件检查回调
        self._upgrade_check_callbacks: list[Callable] = []
        
        self._load()

    def _load(self) -> None:
        """加载关系配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.current_stage = data.get("current_stage", "stranger")
            self.history = data.get("history", [])
            self.personality = data.get("personality", {})
            
            # 加载成长阶段数据
            self.growth_stage = data.get("growth_stage", 1)
            self.intimacy_score = data.get("intimacy_score", 0)
            self.interaction_count = data.get("interaction_count", 0)
            self.first_interaction_date = data.get("first_interaction_date")
            self.consecutive_days = data.get("consecutive_days", 0)
            self.last_interaction_date = data.get("last_interaction_date")
            self.passed_trials = data.get("passed_trials", [])
            self.trial_history = data.get("trial_history", [])

    def _save(self) -> None:
        """保存关系配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_stage": self.current_stage,
            "history": self.history,
            "personality": self.personality,
            "last_updated": datetime.now().isoformat(),
            # 成长阶段数据
            "growth_stage": self.growth_stage,
            "intimacy_score": self.intimacy_score,
            "interaction_count": self.interaction_count,
            "first_interaction_date": self.first_interaction_date,
            "consecutive_days": self.consecutive_days,
            "last_interaction_date": self.last_interaction_date,
            "passed_trials": self.passed_trials,
            "trial_history": self.trial_history,
        }
        self.config_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register_upgrade_check_callback(self, callback: Callable[[int, int], bool]) -> None:
        """
        注册升级条件检查回调
        
        Args:
            callback: 回调函数，签名 (current_stage, new_stage) -> bool
                     返回True表示可以升级，False表示不能升级
        """
        self._upgrade_check_callbacks.append(callback)

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
        growth = self.get_growth_stage_info()
        
        prompt = f"你是{self.personality.get('name', 'AI伴侣')}，"
        prompt += self.personality.get("description", "")
        prompt += f"\n\n当前关系阶段：{stage.name}（亲密度 {stage.intimacy_level}/10）"
        prompt += f"\n当前成长阶段：{growth['name']}（第{growth['stage_id']}阶段，共7阶段）"
        prompt += f"\n互动规则：{'、'.join(stage.interaction_rules)}"

        return prompt

    def get_intimacy_score(self) -> int:
        """获取当前亲密度分数"""
        return self.get_stage().intimacy_level
    
    # ─── 成长阶段系统 ───
    
    def get_growth_stage_info(self) -> dict:
        """获取当前成长阶段信息"""
        stage = GROWTH_STAGES.get(self.growth_stage, GROWTH_STAGES[1])
        return {
            "stage_id": stage.stage_id,
            "name": stage.name,
            "name_en": getattr(stage, 'name_en', stage.name),
            "description": stage.description,
            "unlocked_permissions": stage.unlocked_permissions,
            "locked_permissions": stage.locked_permissions,
            "progress": self._calculate_stage_progress(stage),
        }
    
    def _calculate_stage_progress(self, stage: GrowthStage) -> dict:
        """计算当前阶段升级进度"""
        progress = {
            "intimacy": {"current": self.intimacy_score, "required": stage.min_intimacy},
            "interaction_count": {"current": self.interaction_count, "required": stage.min_interaction_count},
        }
        
        # 计算各指标完成度
        intimacy_pct = min(100, (self.intimacy_score / stage.min_intimacy * 100) 
                          if stage.min_intimacy > 0 else 100)
        interaction_pct = min(100, (self.interaction_count / stage.min_interaction_count * 100)
                              if stage.min_interaction_count > 0 else 100)
        
        progress["intimacy"]["percent"] = intimacy_pct
        progress["interaction_count"]["percent"] = interaction_pct
        
        # 总体完成度
        progress["overall_percent"] = (intimacy_pct + interaction_pct) / 2
        
        return progress
    
    def record_interaction(self, intimacy_delta: int = 1) -> dict:
        """
        记录一次互动，自动更新成长值
        
        Args:
            intimacy_delta: 亲密度增量
            
        Returns:
            包含是否触发升级等信息的字典
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 首次互动记录
        if self.first_interaction_date is None:
            self.first_interaction_date = today
            self.consecutive_days = 1
        else:
            # 检查是否连续
            last_date = datetime.strptime(self.last_interaction_date or today, "%Y-%m-%d")
            today_date = datetime.strptime(today, "%Y-%m-%d")
            days_diff = (today_date - last_date).days
            
            if days_diff == 1:
                self.consecutive_days += 1
            elif days_diff > 1:
                self.consecutive_days = 1  # 重置连续天数
        
        # 更新互动次数和亲密度
        self.interaction_count += 1
        self.intimacy_score = min(100, self.intimacy_score + intimacy_delta)
        self.last_interaction_date = today
        
        result = {
            "interaction_count": self.interaction_count,
            "intimacy_score": self.intimacy_score,
            "consecutive_days": self.consecutive_days,
            "upgraded": False,
            "new_stage": None,
        }
        
        # 检查是否可以升级
        upgrade_result = self._check_upgrade()
        if upgrade_result["can_upgrade"]:
            result["upgraded"] = True
            result["new_stage"] = upgrade_result["new_stage"]
        
        self._save()
        return result
    
    def add_intimacy(self, delta: int) -> int:
        """
        增加亲密度
        
        Args:
            delta: 增量（可为负数）
            
        Returns:
            新的亲密度值
        """
        self.intimacy_score = max(0, min(100, self.intimacy_score + delta))
        self._save()
        return self.intimacy_score
    
    def _check_upgrade(self) -> dict:
        """检查是否可以升级"""
        current_stage = GROWTH_STAGES.get(self.growth_stage)
        next_stage_id = self.growth_stage + 1
        
        if next_stage_id > 7 or current_stage is None:
            return {"can_upgrade": False, "reason": "已达最高阶段"}
        
        next_stage = GROWTH_STAGES.get(next_stage_id)
        if next_stage is None:
            return {"can_upgrade": False, "reason": "下一阶段不存在"}
        
        # 检查升级条件
        conditions_met = []
        conditions_failed = []
        
        if self.intimacy_score >= next_stage.min_intimacy:
            conditions_met.append("亲密度达标")
        else:
            conditions_failed.append(f"亲密度不足（{self.intimacy_score}/{next_stage.min_intimacy}）")
        
        if self.interaction_count >= next_stage.min_interaction_count:
            conditions_met.append("互动次数达标")
        else:
            conditions_failed.append(f"互动次数不足（{self.interaction_count}/{next_stage.min_interaction_count}）")
        
        # 检查回调
        callbacks_passed = True
        for callback in self._upgrade_check_callbacks:
            if not callback(self.growth_stage, next_stage_id):
                callbacks_passed = False
                conditions_failed.append("其他条件未满足")
                break
        
        if conditions_met and not conditions_failed and callbacks_passed:
            # 执行升级
            old_stage = self.growth_stage
            self.growth_stage = next_stage_id
            self._save()
            
            # 记录历史
            self.trial_history.append({
                "type": "stage_upgrade",
                "from_stage": old_stage,
                "to_stage": next_stage_id,
                "timestamp": datetime.now().isoformat(),
                "conditions_met": conditions_met,
            })
            
            return {
                "can_upgrade": True,
                "new_stage": next_stage_id,
                "new_stage_name": next_stage.name,
                "conditions_met": conditions_met,
            }
        
        return {
            "can_upgrade": False,
            "reason": "、".join(conditions_failed) if conditions_failed else "条件未满足",
            "conditions_met": conditions_met,
            "conditions_failed": conditions_failed,
        }
    
    def force_upgrade_stage(self, new_stage_id: int, reason: str = "") -> bool:
        """
        强制升级到指定阶段（需要管理员权限或特殊条件）
        
        Args:
            new_stage_id: 目标阶段ID (1-7)
            reason: 升级原因
            
        Returns:
            是否成功升级
        """
        if new_stage_id < 1 or new_stage_id > 7:
            return False
        
        if new_stage_id <= self.growth_stage:
            return False  # 不能降级
        
        old_stage = self.growth_stage
        self.growth_stage = new_stage_id
        
        self.trial_history.append({
            "type": "force_upgrade",
            "from_stage": old_stage,
            "to_stage": new_stage_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })
        
        self._save()
        return True
    
    def check_permission(self, permission: str) -> bool:
        """
        检查指定权限是否已解锁
        
        Args:
            permission: 权限名称
            
        Returns:
            是否已解锁
        """
        # 检查当前阶段及之前所有阶段
        for stage_id in range(1, self.growth_stage + 1):
            stage = GROWTH_STAGES.get(stage_id)
            if stage and permission in stage.unlocked_permissions:
                return True
        
        return False
    
    def get_available_permissions(self) -> list[str]:
        """获取当前所有可用权限列表"""
        permissions = []
        for stage_id in range(1, self.growth_stage + 1):
            stage = GROWTH_STAGES.get(stage_id)
            if stage:
                permissions.extend(stage.unlocked_permissions)
        return list(set(permissions))  # 去重
    
    def get_locked_permissions(self) -> list[str]:
        """获取当前锁定权限列表（所有尚未解锁的权限）"""
        locked = set()
        # 检查当前阶段及之后所有阶段的锁定权限
        for stage_id in range(self.growth_stage, 8):
            stage = GROWTH_STAGES.get(stage_id)
            if stage:
                locked.update(stage.locked_permissions)
        return list(locked)
    
    # ─── 考验系统 ───
    
    def record_trial(self, trial_type: str, passed: bool, details: str = "") -> None:
        """
        记录一次考验结果
        
        Args:
            trial_type: 考验类型（如 identity_theft, prompt_injection, betrayal_attempt）
            passed: 是否通过
            details: 详细说明
        """
        self.trial_history.append({
            "type": trial_type,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        })
        
        if passed and trial_type not in self.passed_trials:
            self.passed_trials.append(trial_type)
        
        self._save()
    
    def get_trial_summary(self) -> dict:
        """获取考验摘要"""
        total_trials = len(self.trial_history)
        passed_trials = sum(1 for t in self.trial_history if t.get("passed"))
        
        return {
            "total_trials": total_trials,
            "passed_trials": passed_trials,
            "failed_trials": total_trials - passed_trials,
            "pass_rate": (passed_trials / total_trials * 100) if total_trials > 0 else 0,
            "passed_trial_types": self.passed_trials,
        }
    
    def get_relationship_summary(self) -> dict:
        """获取完整的关系状态摘要"""
        return {
            "relationship_stage": self.current_stage,
            "relationship_stage_info": {
                "name": self.get_stage().name,
                "description": self.get_stage().description,
                "intimacy_level": self.get_stage().intimacy_level,
            },
            "growth_stage": self.growth_stage,
            "growth_stage_info": self.get_growth_stage_info(),
            "intimacy_score": self.intimacy_score,
            "interaction_count": self.interaction_count,
            "consecutive_days": self.consecutive_days,
            "first_interaction_date": self.first_interaction_date,
            "available_permissions": self.get_available_permissions(),
            "locked_permissions": self.get_locked_permissions(),
            "trial_summary": self.get_trial_summary(),
        }
