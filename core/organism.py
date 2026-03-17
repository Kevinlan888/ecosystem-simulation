"""
生物基类模块

定义 Organism 基类，所有生物（植物、草食动物、捕食者等）都继承自此类。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.ecosystem import Ecosystem


class Organism:
    """
    生物基类。

    封装所有生物共有的属性和行为：年龄、健康、能量、繁殖策略等。
    """

    def __init__(
        self,
        name: str,
        health: float = 100.0,
        energy: float = 100.0,
        max_age: int = 50,
        reproduction_strategy=None,
        traits: dict | None = None,
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
        """
        self.name: str = name
        self.age: int = 0
        self.health: float = max(0.0, min(100.0, health))
        self.energy: float = max(0.0, min(100.0, energy))
        self.max_age: int = max_age
        self.reproduction_strategy = reproduction_strategy
        self.traits: dict = traits or {}

    # ------------------------------------------------------------------
    # 核心方法
    # ------------------------------------------------------------------

    def step(self, ecosystem: "Ecosystem") -> list:
        """
        执行一个时间步：增龄、消耗基础能量、尝试繁殖。

        Args:
            ecosystem: 当前生态系统实例

        Returns:
            list: 本步产生的新生生物列表
        """
        self.age += 1
        # 基础能量消耗
        self.apply_effect("energy", -1.0)

        offspring = []
        if self.reproduction_strategy and self.is_alive():
            if self.reproduction_strategy.can_reproduce(self):
                offspring = self.reproduction_strategy.reproduce(self, ecosystem)
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
