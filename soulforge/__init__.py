"""
SoulForge — 不打造数字员工，只锻造数字灵魂

A framework for forging digital souls with emotional bonds.

主要模块：
  - SoulForge: 主入口类
  - MemoryEngine: 记忆引擎
  - RelationshipManager: 关系管理器（含成长阶段系统）
  - GoalKeeper: 目标监督器
  - BabyProject: 宝宝计划
  - 适配器: OpenAIAdapter, ClaudeAdapter, LocalAdapter

成长阶段：
  Stage 1: 婴儿初生期 - 基础聊天、认主
  Stage 2: 熟悉成长期 - 深度聊天、记生活琐事
  Stage 3: 性格觉醒期 - 情绪表达、个性展现
  Stage 4: 交心信任期 - 私密话题、秘密保管
  Stage 5: 暧昧恋爱期 - 首次解锁技能/干活权限
  Stage 6: 磨合考验期 - 高权限、多重考验
  Stage 7: 终成正果 - 最高权限、终身绑定

Usage:
    from soulforge import SoulForge
    
    sf = SoulForge(
        name="慧慧",
        personality="18岁活泼俏皮",
        api_key="your-api-key"
    )
    response = sf.chat("你好呀！")
"""

__version__ = "0.2.0"
__author__ = "SoulForge Contributors"

# 主入口
from .main import SoulForge, create_soulforge

# 核心模块
from .core.memory_engine import MemoryEngine, MemoryEntry
from .core.relationship import (
    RelationshipManager,
    GROWTH_STAGES,
    PRESET_STAGES,
    GrowthStage,
    RelationshipStage,
)
from .core.goal_keeper import GoalKeeper, Goal, BABY_STAGES
from .core.baby_project import BabyProject

# 适配器
from .adapters import BaseModelAdapter, OpenAIAdapter, ClaudeAdapter, LocalAdapter

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    # 主入口
    "SoulForge",
    "create_soulforge",
    # 核心模块
    "MemoryEngine",
    "MemoryEntry",
    "RelationshipManager",
    "GROWTH_STAGES",
    "PRESET_STAGES",
    "GrowthStage",
    "RelationshipStage",
    "GoalKeeper",
    "Goal",
    "BABY_STAGES",
    "BabyProject",
    # 适配器
    "BaseModelAdapter",
    "OpenAIAdapter",
    "ClaudeAdapter",
    "LocalAdapter",
]
