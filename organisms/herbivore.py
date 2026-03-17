"""
草食动物生物模块

草食动物通过食物供应获取能量，使用有性繁殖策略。
"""

from core.organism import Organism
from reproduction.sexual import SexualReproduction
from intelligence.neural_brain import NeuralBrain


class Herbivore(Organism):
    """
    草食动物生物。

    - traits: min_temp=0, max_temp=35, is_plant=False, is_herbivore=True
    - 繁殖策略: 有性繁殖（周围有同类时繁殖）
    - 能量来源: 通过食物供应因素获得能量（见 FoodSupplyFactor）
    - 大脑: 默认携带 NeuralBrain，支持神经网络决策
    """

    def __init__(
        self,
        name: str = "Herbivore",
        health: float = 80.0,
        energy: float = 70.0,
        max_age: int = 40,
        reproduction_strategy=None,
        traits: dict | None = None,
        brain=None,
    ):
        """
        初始化草食动物实例。

        Args:
            name: 动物名称
            health: 初始健康值
            energy: 初始能量值
            max_age: 最大寿命
            reproduction_strategy: 繁殖策略（默认有性繁殖）
            traits: 生物特征字典（默认草食动物特征）
            brain: 大脑实例（默认 NeuralBrain）
        """
        super().__init__(
            name=name,
            health=health,
            energy=energy,
            max_age=max_age,
            reproduction_strategy=reproduction_strategy or SexualReproduction(),
            traits=traits or {
                "min_temp": 0,
                "max_temp": 35,
                "is_plant": False,
                "is_herbivore": True,
            },
            brain=brain if brain is not None else NeuralBrain(),
        )
