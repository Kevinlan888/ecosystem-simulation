"""
大脑抽象基类模块

定义所有大脑（智慧系统）必须实现的接口。
"""

from abc import ABC, abstractmethod


class BaseBrain(ABC):
    """
    大脑抽象基类。

    所有大脑实现（神经网络大脑、无智慧占位等）都必须继承此类，
    实现 decide()、clone()、mutate() 和 crossover() 方法。
    """

    @abstractmethod
    def decide(self, inputs: list) -> list:
        """
        根据输入感知，返回行动决策输出。

        Args:
            inputs: 感知输入向量（8维浮点数列表）

        Returns:
            list: 决策输出向量（4维浮点数列表，值域 0~1）
        """

    @abstractmethod
    def clone(self) -> "BaseBrain":
        """
        克隆大脑（用于遗传）。

        Returns:
            BaseBrain: 当前大脑的深拷贝
        """

    @abstractmethod
    def mutate(self, mutation_rate: float) -> None:
        """
        变异大脑权重。

        Args:
            mutation_rate: 每个权重发生变异的概率（0~1）
        """

    @abstractmethod
    def crossover(self, other: "BaseBrain") -> "BaseBrain":
        """
        与另一个大脑交叉，生成后代大脑。

        Args:
            other: 另一个大脑实例（类型应与自身相同）

        Returns:
            BaseBrain: 后代大脑实例
        """
