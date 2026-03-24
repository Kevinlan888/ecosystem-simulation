"""
捕食者生物模块

捕食者通过捕食草食动物获取能量，使用有性繁殖策略。
"""

from core.organism import Organism
from reproduction.sexual import SexualReproduction
from intelligence.neural_brain import NeuralBrain


class Predator(Organism):
    """
    捕食者生物。

    - traits: min_temp=-5, max_temp=40, is_plant=False, is_predator=True
    - 繁殖策略: 有性繁殖
    - 能量来源: 捕食草食动物获得能量（在 step() 中实现捕食逻辑）
    - 大脑: 默认携带 NeuralBrain，支持神经网络决策
    """

    def __init__(
        self,
        name: str = "Predator",
        health: float = 90.0,
        energy: float = 80.0,
        max_age: int = 200 * 200,  # 捕食者寿命 200 MC 天
        reproduction_strategy=None,
        traits: dict | None = None,
        hunt_energy_gain: float = 30.0,
        hunt_chance: float = 0.4,
        brain=None,
    ):
        """
        初始化捕食者实例。

        Args:
            name: 捕食者名称
            health: 初始健康值
            energy: 初始能量值
            max_age: 最大寿命
            reproduction_strategy: 繁殖策略（默认有性繁殖）
            traits: 生物特征字典（默认捕食者特征）
            hunt_energy_gain: 成功捕猎后获得的能量值
            hunt_chance: 每步捕猎成功概率
            brain: 大脑实例（默认 NeuralBrain）
        """
        super().__init__(
            name=name,
            health=health,
            energy=energy,
            max_age=max_age,
            reproduction_strategy=reproduction_strategy or SexualReproduction(min_age=20 * 200),  # 20 MC 天成熟
            traits=traits or {
                "min_temp": -5,
                "max_temp": 40,
                "is_plant": False,
                "is_predator": True,
            },
            brain=brain if brain is not None else NeuralBrain(),
            speed=3.0,
        )
        self.hunt_energy_gain = hunt_energy_gain
        self.hunt_chance = hunt_chance

    def step(self, ecosystem) -> list:
        """
        捕食者的时间步：本能追猎优先，神经网络辅助调参。

        行为层级：
        1. 本能层（硬编码）：饥饿时直线追最近猎物，无猎物时随机游走
        2. 神经层：大脑影响追猎速度增益和繁殖意愿
        3. 捕猎：进入 hunt_radius 内有概率击中猎物
        4. 繁殖：有猎物且满足条件时尝试繁殖
        """
        import math
        import random

        # 1. 神经网络感知与决策（用于速度增益等辅助参数）
        self.think(ecosystem)
        offspring = []

        self.age += 1
        energy_cost = 0.75 if getattr(self, "_resting", False) else 1.5
        self._resting = False
        self.apply_effect("energy", -energy_cost)

        # 2. 收集猎物列表
        prey_list = [
            o for o in ecosystem.organisms
            if o.traits.get("is_herbivore", False) and o.is_alive() and o.x is not None
        ]

        # 3. 本能追猎移动（不依赖神经网络决策，饥饿时必然行动）
        if self.x is not None:
            w, h = ecosystem.world_size
            if prey_list and self.energy < 80:
                # 找到最近猎物，直线追击
                nearest = min(prey_list, key=lambda o: math.hypot(o.x - self.x, o.y - self.y))
                dist = math.hypot(nearest.x - self.x, nearest.y - self.y)
                if dist > 0:
                    # 神经网络 decisions[0] 影响追猎速度 (0.8x ~ 1.3x)
                    speed_boost = 0.8 + max(0.0, self.decisions[0]) * 0.5
                    move_dist = min(self.speed * speed_boost, dist)
                    self.x = max(0.0, min(w, self.x + (nearest.x - self.x) / dist * move_dist))
                    self.y = max(0.0, min(h, self.y + (nearest.y - self.y) / dist * move_dist))
            else:
                # 吃饱或无猎物时随机游走巡逻
                angle = random.uniform(0.0, 6.2832)
                self.x = max(0.0, min(w, self.x + math.cos(angle) * self.speed * 0.4))
                self.y = max(0.0, min(h, self.y + math.sin(angle) * self.speed * 0.4))

        # 4. 捕猎：进入捕猎半径内概率击中
        hunt_radius = 8.0
        nearby_prey = [
            o for o in prey_list
            if math.hypot(o.x - self.x, o.y - self.y) <= hunt_radius
        ] if self.x is not None else []

        if self.is_alive() and nearby_prey:
            # 能量低于阈值时才真正捕杀（饱食机制）
            if self.energy < 65 and random.random() < self.hunt_chance:
                prey = min(nearby_prey, key=lambda o: math.hypot(o.x - self.x, o.y - self.y))
                prey.apply_effect("health", -30.0)
                gain = self.hunt_energy_gain * (0.8 + max(0.0, self.decisions[0]) * 0.4)
                self.apply_effect("energy", gain)

        # 5. 饥饿死亡惩罚：无猎物时扣血
        if self.is_alive() and not prey_list:
            self.apply_effect("health", -3.0)

        # 6. 繁殖（有猎物且成熟）
        if prey_list and self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                new_kids = self.reproduction_strategy.reproduce(self, ecosystem)
                self._place_offspring(new_kids, ecosystem)
                self.offspring_count += len(new_kids)
                offspring.extend(new_kids)
        return offspring
