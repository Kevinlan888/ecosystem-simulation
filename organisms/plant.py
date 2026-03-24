"""
植物生物模块

植物通过光照获取能量，使用无性繁殖（分裂）策略。
"""

from core.organism import Organism
from reproduction.asexual import AsexualReproduction


class Plant(Organism):
    """
    植物生物。

    - traits: min_temp=5, max_temp=40, is_plant=True
    - 繁殖策略: 无性繁殖（能量充足时自动分裂）
    - 能量来源: 通过光照因素获得能量（见 LightFactor）
    """

    def __init__(
        self,
        name: str = "Plant",
        health: float = 80.0,
        energy: float = 60.0,
        max_age: int = 30 * 200,   # 植物寿命 30 MC 天
        reproduction_strategy=None,
        traits: dict | None = None,
    ):
        """
        初始化植物实例。

        Args:
            name: 植物名称
            health: 初始健康值
            energy: 初始能量值
            max_age: 最大寿命
            reproduction_strategy: 繁殖策略（默认无性繁殖）
            traits: 生物特征字典（默认植物特征）
        """
        super().__init__(
            name=name,
            health=health,
            energy=energy,
            max_age=max_age,
            reproduction_strategy=reproduction_strategy or AsexualReproduction(),
            traits=traits or {
                "min_temp": 5,
                "max_temp": 40,
                "is_plant": True,
            },
        )

    def step(self, ecosystem) -> list:
        """
        植物的时间步：增龄、消耗能量（更少）、尝试繁殖。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步产生的新生植物列表
        """
        self.age += 1
        # 植物基础能量消耗更少
        self.apply_effect("energy", -0.5)

        offspring = []
        if self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                offspring = self.reproduction_strategy.reproduce(self, ecosystem)
                self._place_offspring(offspring, ecosystem)
        return offspring
