"""
光照因素模块

模拟昼夜循环的光照强度变化，仅影响植物的能量（光合作用）。
"""

import math
from core.interfaces import EnvironmentalFactor


class LightFactor(EnvironmentalFactor):
    """
    光照环境因素。

    - 光照强度按昼夜周期（正弦函数）在 [0, 1] 范围内变化。
    - 仅影响 traits['is_plant'] == True 的生物：
        - 光照充足（> 0.5）：植物能量恢复
        - 光照不足（<= 0.5）：植物能量下降
    """

    def __init__(
        self,
        day_length: int = 12,
        energy_gain: float = 3.0,
        energy_loss: float = 1.0,
    ):
        """
        初始化光照因素。

        Args:
            day_length: 白天持续的 tick 数（一个完整昼夜 = day_length * 2）
            energy_gain: 光照充足时每步植物能量恢复量
            energy_loss: 光照不足时每步植物能量减少量
        """
        self._name = "light"
        self.day_length = day_length
        self.energy_gain = energy_gain
        self.energy_loss = energy_loss
        self.intensity: float = 0.0

    @property
    def name(self) -> str:
        """环境因素名称。"""
        return self._name

    def update(self, ecosystem) -> None:
        """
        按昼夜周期更新光照强度（正弦函数映射到 [0, 1]）。

        Args:
            ecosystem: 当前生态系统实例
        """
        period = self.day_length * 2
        self.intensity = (math.sin(2 * math.pi * ecosystem.tick / period) + 1) / 2

    def apply(self, organism, ecosystem) -> None:
        """
        仅对植物施加光照影响：充足时恢复能量，不足时消耗能量。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """
        if not organism.traits.get("is_plant", False):
            return

        if self.intensity > 0.5:
            organism.apply_effect("energy", self.energy_gain)
        else:
            organism.apply_effect("energy", -self.energy_loss)

    def __repr__(self) -> str:
        return f"LightFactor(intensity={self.intensity:.2f})"
