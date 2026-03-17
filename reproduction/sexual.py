"""
有性繁殖策略模块

适用于草食动物、捕食者等需要配偶才能繁殖的生物。
"""

from __future__ import annotations
import random
from core.interfaces import ReproductionStrategy


class SexualReproduction(ReproductionStrategy):
    """
    有性繁殖策略。

    条件：能量 > 50 且年龄 > 5，且生态系统中存在同类伙伴。
    结果：生成一个后代（traits 取双亲平均），双亲各消耗 20 点能量。
    """

    def can_reproduce(self, organism) -> bool:
        """
        判断是否满足有性繁殖条件（不检查伙伴，伙伴在 reproduce 中查找）。

        Args:
            organism: 待判断的生物实例

        Returns:
            bool: 能量 > 50 且年龄 > 5
        """
        return organism.energy > 50 and organism.age > 5

    def reproduce(self, organism, ecosystem) -> list:
        """
        在生态系统中寻找同类伙伴，找到则生成后代。

        Args:
            organism: 执行繁殖的生物实例
            ecosystem: 当前生态系统实例

        Returns:
            list: 包含一个新生生物的列表，或空列表（未找到伙伴）
        """
        # 寻找同类且满足繁殖条件的伙伴（排除自身）
        partner = next(
            (
                o
                for o in ecosystem.organisms
                if o is not organism
                and o.name == organism.name
                and o.is_alive()
                and o.energy > 50
                and o.age > 5
            ),
            None,
        )
        if partner is None:
            return []

        # 食物感知：人均食物越少，繁殖意愿越低（模拟老鼠等动物的饥荒抑制机制）
        food_factor = next(
            (f for f in ecosystem.factors if f.name == "food_supply"), None
        )
        if food_factor is not None:
            same_species_count = sum(
                1 for o in ecosystem.organisms
                if o.name == organism.name and o.is_alive()
            )
            food_per_individual = food_factor.food_amount / max(1, same_species_count)
            if food_per_individual < 10:
                return []          # 极度饥荒：完全停止繁殖
            elif food_per_individual < 30:
                if random.random() > food_per_individual / 30:
                    return []      # 食物不足：概率性抑制繁殖

        # 双亲各消耗 20 点能量
        organism.apply_effect("energy", -20)
        partner.apply_effect("energy", -20)

        # 后代 traits 取双亲平均（数值型特征）
        offspring_traits = {}
        all_keys = set(organism.traits) | set(partner.traits)
        for key in all_keys:
            v1 = organism.traits.get(key)
            v2 = partner.traits.get(key)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                offspring_traits[key] = (v1 + v2) / 2
            else:
                # 非数值特征继承亲本
                offspring_traits[key] = v1 if v1 is not None else v2

        offspring = organism.__class__(
            name=organism.name,
            health=60.0,
            energy=50.0,
            max_age=organism.max_age,
            reproduction_strategy=SexualReproduction(),
            traits=offspring_traits,
        )
        return [offspring]
