"""
生物基类模块

定义 Organism 基类，所有生物（植物、草食动物、捕食者等）都继承自此类。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.ecosystem import Ecosystem

from intelligence.no_brain import NoBrain


class Organism:
    """
    生物基类。

    封装所有生物共有的属性和行为：年龄、健康、能量、繁殖策略、大脑等。
    """

    def __init__(
        self,
        name: str,
        health: float = 100.0,
        energy: float = 100.0,
        max_age: int = 50,
        reproduction_strategy=None,
        traits: dict | None = None,
        brain=None,
    ):
        """
        初始化生物实例。

        Args:
            name: 物种名称
            health: 初始健康值（0.0 ~ 100.0）
            energy: 初始能量值（0.0 ~ 100.0）
            max_age: 最大寿命（超过则死亡）
            reproduction_strategy: 繁殖策略实例（ReproductionStrategy 子类）
            traits: 生物特征字典，用于环境因素判断
            brain: 大脑实例（BaseBrain 子类），默认使用 NoBrain
        """
        self.name: str = name
        self.age: int = 0
        self.health: float = max(0.0, min(100.0, health))
        self.energy: float = max(0.0, min(100.0, energy))
        self.max_age: int = max_age
        self.reproduction_strategy = reproduction_strategy
        self.traits: dict = traits or {}
        self.brain = brain if brain is not None else NoBrain()
        self.fitness_score: float = 0.0
        self.decisions: list = [0.5, 0.5, 0.5, 0.5]
        self._resting: bool = False  # 标记本步是否休息（由 act() 设置）

    # ------------------------------------------------------------------
    # 核心方法
    # ------------------------------------------------------------------

    def sense(self, ecosystem: "Ecosystem") -> list:
        """
        感知环境，生成神经网络输入向量（8维）。

        从 ecosystem 中获取：最近食物距离、捕食者距离、同类距离、温度、水资源。
        若找不到对应信息，默认返回 1.0（最远/最差）。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 长度为 8 的感知输入向量
        """
        # 自身状态（归一化）
        energy_norm = self.energy / 100.0
        health_norm = self.health / 100.0
        age_ratio = self.age / max(1, self.max_age)

        # 最近食物距离：以种群中植物比例近似（值越小表示食物越丰富，感知距离越近）
        plants = [o for o in ecosystem.organisms if o.traits.get("is_plant", False) and o.is_alive()]
        nearest_food = 1.0 - (len(plants) / max(1, len(ecosystem.organisms)))

        # 最近捕食者距离：以种群中捕食者比例近似（值越小表示捕食者越多，威胁越大）
        predators = [o for o in ecosystem.organisms if o.traits.get("is_predator", False) and o.is_alive()]
        nearest_predator = 1.0 - (len(predators) / max(1, len(ecosystem.organisms)))

        # 最近同类距离：以同名物种比例近似（值越小表示同类越多，越容易找到伴侣）
        same_species = [o for o in ecosystem.organisms if o.name == self.name and o is not self and o.is_alive()]
        nearest_mate = 1.0 - (len(same_species) / max(1, len(ecosystem.organisms)))

        # 当前温度（从环境因素中获取）
        temp_factor = next((f for f in ecosystem.factors if f.name == "temperature"), None)
        current_temp = temp_factor.current_temp if temp_factor is not None else 25.0
        temp_norm = current_temp / 50.0

        # 水资源（从环境因素中获取）
        water_factor = next((f for f in ecosystem.factors if f.name == "water"), None)
        water_norm = (water_factor.water_level / water_factor.max_level) if water_factor is not None else 1.0

        return [
            energy_norm,
            health_norm,
            age_ratio,
            nearest_food,
            nearest_predator,
            nearest_mate,
            temp_norm,
            water_norm,
        ]

    def think(self, ecosystem: "Ecosystem") -> None:
        """
        调用 brain.decide()，将感知输入转化为决策，更新 self.decisions。

        Args:
            ecosystem: 当前生态系统实例
        """
        inputs = self.sense(ecosystem)
        self.decisions = self.brain.decide(inputs)

    def act(self, ecosystem: "Ecosystem") -> list:
        """
        根据 self.decisions 执行行动，返回新生生物列表。

        行动规则：
        - decisions[0] > 0.5: 趋向食物（能量+5，概率性）
        - decisions[1] > 0.5: 逃离捕食者（健康+3）
        - decisions[2] > 0.5: 寻找伴侣（调用繁殖策略）
        - decisions[3] > 0.5: 休息（标记本步能耗减半，通过 _resting 属性传递）

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步通过主动求偶产生的新生生物列表
        """
        offspring = []
        d = self.decisions

        # 趋向食物：寻找植物获取额外能量
        if d[0] > 0.5:
            plants = [o for o in ecosystem.organisms if o.traits.get("is_plant", False) and o.is_alive()]
            if plants:
                self.apply_effect("energy", 5.0)

        # 逃离捕食者：存在捕食者时减少受害概率（健康微增）
        if d[1] > 0.5:
            predators = [o for o in ecosystem.organisms if o.traits.get("is_predator", False) and o.is_alive()]
            if predators:
                self.apply_effect("health", 3.0)

        # 寻找伴侣：主动触发繁殖（捕食者在 Predator.step() 中单独处理，此处跳过）
        if d[2] > 0.5 and not self.traits.get("is_predator", False):
            if self.reproduction_strategy and self.is_alive():
                if self.reproduction_strategy.can_reproduce(self):
                    offspring.extend(self.reproduction_strategy.reproduce(self, ecosystem))

        # 休息：标记本步休息，step() 中将能耗减半
        self._resting = d[3] > 0.5

        return offspring

    def step(self, ecosystem: "Ecosystem") -> list:
        """
        执行一个时间步：感知、决策、行动、增龄、消耗基础能量、尝试繁殖。

        在原有逻辑之前插入 think() 和 act()，其余逻辑（年龄增加、
        死亡判断、繁殖等）保持不变。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步产生的新生生物列表
        """
        # 1. 感知与决策
        self.think(ecosystem)
        # 2. 执行行动（act 可能产生后代，并在 decisions[2]>0.5 时已触发繁殖）
        offspring = self.act(ecosystem)

        self.age += 1
        # 基础能量消耗（休息时减半）
        energy_cost = 0.5 if getattr(self, "_resting", False) else 1.0
        self._resting = False
        self.apply_effect("energy", -energy_cost)

        # 仅当大脑未主动寻找伴侣时，才由 step() 触发繁殖（向后兼容 NoBrain）。
        # 若 decisions[2] > 0.5，act() 已调用过繁殖策略，此处跳过以防重复繁殖。
        if self.decisions[2] <= 0.5 and self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                offspring.extend(self.reproduction_strategy.reproduce(self, ecosystem))
        return offspring

    def is_alive(self) -> bool:
        """
        判断生物是否存活。

        Returns:
            bool: 健康值 > 0 且能量 > 0 且年龄未超过最大寿命
        """
        return self.health > 0 and self.energy > 0 and self.age <= self.max_age

    def apply_effect(self, attribute: str, delta: float) -> None:
        """
        通用属性修改接口，方便环境因素调用。

        仅修改 health 和 energy，并将其限制在 [0.0, 100.0] 范围内。

        Args:
            attribute: 属性名称，支持 'health' 和 'energy'
            delta: 变化量（正值为增加，负值为减少）
        """
        if attribute not in ("health", "energy"):
            return
        current = getattr(self, attribute)
        setattr(self, attribute, max(0.0, min(100.0, current + delta)))

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"age={self.age}, health={self.health:.1f}, energy={self.energy:.1f})"
        )
