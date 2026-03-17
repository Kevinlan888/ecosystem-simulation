"""
水资源因素模块

模拟水资源的消耗与恢复。能量低于阈值且水资源不足时，额外扣除健康值。
"""

from core.interfaces import EnvironmentalFactor


class WaterFactor(EnvironmentalFactor):
    """
    水资源环境因素。

    - 所有生物若能量低于阈值且水资源不足，则额外扣除健康值。
    - 每步水位缓慢恢复。
    """

    def __init__(
        self,
        initial_level: float = 150.0,
        regen_rate: float = 5.0,
        max_level: float = 300.0,
        consumption_per_organism: float = 1.0,
        low_water_threshold: float = 30.0,
        energy_threshold: float = 40.0,
        health_penalty: float = 3.0,
    ):
        """
        初始化水资源因素。

        Args:
            initial_level: 初始水位
            regen_rate: 每步水位再生量
            max_level: 最大水位
            consumption_per_organism: 每个生物每步消耗水量
            low_water_threshold: 低水位警戒线
            energy_threshold: 能量低于此值时才受水资源不足影响
            health_penalty: 缺水时每步扣除的健康值
        """
        self._name = "water"
        self.water_level: float = initial_level
        self.regen_rate: float = regen_rate
        self.max_level: float = max_level
        self.consumption_per_organism: float = consumption_per_organism
        self.low_water_threshold: float = low_water_threshold
        self.energy_threshold: float = energy_threshold
        self.health_penalty: float = health_penalty

    @property
    def name(self) -> str:
        """环境因素名称。"""
        return self._name

    def update(self, ecosystem) -> None:
        """
        每步水位缓慢恢复（不超过上限）。

        Args:
            ecosystem: 当前生态系统实例
        """
        self.water_level = min(self.max_level, self.water_level + self.regen_rate)

    def apply(self, organism, ecosystem) -> None:
        """
        所有生物消耗水资源；若能量低于阈值且水资源不足，扣除健康值。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """
        # 消耗水资源
        if self.water_level >= self.consumption_per_organism:
            self.water_level -= self.consumption_per_organism
        else:
            # 水资源不足，且能量较低时影响健康
            if organism.energy < self.energy_threshold:
                organism.apply_effect("health", -self.health_penalty)

    def __repr__(self) -> str:
        return f"WaterFactor(water_level={self.water_level:.1f})"
