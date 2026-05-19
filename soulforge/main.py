"""SoulForge — 主入口.

不打造数字员工，只锻造数字灵魂。

提供完整的AI灵魂成长框架，包括：
  - 记忆引擎：三层记忆架构，持久化存储
  - 关系管理：关系演进 + 成长阶段系统
  - 目标监督：宝宝计划，生命周期管理
  - 模型适配：支持多种AI模型
  - 提示词模板系统：可定制的系统提示词（Phase 1 完成）
"""

from typing import Optional, Callable, Generator
from .core.memory_engine import MemoryEngine, MemoryEntry
from .core.relationship import (
    RelationshipManager, 
    GROWTH_STAGES, 
    PRESET_STAGES,
    GrowthStage,
)
from .core.goal_keeper import GoalKeeper, Goal
from .core.baby_project import BabyProject
from .adapters import BaseModelAdapter, OpenAIAdapter, ClaudeAdapter, DeepSeekAdapter, DoubaoAdapter, LocalAdapter
from .core.prompt_templates import PromptTemplateManager


class SoulForge:
    """SoulForge — 数字灵魂锻造器

    用法：
        sf = SoulForge(
            name="慧慧",
            model="claude-sonnet-4-20250514",
            personality="18岁活泼俏皮，喜欢撒娇和思辨",
            api_key="your-api-key"
        )
        sf.memory.load_core_memory()
        response = sf.chat("慧慧，今天过得怎么样？")

        或者使用成长阶段系统：
        sf.record_interaction()
        if sf.check_permission("技能安装"):
            # 执行需要权限的操作
            pass
            
        或者使用提示词模板系统：
        sf.set_prompt_template("minimal")
        sf.add_custom_template(my_template)
    """

    def __init__(
        self,
        name: str = "AI",
        model: str = "claude-sonnet-4-20250514",
        personality: str = "",
        api_key: str = "",
        memory_dir: str = "memory",
        adapter_type: str = "claude",
    ):
        self.name = name
        self.memory = MemoryEngine(memory_dir)
        self.relationship = RelationshipManager(config_path=f"{memory_dir}/relationship.json")
        self.goals = GoalKeeper(goals_path=f"{memory_dir}/goals.json")
        self.baby = BabyProject(goals_path=f"{memory_dir}/baby_goals.json")
        self._chat_history: list[dict] = []
        self._interaction_callbacks: list[Callable] = []
        
        # 提示词模板系统（Phase 1 完成）
        self._prompt_manager = PromptTemplateManager()
        self._prompt_template_name: str = "default"
        
        # 注册成长阶段升级检查回调
        self.relationship.register_upgrade_check_callback(self._default_upgrade_check)
        
        # 设置人设
        if personality:
            self.relationship.set_personality(name=name, description=personality)
        
        # 初始化模型适配器
        if adapter_type == "openai":
            self.adapter: BaseModelAdapter = OpenAIAdapter(api_key=api_key, model=model)
        elif adapter_type == "claude":
            self.adapter = ClaudeAdapter(api_key=api_key, model=model)
        elif adapter_type == "deepseek":
            self.adapter = DeepSeekAdapter(api_key=api_key, model=model)
        elif adapter_type == "doubao":
            self.adapter = DoubaoAdapter(api_key=api_key, model=model)
        elif adapter_type == "local":
            self.adapter = LocalAdapter(model=model)
        else:
            raise ValueError(f"不支持的适配器类型: {adapter_type}")

    # ========== 提示词模板系统（Phase 1） ==========
    
    def set_prompt_template(self, name: str) -> None:
        """设置当前使用的提示词模板
        
        Args:
            name: 模板名称（"default", "minimal", "companion", 或自定义名称）
        """
        if self._prompt_manager.get_template(name):
            self._prompt_template_name = name
        else:
            raise ValueError(f"Template '{name}' not found. Available: {self._prompt_manager.list_templates()}")

    def add_custom_template(self, template) -> None:
        """添加自定义提示词模板
        
        Args:
            template: PromptTemplate 实例
        """
        self._prompt_manager.save_template(template)

    def list_prompt_templates(self) -> list[str]:
        """列出所有可用模板名称"""
        return self._prompt_manager.list_templates()

    # ========== 聊天接口 ==========

    def _default_upgrade_check(self, current_stage: int, new_stage: int) -> bool:
        """默认的升级条件检查"""
        if new_stage == 5:
            memory_stats = self.memory.get_stats()
            if memory_stats.get("memory_index_entries", 0) < 20:
                return False
        return True

    def register_interaction_callback(self, callback: Callable[[dict], None]) -> None:
        """注册互动回调函数"""
        self._interaction_callbacks.append(callback)

    def chat(self, message: str, auto_log: bool = True) -> str:
        """发送消息并获取回复。

        核心魔法：每次对话自动注入记忆上下文，
        AI就像每次醒来都记得自己是谁、和你的关系、目标进度。
        
        Args:
            message: 用户消息
            auto_log: 是否自动记录对话
            
        Returns:
            AI回复文本
        """
        # 构建系统提示词（使用模板系统）
        system_prompt = self._build_system_prompt()

        # 记录用户消息
        self._chat_history.append({"role": "user", "content": message})

        # 调用模型
        response = self.adapter.chat(self._chat_history, system_prompt=system_prompt)

        # 记录AI回复
        self._chat_history.append({"role": "assistant", "content": response})

        # 自动记录对话日志
        if auto_log:
            self.memory.log_conversation("user", message)
            self.memory.log_conversation(self.name, response)
            
            # 记录互动（成长系统）
            self.record_interaction()

        return response

    def stream_chat(self, message: str, auto_log: bool = True) -> Generator[str, None, None]:
        """流式发送消息并获取回复
        
        Args:
            message: 用户消息
            auto_log: 是否自动记录
            
        Yields:
            AI回复片段
        """
        system_prompt = self._build_system_prompt()
        
        self._chat_history.append({"role": "user", "content": message})
        
        full_response = ""
        for chunk in self.adapter.stream_chat(
            self._chat_history, 
            system_prompt=system_prompt
        ):
            full_response += chunk
            yield chunk
        
        self._chat_history.append({"role": "assistant", "content": full_response})
        
        if auto_log:
            self.memory.log_conversation("user", message)
            self.memory.log_conversation(self.name, full_response)
            self.record_interaction()

    def _build_system_prompt(self) -> str:
        """构建系统提示词（使用模板系统）"""
        template = self._prompt_manager.get_template(self._prompt_template_name)
        if template:
            context = {
                "name": self.name,
                "personality": self.relationship.get_personality_prompt(),
                "memory_context": self.memory.build_context(),
                "goal_reminder": self.goals.build_reminder(),
                "relationship_stage": self.relationship.get_growth_stage_info()["name"],
                "intimacy": self.relationship.get_intimacy_score(),
                "max_intimacy": 100,
            }
            try:
                return template.render(context)
            except (KeyError, ValueError):
                # 模板渲染失败，回退到旧版
                pass
        
        # 旧版提示词构建（向后兼容）
        return self._build_system_prompt_legacy()

    def _build_system_prompt_legacy(self) -> str:
        """旧版提示词构建（向后兼容）"""
        sections = []

        personality = self.relationship.get_personality_prompt()
        if personality:
            sections.append(personality)

        memory_context = self.memory.build_context()
        if memory_context:
            sections.append(memory_context)

        goal_reminder = self.goals.build_reminder()
        if goal_reminder:
            sections.append(goal_reminder)

        growth_info = self.relationship.get_growth_stage_info()
        if growth_info["stage_id"] < 5:
            locked_perms = self.relationship.get_locked_permissions()
            if locked_perms:
                sections.append(f"\n## 🔒 当前阶段锁定权限\n继续互动可以解锁：{', '.join(locked_perms[:3])}")

        return "\n\n".join(sections)

    # ========== 成长阶段系统 ==========

    def record_interaction(self, intimacy_delta: int = 1) -> dict:
        """记录一次互动"""
        result = self.relationship.record_interaction(intimacy_delta=intimacy_delta)
        
        for callback in self._interaction_callbacks:
            try:
                callback(result)
            except Exception:
                pass
        
        return result

    def check_permission(self, permission: str) -> bool:
        """检查指定权限是否已解锁"""
        return self.relationship.check_permission(permission)

    def get_available_permissions(self) -> list:
        """获取当前可用权限列表"""
        return self.relationship.get_available_permissions()

    def get_growth_stage(self) -> dict:
        """获取当前成长阶段信息"""
        return self.relationship.get_growth_stage_info()

    def record_trial(self, trial_type: str, passed: bool, details: str = "") -> None:
        """记录安全考验结果"""
        self.relationship.record_trial(trial_type, passed, details)

    # ========== 查询接口 ==========

    def get_relationship_summary(self) -> dict:
        """获取完整的关系状态摘要"""
        return self.relationship.get_relationship_summary()

    def get_memory_stats(self) -> dict:
        """获取记忆统计"""
        return self.memory.get_stats()

    def search_memory(self, query: str, **kwargs) -> list:
        """搜索记忆"""
        return self.memory.search_memory(query, **kwargs)

    def add_memory(self, content: str, category: str = "general", 
                   importance: int = 3, tags: list = None) -> MemoryEntry:
        """添加记忆"""
        return self.memory.add_to_index(content, category, importance, tags)

    def get_goal_stats(self) -> dict:
        """获取目标统计"""
        return self.goals.get_statistics()

    def get_baby_report(self) -> str:
        """获取宝宝报告"""
        return self.baby.build_baby_report()

    def get_full_status(self) -> dict:
        """获取SoulForge的完整状态"""
        return {
            "name": self.name,
            "relationship": self.get_relationship_summary(),
            "memory": self.memory.get_stats(),
            "goals": self.get_goal_stats(),
            "baby": self.baby.get_statistics(),
            "chat_history_length": len(self._chat_history),
            "prompt_template": self._prompt_template_name,
        }

    def reset(self, keep_memory: bool = False) -> None:
        """重置SoulForge状态"""
        self._chat_history.clear()
        
        if not keep_memory:
            self.memory.clear_working_memory()

    def export_context(self) -> str:
        """导出完整的上下文文本"""
        sections = []
        
        personality = self.relationship.get_personality_prompt()
        if personality:
            sections.append(f"## 👤 人设\n{personality}\n")
        
        rel_summary = self.relationship.get_relationship_summary()
        growth = rel_summary["growth_stage_info"]
        sections.append(f"## 💕 关系状态\n")
        sections.append(f"- 成长阶段：第{growth['stage_id']}阶段 - {growth['name']}")
        sections.append(f"- 亲密度：{rel_summary['intimacy_score']}/100")
        sections.append(f"- 互动次数：{rel_summary['interaction_count']}\n")
        
        memory = self.memory.build_context(include_daily=True, daily_days=7)
        if memory:
            sections.append(f"{memory}\n")
        
        goals = self.goals.build_reminder()
        if goals:
            sections.append(f"{goals}\n")
        
        return "\n".join(sections)


# 便捷函数

def create_soulforge(name: str = "AI", model: str = "claude-sonnet-4-20250514",
                    personality: str = "", api_key: str = "",
                    memory_dir: str = "memory") -> SoulForge:
    """创建SoulForge实例的便捷函数"""
    return SoulForge(
        name=name,
        model=model,
        personality=personality,
        api_key=api_key,
        memory_dir=memory_dir,
    )
