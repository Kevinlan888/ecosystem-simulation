"""
无性繁殖策略模块

适用于植物等通过分裂、出芽方式繁殖的生物。
"""

from __future__ import annotations
from core.interfaces import ReproductionStrategy


class AsexualReproduction(ReproductionStrategy):
    """
    无性繁殖策略。

    条件：能量 > 70 且年龄 > 3。
    结果：克隆一个同类新生物，能量减半。
    """

    def can_reproduce(self, organism) -> bool:
        """
        判断是否满足无性繁殖条件。

        Args:
            organism: 待判断的生物实例

        Returns:
            bool: 能量 > 70 且年龄 > 3
        """
        return organism.energy > 70 and organism.age > 3

    def reproduce(self, organism, ecosystem) -> list:
        """
        执行无性繁殖：创建同类新生物，亲本能量减半。

        Args:
            organism: 执行繁殖的生物实例
            ecosystem: 当前生态系统实例（保留接口，暂未使用）

        Returns:
            list: 包含一个新生生物的列表
        """
        offspring_energy = organism.energy / 2
        organism.apply_effect("energy", -offspring_energy)

        # 创建同类新生物（traits 完整继承）
        offspring = organism.__class__(
            name=organism.name,
            health=50.0,
            energy=offspring_energy,
            max_age=organism.max_age,
            reproduction_strategy=AsexualReproduction(),
            traits=dict(organism.traits),
        )
        return [offspring]
