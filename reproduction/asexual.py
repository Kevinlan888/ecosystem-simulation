"""
无性繁殖策略模块

适用于植物等通过分裂、出芽方式繁殖的生物。
"""

from __future__ import annotations
import random
from core.interfaces import ReproductionStrategy


class AsexualReproduction(ReproductionStrategy):
    """
    无性繁殖策略。

    条件：能量 > 70 且年龄 > 3。
    结果：克隆一个同类新生物，能量减半。
    """

    def can_reproduce(self, organism) -> bool:
        # 植物需生长至少 90 天（约 3 个月）才能分裂繁殖
        return organism.energy > 70 and organism.age > 90

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

        # 种群密度限制：同类过多时概率性抑制分裂（防止植物爆炸式增长挤占资源）
        same_count = sum(
            1 for o in ecosystem.organisms
            if o.name == organism.name and o.is_alive()
        )
        total_count = max(1, len(ecosystem.organisms))
        density_ratio = same_count / total_count
        if density_ratio > 0.6 and random.random() < density_ratio:
            return []  # 密度过高时抑制繁殖

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
