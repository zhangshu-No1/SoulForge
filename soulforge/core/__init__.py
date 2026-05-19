"""SoulForge Core Modules.

Core modules for the SoulForge framework.
"""

from .memory_engine import MemoryEngine, MemoryEntry
from .relationship import (
    RelationshipManager,
    GROWTH_STAGES,
    PRESET_STAGES,
    GrowthStage,
)
from .goal_keeper import GoalKeeper, Goal, BABY_STAGES
from .baby_project import BabyProject
from .prompt_templates import PromptTemplate, PromptTemplateManager
from .emotion_system import EmotionSystem, Emotion, EmotionEvent

__all__ = [
    "MemoryEngine",
    "MemoryEntry",
    "RelationshipManager",
    "GROWTH_STAGES",
    "PRESET_STAGES",
    "GrowthStage",
    "GoalKeeper",
    "Goal",
    "BABY_STAGES",
    "BabyProject",
    "PromptTemplate",
    "PromptTemplateManager",
    "EmotionSystem",
    "Emotion",
    "EmotionEvent",
]
