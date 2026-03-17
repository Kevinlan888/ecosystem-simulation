"""
捕食者生物模块

捕食者通过捕食草食动物获取能量，使用有性繁殖策略。
"""

from core.organism import Organism
from reproduction.sexual import SexualReproduction


class Predator(Organism):
    """
    捕食者生物。

    - traits: min_temp=-5, max_temp=40, is_plant=False, is_predator=True
    - 繁殖策略: 有性繁殖
    - 能量来源: 捕食草食动物获得能量（在 step() 中实现捕食逻辑）
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
        )
        self.hunt_energy_gain = hunt_energy_gain
        self.hunt_chance = hunt_chance

    def step(self, ecosystem) -> list:
        """
        捕食者的时间步：增龄、消耗能量、尝试捕猎、尝试繁殖。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步产生的新生捕食者列表
        """
        import random

        self.age += 1
        # 基础能量消耗
        self.apply_effect("energy", -1.5)

        # 尝试捕猎草食动物
        if self.is_alive():
            prey_list = [
                o for o in ecosystem.organisms
                if o.traits.get("is_herbivore", False) and o.is_alive()
            ]
            if prey_list and random.random() < self.hunt_chance:
                prey = random.choice(prey_list)
                # 捕食：猎物失去大量健康，捕食者获得能量
                prey.apply_effect("health", -50.0)
                self.apply_effect("energy", self.hunt_energy_gain)

        offspring = []
        if self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                offspring = self.reproduction_strategy.reproduce(self, ecosystem)
        return offspring
