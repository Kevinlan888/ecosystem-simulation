"""
生态系统主类模块

Ecosystem 驱动整个模拟的每一个时间步：
- 管理生物列表和环境因素列表
- 每步按顺序更新因素、作用生物、推进生物状态、清理死亡、添加新生
- 通过 EventBus 发布生命周期事件
"""

from __future__ import annotations
from events.event_bus import EventBus
from intelligence.genetic_algorithm import GeneticAlgorithm


class Ecosystem:
    """
    生态系统主类。

    负责协调所有生物和环境因素，驱动时间步进。
    """

    def __init__(self, evolve_interval: int = 20, world_size: tuple = (100.0, 100.0)):
        """
        初始化一个空的生态系统。

        Args:
            evolve_interval: 每隔多少步执行一次种群进化（遗传算法）
            world_size: 世界空间尺寸 (width, height)，用于生物空间定位和可视化
        """
        self.organisms: list = []
        self.factors: list = []
        self.tick: int = 0
        self.event_bus: EventBus = EventBus()
        self.ga: GeneticAlgorithm = GeneticAlgorithm()
        self.evolve_interval: int = evolve_interval
        self.world_size: tuple = world_size

    # ------------------------------------------------------------------
    # 管理接口
    # ------------------------------------------------------------------

    def add_organism(self, organism) -> None:
        """
        向生态系统添加一个生物。未设置位置的生物将在世界范围内随机放置。

        Args:
            organism: Organism 实例
        """
        import random
        if organism.x is None:
            organism.x = random.uniform(0.0, self.world_size[0])
            organism.y = random.uniform(0.0, self.world_size[1])
        self.organisms.append(organism)
        self.event_bus.publish("organism_born", {"organism": organism})

    def add_factor(self, factor) -> None:
        """
        向生态系统添加一个环境因素（可随时动态添加）。

        Args:
            factor: EnvironmentalFactor 实例
        """
        self.factors.append(factor)
        self.event_bus.publish("factor_added", {"factor": factor})

    def remove_factor(self, factor_name: str) -> None:
        """
        通过名字移除环境因素（支持动态移除）。

        Args:
            factor_name: 环境因素的 name 属性值
        """
        removed = [f for f in self.factors if f.name == factor_name]
        self.factors = [f for f in self.factors if f.name != factor_name]
        for f in removed:
            self.event_bus.publish("factor_removed", {"factor": f})

    # ------------------------------------------------------------------
    # 时间步推进
    # ------------------------------------------------------------------

    def step(self) -> None:
        """
        推进一个时间步：
        1. tick +1
        2. 所有环境因素 update()
        3. 所有环境因素对所有生物 apply()
        4. 所有生物执行 step()，收集新生生物
        5. 移除死亡生物（并发布 organism_died 事件）
        6. 添加新生生物（并发布 organism_born 事件）
        7. 发布 tick_end 事件
        """
        self.tick += 1

        # 2. 更新所有环境因素自身状态
        for factor in self.factors:
            factor.update(self)

        # 3. 环境因素作用于所有生物（快照，避免中途修改列表影响迭代）
        current_organisms = list(self.organisms)
        for factor in self.factors:
            for organism in current_organisms:
                factor.apply(organism, self)

        # 4. 所有生物执行一个时间步，收集后代
        new_offspring: list = []
        for organism in current_organisms:
            if organism.is_alive():
                offspring = organism.step(self)
                new_offspring.extend(offspring)

        # 5. 移除死亡生物
        dead = [o for o in self.organisms if not o.is_alive()]
        self.organisms = [o for o in self.organisms if o.is_alive()]
        for o in dead:
            self.event_bus.publish("organism_died", {"organism": o, "tick": self.tick})

        # 6. 添加新生生物（直接追加，不再重复发布，add_organism 已发布）
        for offspring in new_offspring:
            self.add_organism(offspring)

        # 7. 发布 tick_end 事件
        self.event_bus.publish("tick_end", {"tick": self.tick, "status": self.status()})

        # 8. 每隔 evolve_interval 步执行一次种群进化（按物种分组，防止跨物种污染大脑）
        if self.tick % self.evolve_interval == 0 and len(self.organisms) > 2:
            by_species: dict = {}
            for org in self.organisms:
                by_species.setdefault(org.name, []).append(org)
            for group in by_species.values():
                if len(group) > 1:
                    self.ga.evolve_population(group)
            self.event_bus.publish("evolution_occurred", {
                "tick": self.tick,
                "population": len(self.organisms),
            })

    def run(self, steps: int) -> None:
        """
        运行指定步数。

        Args:
            steps: 要运行的时间步数量
        """
        for _ in range(steps):
            self.step()

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """
        返回当前生态系统统计信息。

        Returns:
            dict: 包含 tick、总生物数、各物种数量的字典
        """
        counts: dict[str, int] = {}
        for o in self.organisms:
            counts[o.name] = counts.get(o.name, 0) + 1
        return {
            "tick": self.tick,
            "total": len(self.organisms),
            "species": counts,
        }

    def __repr__(self) -> str:
        return f"Ecosystem(tick={self.tick}, organisms={len(self.organisms)}, factors={len(self.factors)})"
