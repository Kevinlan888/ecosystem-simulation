"""
草食动物生物模块

草食动物通过食物供应获取能量，使用有性繁殖策略。
"""

import math
import random

from core.organism import Organism
from reproduction.sexual import SexualReproduction
from intelligence.neural_brain import NeuralBrain


class Herbivore(Organism):
    """
    草食动物生物。

    - traits: min_temp=0, max_temp=35, is_plant=False, is_herbivore=True
    - 繁殖策略: 有性繁殖（周围有同类时繁殖）
    - 能量来源: 通过食物供应因素获得能量（见 FoodSupplyFactor）
    - 大脑: 默认携带 NeuralBrain，支持神经网络决策
    """

    def __init__(
        self,
        name: str = "Herbivore",
        health: float = 100.0,
        energy: float = 85.0,
        max_age: int = 100 * 200,  # 草食动物寿命 100 MC 天
        reproduction_strategy=None,
        traits: dict | None = None,
        brain=None,
    ):
        """
        初始化草食动物实例。

        Args:
            name: 动物名称
            health: 初始健康值
            energy: 初始能量值
            max_age: 最大寿命
            reproduction_strategy: 繁殖策略（默认有性繁殖）
            traits: 生物特征字典（默认草食动物特征）
            brain: 大脑实例（默认 NeuralBrain）
        """
        super().__init__(
            name=name,
            health=health,
            energy=energy,
            max_age=max_age,
            reproduction_strategy=reproduction_strategy or SexualReproduction(min_age=10 * 200),  # 10 MC 天成熟
            traits=traits or {
                "min_temp": 0,
                "max_temp": 35,
                "is_plant": False,
                "is_herbivore": True,
            },
            brain=brain if brain is not None else NeuralBrain(),
            speed=2.0,
        )

    def step(self, ecosystem) -> list:
        """草食动物时间步：感知决策、增龄耗能、饥饿觅食植物（真实食物链）、繁殖。"""
        self.think(ecosystem)
        offspring = self.act(ecosystem)

        self.age += 1
        energy_cost = 0.5 if getattr(self, "_resting", False) else 1.0
        self._resting = False
        self.apply_effect("energy", -energy_cost)

        # 核心机制：饥饿时进食 eat_radius 内最近的植物（空间耦合）
        eat_radius = 8.0
        if self.energy < 70 and self.is_alive():
            nearby_plants = [
                o for o in ecosystem.organisms
                if o.traits.get("is_plant", False) and o.is_alive()
                and o.x is not None
                and math.hypot(o.x - self.x, o.y - self.y) <= eat_radius
            ]
            if nearby_plants:
                plant = min(nearby_plants, key=lambda o: math.hypot(o.x - self.x, o.y - self.y))
                plant.apply_effect("health", -25.0)
                # 大脑食物意愿越强，进食收益越高（10~30 energy）
                gain = 10.0 + self.decisions[0] * 20.0
                self.apply_effect("energy", gain)

        if self.decisions[2] <= 0.5 and self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                new_kids = self.reproduction_strategy.reproduce(self, ecosystem)
                self._place_offspring(new_kids, ecosystem)
                self.offspring_count += len(new_kids)
                offspring.extend(new_kids)
        return offspring
