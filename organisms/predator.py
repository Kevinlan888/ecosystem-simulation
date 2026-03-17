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
        max_age: int = 50,
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
            reproduction_strategy=reproduction_strategy or SexualReproduction(),
            traits=traits or {
                "min_temp": -5,
                "max_temp": 40,
                "is_plant": False,
                "is_predator": True,
            },
            brain=brain if brain is not None else NeuralBrain(),
        )
        self.hunt_energy_gain = hunt_energy_gain
        self.hunt_chance = hunt_chance

    def step(self, ecosystem) -> list:
        """
        捕食者的时间步：感知、决策、行动、增龄、消耗能量、尝试捕猎、尝试繁殖。

        在原有捕猎逻辑之前插入大脑驱动的 think() 和 act()。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步产生的新生捕食者列表
        """
        import random

        # 1. 感知与决策
        self.think(ecosystem)
        # 2. 执行行动（act 可能产生后代）
        offspring = self.act(ecosystem)

        self.age += 1
        # 基础能量消耗（休息时减半）
        energy_cost = 0.75 if getattr(self, "_resting", False) else 1.5
        self._resting = False
        self.apply_effect("energy", -energy_cost)

        prey_list = [
            o for o in ecosystem.organisms
            if o.traits.get("is_herbivore", False) and o.is_alive()
        ]

        # 核心机制：只在饥饿时捕猎（饱食后停止，防止将猎物全部捕杀）
        if self.is_alive() and self.energy < 65:
            if prey_list and random.random() < self.hunt_chance:
                prey = random.choice(prey_list)
                prey.apply_effect("health", -30.0)
                self.apply_effect("energy", self.hunt_energy_gain)

        # 饥饿惩罚：无猎物时每步额外扣血（模拟饿死），迫使捕食者随猎物减少而衰亡
        if self.is_alive() and not prey_list:
            self.apply_effect("health", -3.0)

        # 繁殖必须有猎物存在（无食物来源无法支撑后代）
        if prey_list and self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                offspring.extend(self.reproduction_strategy.reproduce(self, ecosystem))
        return offspring
