"""
疾病因素模块

模拟疾病的传播与自愈机制：随机感染、持续伤害、健康值高时有概率自愈。
"""

import random
from core.interfaces import EnvironmentalFactor


class DiseaseFactor(EnvironmentalFactor):
    """
    疾病环境因素。

    - 每步有概率感染未感染生物（感染率受当前感染者数量影响）。
    - 已感染生物每步扣除健康值。
    - 健康值高于自愈阈值时，有概率自愈。
    """

    def __init__(
        self,
        infection_rate: float = 0.05,
        damage: float = 3.0,
        recovery_threshold: float = 70.0,
        recovery_chance: float = 0.1,
    ):
        """
        初始化疾病因素。

        Args:
            infection_rate: 基础感染概率（每个未感染生物每步被感染的概率）
            damage: 已感染生物每步扣除的健康值
            recovery_threshold: 健康值高于此值时才有自愈机会
            recovery_chance: 满足自愈条件时每步自愈的概率
        """
        self._name = "disease"
        self.infection_rate: float = infection_rate
        self.damage: float = damage
        self.recovery_threshold: float = recovery_threshold
        self.recovery_chance: float = recovery_chance
        # 存储已感染生物的 id 集合
        self._infected: set = set()

    @property
    def name(self) -> str:
        """环境因素名称。"""
        return self._name

    def update(self, ecosystem) -> None:
        """
        清理已死亡生物的感染记录。

        Args:
            ecosystem: 当前生态系统实例
        """
        alive_ids = {id(o) for o in ecosystem.organisms}
        self._infected = self._infected & alive_ids

    def apply(self, organism, ecosystem) -> None:
        """
        对单个生物施加疾病影响：感染、伤害或自愈。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """
        oid = id(organism)
        if oid in self._infected:
            # 已感染：扣除健康值
            organism.apply_effect("health", -self.damage)
            # 检查自愈
            if organism.health >= self.recovery_threshold:
                if random.random() < self.recovery_chance:
                    self._infected.discard(oid)
        else:
            # 未感染：随机感染
            if random.random() < self.infection_rate:
                self._infected.add(oid)

    def is_infected(self, organism) -> bool:
        """
        检查特定生物是否已被感染。

        Args:
            organism: 待检查的生物实例

        Returns:
            bool: 是否已感染
        """
        return id(organism) in self._infected

    def __repr__(self) -> str:
        return f"DiseaseFactor(infected={len(self._infected)}, rate={self.infection_rate})"
