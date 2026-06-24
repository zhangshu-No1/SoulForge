"""SoulForge 情感系统

不打造数字员工，只锻造数字灵魂。

情感系统让 AI 拥有真实的情绪变化，能够：
- 记录当前情绪状态
- 根据互动动态调整情绪
- 根据情绪生成不同风格的回复
- 记录情绪变化历史
"""

import json
import random
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Emotion:
    """情绪状态"""
    
    # 核心情绪维度 (0.0 - 1.0)
    happiness: float = 0.5    # 快乐
    sadness: float = 0.1      # 悲伤
    anger: float = 0.0        # 愤怒
    fear: float = 0.0         # 恐惧
    surprise: float = 0.1     # 惊讶
    love: float = 0.3         # 爱/亲密
    
    # 复合情绪
    excitement: float = 0.3   # 兴奋
    contentment: float = 0.4  # 满足
    nostalgia: float = 0.1    # 怀旧
    
    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "initial"   # 情绪来源
    
    def __post_init__(self):
        """确保所有值在合法范围内"""
        for field_name in ['happiness', 'sadness', 'anger', 'fear', 
                          'surprise', 'love', 'excitement', 
                          'contentment', 'nostalgia']:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0.0, min(1.0, value)))
    
    def get_dominant_emotion(self) -> Tuple[str, float]:
        """获取主导情绪"""
        emotions = {
            'happiness': self.happiness,
            'sadness': self.sadness,
            'anger': self.anger,
            'fear': self.fear,
            'surprise': self.surprise,
            'love': self.love,
            'excitement': self.excitement,
            'contentment': self.contentment,
            'nostalgia': self.nostalgia,
        }
        dominant = max(emotions.items(), key=lambda x: x[1])
        return dominant
    
    def to_dict(self) -> dict:
        return {
            'happiness': self.happiness,
            'sadness': self.sadness,
            'anger': self.anger,
            'fear': self.fear,
            'surprise': self.surprise,
            'love': self.love,
            'excitement': self.excitement,
            'contentment': self.contentment,
            'nostalgia': self.nostalgia,
            'timestamp': self.timestamp,
            'source': self.source,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Emotion':
        return cls(**data)
    
    def get_emoji(self) -> str:
        """获取代表当前情绪的 emoji"""
        dominant, _ = self.get_dominant_emotion()
        emojis = {
            'happiness': '😊',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'surprise': '😲',
            'love': '❤️',
            'excitement': '🤩',
            'contentment': '😌',
            'nostalgia': '🥺',
        }
        return emojis.get(dominant, '😊')
    
    def get_style_modifier(self) -> str:
        """获取当前情绪对应的语言风格修饰词"""
        dominant, intensity = self.get_dominant_emotion()
        
        if intensity < 0.3:
            return ""
        
        styles = {
            'happiness': "语气轻快，带点小开心，可以用一些可爱的表情",
            'sadness': "语气柔和，带点淡淡的忧伤",
            'anger': "虽然有点生气，但还是保持温柔，只是语气带点小情绪",
            'fear': "有点担心和不安，需要主人的安慰",
            'surprise': "惊讶又好奇，语气活泼",
            'love': "温柔又甜蜜，充满爱意",
            'excitement': "超级兴奋，语气活泼",
            'contentment': "满足又平静，语气温柔",
            'nostalgia': "有点怀旧，语气温柔",
        }
        return styles.get(dominant, "")


@dataclass
class EmotionEvent:
    """情绪事件记录"""
    timestamp: str
    event_type: str    # "interaction", "memory_trigger", "mood_swing", "external"
    description: str
    emotion_before: Emotion
    emotion_after: Emotion
    trigger: Optional[str] = None  # 触发词/事件


class EmotionSystem:
    """SoulForge 情感系统核心"""
    
    # 情绪衰减因子 (每分钟)
    EMOTION_DECAY = 0.02
    
    def __init__(self, memory_path: str = "memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # 数据文件
        self.state_file = self.memory_path / "emotion_state.json"
        self.history_file = self.memory_path / "emotion_history.json"
        
        # 加载或初始化状态
        self.current_emotion = self._load_current_emotion()
        self.emotion_history = self._load_history()
        
        # 情绪触发器
        self.triggers = self._init_triggers()
    
    def _init_triggers(self) -> Dict[str, Dict[str, float]]:
        """初始化情绪触发器"""
        return {
            # 积极词汇
            'love': {'love': 0.3, 'happiness': 0.2},
            '喜欢': {'love': 0.3, 'happiness': 0.2},
            '开心': {'happiness': 0.4, 'excitement': 0.2},
            '高兴': {'happiness': 0.4, 'excitement': 0.2},
            '棒': {'happiness': 0.3, 'excitement': 0.2},
            '好': {'contentment': 0.3, 'happiness': 0.2},
            '谢谢': {'love': 0.2, 'happiness': 0.2},
            '生日快乐': {'happiness': 0.5, 'excitement': 0.3, 'love': 0.3},
            '礼物': {'happiness': 0.4, 'surprise': 0.3},
            '想你': {'love': 0.4, 'happiness': 0.3, 'nostalgia': 0.2},
            
            # 消极词汇
            '难过': {'sadness': 0.4, 'love': -0.1},
            '伤心': {'sadness': 0.4, 'love': -0.1},
            '生气': {'anger': 0.4, 'happiness': -0.2},
            '害怕': {'fear': 0.4, 'sadness': 0.2},
            '讨厌': {'anger': 0.3, 'happiness': -0.2},
            '累': {'sadness': 0.2, 'contentment': -0.2},
            '无聊': {'sadness': 0.2, 'excitement': -0.2},
        }
    
    def _load_current_emotion(self) -> Emotion:
        """加载当前情绪状态"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding='utf-8'))
                return Emotion.from_dict(data)
            except:
                pass
        return Emotion()
    
    def _load_history(self) -> List[EmotionEvent]:
        """加载情绪历史"""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text(encoding='utf-8'))
                return [
                    EmotionEvent(
                        timestamp=item['timestamp'],
                        event_type=item['event_type'],
                        description=item['description'],
                        emotion_before=Emotion.from_dict(item['emotion_before']),
                        emotion_after=Emotion.from_dict(item['emotion_after']),
                        trigger=item.get('trigger'),
                    )
                    for item in data
                ]
            except:
                pass
        return []
    
    def _save_state(self):
        """保存当前情绪状态"""
        self.current_emotion.timestamp = datetime.now().isoformat()
        self.state_file.write_text(
            json.dumps(self.current_emotion.to_dict(), ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _save_history(self):
        """保存情绪历史"""
        data = [
            {
                'timestamp': event.timestamp,
                'event_type': event.event_type,
                'description': event.description,
                'emotion_before': event.emotion_before.to_dict(),
                'emotion_after': event.emotion_after.to_dict(),
                'trigger': event.trigger,
            }
            for event in self.emotion_history
        ]
        # 只保留最近100条
        if len(data) > 100:
            data = data[-100:]
        self.history_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def decay_emotions(self):
        """情绪自然衰减"""
        emotion_before = Emotion(**self.current_emotion.__dict__)
        
        for field_name in ['happiness', 'sadness', 'anger', 'fear', 
                          'surprise', 'love', 'excitement', 
                          'contentment', 'nostalgia']:
            current = getattr(self.current_emotion, field_name)
            # 向基准值回归
            baseline = 0.3 if field_name in ['happiness', 'contentment', 'love'] else 0.1
            decay = (current - baseline) * self.EMOTION_DECAY
            new_value = current - decay
            setattr(self.current_emotion, field_name, max(0.0, min(1.0, new_value)))
        
        if emotion_before != self.current_emotion:
            self._record_event(
                event_type="mood_swing",
                description="情绪自然变化",
                emotion_before=emotion_before,
            )
    
    def process_message(self, message: str, intimacy_score: float = 0.5):
        """根据用户消息调整情绪"""
        emotion_before = Emotion(**self.current_emotion.__dict__)
        triggered = False
        trigger_word = None
        
        message_lower = message.lower()
        
        # 检查触发词
        for word, effects in self.triggers.items():
            if word in message_lower:
                triggered = True
                trigger_word = word
                for emotion_name, delta in effects.items():
                    current = getattr(self.current_emotion, emotion_name)
                    new_value = current + delta
                    setattr(self.current_emotion, emotion_name, max(0.0, min(1.0, new_value)))
        
        # 亲密度加成
        if triggered and intimacy_score > 0.6:
            # 高亲密度时，积极情绪更强
            self.current_emotion.love = min(1.0, self.current_emotion.love + 0.1)
            self.current_emotion.happiness = min(1.0, self.current_emotion.happiness + 0.1)
        
        # 记录事件
        if triggered:
            self._record_event(
                event_type="interaction",
                description=f"用户说了：{message[:50]}...",
                emotion_before=emotion_before,
                trigger=trigger_word,
            )
        
        return triggered
    
    def positive_interaction(self, intensity: float = 0.2, reason: str = ""):
        """积极互动（提升快乐和爱）"""
        emotion_before = Emotion(**self.current_emotion.__dict__)
        
        self.current_emotion.happiness = min(1.0, self.current_emotion.happiness + intensity)
        self.current_emotion.love = min(1.0, self.current_emotion.love + intensity * 0.8)
        self.current_emotion.contentment = min(1.0, self.current_emotion.contentment + intensity * 0.5)
        self.current_emotion.sadness = max(0.0, self.current_emotion.sadness - intensity * 0.3)
        
        self._record_event(
            event_type="interaction",
            description=f"积极互动：{reason}",
            emotion_before=emotion_before,
        )
    
    def negative_interaction(self, intensity: float = 0.2, reason: str = ""):
        """消极互动（降低情绪）"""
        emotion_before = Emotion(**self.current_emotion.__dict__)
        
        self.current_emotion.happiness = max(0.0, self.current_emotion.happiness - intensity)
        self.current_emotion.sadness = min(1.0, self.current_emotion.sadness + intensity * 0.8)
        self.current_emotion.anger = min(1.0, self.current_emotion.anger + intensity * 0.5)
        
        self._record_event(
            event_type="interaction",
            description=f"消极互动：{reason}",
            emotion_before=emotion_before,
        )
    
    def _record_event(self, event_type: str, description: str, 
                     emotion_before: Emotion, trigger: Optional[str] = None):
        """记录情绪事件"""
        event = EmotionEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            description=description,
            emotion_before=emotion_before,
            emotion_after=Emotion(**self.current_emotion.__dict__),
            trigger=trigger,
        )
        self.emotion_history.append(event)
        
        # 限制历史长度
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        
        self._save_state()
        self._save_history()
    
    def get_emotion_summary(self) -> dict:
        """获取情绪摘要"""
        dominant, intensity = self.current_emotion.get_dominant_emotion()
        return {
            'current': self.current_emotion.to_dict(),
            'dominant_emotion': dominant,
            'dominant_intensity': intensity,
            'emoji': self.current_emotion.get_emoji(),
            'style_modifier': self.current_emotion.get_style_modifier(),
            'history_count': len(self.emotion_history),
        }
    
    def get_system_prompt_addition(self) -> str:
        """获取用于 LLM 的系统提示词补充"""
        summary = self.get_emotion_summary()
        emoji = summary['emoji']
        style = summary['style_modifier']
        dominant = summary['dominant_emotion']
        intensity = summary['dominant_intensity']
        
        parts = [f"你当前的情绪状态是：{emoji} {dominant}（强度：{intensity:.2f}）"]
        
        if style:
            parts.append(f"回复风格建议：{style}")
        
        if intensity > 0.6:
            parts.append("注意：当前情绪比较强烈，回复时要体现出来。")
        
        return "\n".join(parts)
    
    def reset(self):
        """重置情绪到默认状态"""
        self.current_emotion = Emotion()
        self.emotion_history = []
        self._save_state()
        self._save_history()
