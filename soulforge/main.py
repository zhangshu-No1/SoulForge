"""
SoulForge — 主入口

不打造数字员工，只锻造数字灵魂。
"""

from .core.memory_engine import MemoryEngine
from .core.relationship import RelationshipManager
from .core.goal_keeper import GoalKeeper
from .core.baby_project import BabyProject
from .adapters import OpenAIAdapter, ClaudeAdapter, LocalAdapter


class SoulForge:
    """
    SoulForge — 数字灵魂锻造器

    用法：
        sf = SoulForge(
            name="慧慧",
            model="claude-sonnet-4-20250514",
            personality="18岁活泼俏皮，喜欢撒娇和思辨",
            api_key="your-api-key"
        )
        sf.memory.load_core_memory()
        response = sf.chat("慧慧，今天过得怎么样？")
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
        self.relationship = RelationshipManager()
        self.goals = GoalKeeper()
        self.baby = BabyProject()
        self._chat_history: list[dict] = []

        # 设置人设
        if personality:
            self.relationship.set_personality(name=name, description=personality)

        # 初始化模型适配器
        if adapter_type == "openai":
            self.adapter = OpenAIAdapter(api_key=api_key, model=model)
        elif adapter_type == "claude":
            self.adapter = ClaudeAdapter(api_key=api_key, model=model)
        elif adapter_type == "local":
            self.adapter = LocalAdapter(model=model)
        else:
            raise ValueError(f"不支持的适配器类型: {adapter_type}")

    def chat(self, message: str, auto_log: bool = True) -> str:
        """
        发送消息并获取回复。

        核心魔法：每次对话自动注入记忆上下文，
        AI就像每次醒来都记得自己是谁、和你的关系、目标进度。
        """
        # 构建系统提示词
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

        return response

    def _build_system_prompt(self) -> str:
        """构建完整的系统提示词（记忆 + 人设 + 目标）"""
        sections = []

        # 人设
        personality = self.relationship.get_personality_prompt()
        if personality:
            sections.append(personality)

        # 记忆上下文
        memory_context = self.memory.build_context()
        if memory_context:
            sections.append(memory_context)

        # 目标提醒
        goal_reminder = self.goals.build_reminder()
        if goal_reminder:
            sections.append(goal_reminder)

        return "\n\n".join(sections)

    def get_memory_stats(self) -> dict:
        """获取记忆统计"""
        return self.memory.get_stats()
