"""
无智慧大脑模块

提供默认的无智慧行为，所有决策返回 0.5（中立/随机）。
用于向后兼容：未设置大脑的生物默认使用此类。
"""

from intelligence.base_brain import BaseBrain


class NoBrain(BaseBrain):
    """
    无智慧占位大脑。

    所有决策返回 0.5，表示中立行为，与原有逻辑完全兼容。
    植物等不需要智慧的生物默认使用此类。
    """

    def decide(self, inputs: list) -> list:
        """返回中立决策（全部 0.5）。"""
        return [0.5, 0.5, 0.5, 0.5]

    def clone(self) -> "NoBrain":
        """克隆无智慧大脑（直接返回新实例）。"""
        return NoBrain()

    def mutate(self, mutation_rate: float) -> None:
        """无智慧大脑不支持变异，此方法为空操作。"""

    def crossover(self, other: "BaseBrain") -> "NoBrain":
        """无智慧大脑不支持交叉，返回新的无智慧大脑。"""
        return NoBrain()
