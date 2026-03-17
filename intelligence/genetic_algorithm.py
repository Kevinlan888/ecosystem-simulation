"""
遗传算法模块

在生态模拟过程中执行种群进化：不单独训练，而是通过自然选择、
交叉和变异来更新生物的大脑权重，模拟"代际学习"场景。
"""

import random
from intelligence.no_brain import NoBrain


class GeneticAlgorithm:
    """
    遗传算法。

    在一批生物中执行进化：
    1. 按适应度（fitness_score）排序
    2. 保留精英（前 elite_ratio 比例）
    3. 其余通过交叉 + 变异生成新大脑

    注意：这不替换生物，只更新其大脑权重，
    用于模拟"代际学习"场景。
    """

    # 适应度权重（对应 age、energy、health）
    FITNESS_AGE_WEIGHT: float = 0.4
    FITNESS_ENERGY_WEIGHT: float = 0.3
    FITNESS_HEALTH_WEIGHT: float = 0.3

    def __init__(self, mutation_rate: float = 0.1, elite_ratio: float = 0.2):
        """
        初始化遗传算法。

        Args:
            mutation_rate: 权重变异概率（0~1）
            elite_ratio: 精英保留比例（0~1）
        """
        self.mutation_rate = mutation_rate
        self.elite_ratio = elite_ratio

    def compute_fitness(self, organism) -> float:
        """
        计算单个生物的适应度。

        适应度公式：
            fitness = age × FITNESS_AGE_WEIGHT + energy × FITNESS_ENERGY_WEIGHT
                    + health × FITNESS_HEALTH_WEIGHT

        Args:
            organism: 生物实例（需有 age、energy、health 属性）

        Returns:
            float: 适应度分数（越高越好）
        """
        return (
            organism.age * self.FITNESS_AGE_WEIGHT
            + organism.energy * self.FITNESS_ENERGY_WEIGHT
            + organism.health * self.FITNESS_HEALTH_WEIGHT
        )

    def breed_brain(self, parent1_brain, parent2_brain):
        """
        交叉 + 变异，生成后代大脑。

        Args:
            parent1_brain: 父本大脑
            parent2_brain: 母本大脑

        Returns:
            BaseBrain: 后代大脑（经过交叉和变异）
        """
        child_brain = parent1_brain.crossover(parent2_brain)
        child_brain.mutate(self.mutation_rate)
        return child_brain

    def evolve_population(self, organisms: list) -> None:
        """
        在一批生物中执行进化，更新非精英生物的大脑权重。

        流程：
        1. 计算并更新所有生物的适应度评分
        2. 按适应度排序
        3. 保留精英（前 elite_ratio）
        4. 其余通过交叉 + 变异生成新大脑

        Args:
            organisms: 生物实例列表（需有 brain 和 fitness_score 属性）
        """
        if not organisms:
            return

        # 更新所有生物的适应度评分
        for org in organisms:
            org.fitness_score = self.compute_fitness(org)

        # 按适应度降序排序（高适应度的在前）
        sorted_orgs = sorted(organisms, key=lambda o: o.fitness_score, reverse=True)

        n = len(sorted_orgs)
        elite_count = max(1, int(n * self.elite_ratio))

        # 提取精英大脑列表（排除 NoBrain）
        elite_brains = [
            o.brain for o in sorted_orgs[:elite_count]
            if not isinstance(o.brain, NoBrain)
        ]

        # 若没有有效精英大脑，无需进化
        if not elite_brains:
            return

        # 对非精英生物的大脑进行交叉 + 变异更新
        for org in sorted_orgs[elite_count:]:
            if isinstance(org.brain, NoBrain):
                continue  # NoBrain 生物跳过进化

            parent1 = random.choice(elite_brains)
            parent2 = random.choice(elite_brains)
            org.brain = self.breed_brain(parent1, parent2)
