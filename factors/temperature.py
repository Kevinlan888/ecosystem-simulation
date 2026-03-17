"""
温度因素模块

模拟季节性温度变化（正弦波），温度超出生物耐受范围时扣除健康值。
"""

import math
from core.interfaces import EnvironmentalFactor


class TemperatureFactor(EnvironmentalFactor):
    """
    温度环境因素。

    - 当前温度按正弦函数随时间周期性波动，模拟四季变化。
    - 若生物 traits 中定义了 min_temp / max_temp，超出范围则扣健康。
    """

    def __init__(
        self,
        base_temp: float = 20.0,
        amplitude: float = 15.0,
        period: int = 40,
        damage_per_degree: float = 0.5,
    ):
        """
        初始化温度因素。

        Args:
            base_temp: 基准温度（°C）
            amplitude: 温度波动幅度（°C）
            period: 一个季节周期所需 tick 数
            damage_per_degree: 每超出 1°C 扣除的健康值
        """
        self._name = "temperature"
        self.base_temp = base_temp
        self.amplitude = amplitude
        self.period = period
        self.damage_per_degree = damage_per_degree
        self.current_temp: float = base_temp

    @property
    def name(self) -> str:
        """环境因素名称。"""
        return self._name

    def update(self, ecosystem) -> None:
        """
        按正弦函数更新当前温度。

        Args:
            ecosystem: 当前生态系统实例
        """
        self.current_temp = self.base_temp + self.amplitude * math.sin(
            2 * math.pi * ecosystem.tick / self.period
        )

    def apply(self, organism, ecosystem) -> None:
        """
        若温度超出生物耐受范围，扣除健康值。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """
        min_temp = organism.traits.get("min_temp")
        max_temp = organism.traits.get("max_temp")

        excess = 0.0
        if min_temp is not None and self.current_temp < min_temp:
            excess = min_temp - self.current_temp
        elif max_temp is not None and self.current_temp > max_temp:
            excess = self.current_temp - max_temp

        if excess > 0:
            organism.apply_effect("health", -excess * self.damage_per_degree)

    def __repr__(self) -> str:
        return f"TemperatureFactor(current_temp={self.current_temp:.1f}°C)"
