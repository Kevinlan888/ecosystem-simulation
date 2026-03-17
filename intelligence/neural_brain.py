"""
神经网络大脑模块

使用纯 numpy 实现的前馈神经网络大脑，无需任何深度学习框架。

网络结构：
    输入层(8) → 隐藏层1(16, tanh) → 隐藏层2(8, tanh) → 输出层(4, sigmoid)
"""

import copy
import numpy as np
from intelligence.base_brain import BaseBrain


class NeuralBrain(BaseBrain):
    """
    基于前馈神经网络的生物大脑。

    网络结构（固定）：
        - 输入层：8 个节点
        - 隐藏层1：16 个节点，激活函数 tanh
        - 隐藏层2：8 个节点，激活函数 tanh
        - 输出层：4 个节点，激活函数 sigmoid

    输入（8维）：
        [能量/100, 健康/100, 年龄比例, 食物距离, 捕食者距离, 同类距离, 温度/50, 水位/100]

    输出（4维）：
        [趋向食物意愿, 逃离捕食者意愿, 寻找伴侣意愿, 休息意愿]
    """

    # 网络层结构
    LAYER_SIZES = [8, 16, 8, 4]
    # sigmoid 溢出防护剪裁范围
    _SIGMOID_CLIP = 500.0

    def __init__(self, weights: list | None = None):
        """
        初始化神经网络大脑。

        Args:
            weights: 可选，预设的权重列表（用于从字典恢复）。
                     若为 None，则随机初始化（正态分布，std=0.5）。
        """
        if weights is not None:
            self.weights = weights
        else:
            self.weights = self._init_weights()

    def _init_weights(self) -> list:
        """
        随机初始化所有层的权重矩阵。

        Returns:
            list: 每个元素为 numpy 数组，形状为 (in_size, out_size)
        """
        weights = []
        for i in range(len(self.LAYER_SIZES) - 1):
            in_size = self.LAYER_SIZES[i]
            out_size = self.LAYER_SIZES[i + 1]
            # Xavier 初始化：避免 tanh 激活下的梯度消失
            std = np.sqrt(2.0 / (in_size + out_size))
            w = np.random.normal(0.0, std, (in_size, out_size))
            weights.append(w)
        return weights

    @staticmethod
    def _tanh(x: np.ndarray) -> np.ndarray:
        """tanh 激活函数。"""
        return np.tanh(x)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        """sigmoid 激活函数（带剪裁防止数值溢出）。"""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -NeuralBrain._SIGMOID_CLIP, NeuralBrain._SIGMOID_CLIP)))

    def decide(self, inputs: list) -> list:
        """
        执行前向传播，返回决策输出。

        Args:
            inputs: 长度为 8 的感知输入列表

        Returns:
            list: 长度为 4 的决策输出列表，值域 [0, 1]
        """
        x = np.array(inputs, dtype=float)

        # 隐藏层1：tanh
        x = self._tanh(x @ self.weights[0])
        # 隐藏层2：tanh
        x = self._tanh(x @ self.weights[1])
        # 输出层：sigmoid
        x = self._sigmoid(x @ self.weights[2])

        return x.tolist()

    def clone(self) -> "NeuralBrain":
        """
        深拷贝所有权重矩阵，返回新的 NeuralBrain 实例。

        Returns:
            NeuralBrain: 权重完全相同的新大脑
        """
        cloned_weights = [w.copy() for w in self.weights]
        return NeuralBrain(weights=cloned_weights)

    def mutate(self, mutation_rate: float = 0.1) -> None:
        """
        对每个权重以 mutation_rate 概率加入高斯噪声（std=0.2）。

        Args:
            mutation_rate: 每个权重发生变异的概率（0~1）
        """
        for w in self.weights:
            mask = np.random.random(w.shape) < mutation_rate
            noise = np.random.normal(0.0, 0.2, w.shape)
            w += mask * noise

    def crossover(self, other: "BaseBrain") -> "NeuralBrain":
        """
        与另一个大脑均匀交叉，生成后代大脑。

        对每层权重矩阵中的每个元素，随机选择来自 self 或 other。

        Args:
            other: 另一个 NeuralBrain 实例

        Returns:
            NeuralBrain: 后代大脑实例
        """
        if not isinstance(other, NeuralBrain):
            return self.clone()

        child_weights = []
        for w_self, w_other in zip(self.weights, other.weights):
            mask = np.random.random(w_self.shape) < 0.5
            child_w = np.where(mask, w_self, w_other)
            child_weights.append(child_w)
        return NeuralBrain(weights=child_weights)

    def to_dict(self) -> dict:
        """
        将大脑权重序列化为字典，方便保存。

        Returns:
            dict: 包含权重列表（每层为嵌套列表）的字典
        """
        return {
            "type": "NeuralBrain",
            "layer_sizes": self.LAYER_SIZES,
            "weights": [w.tolist() for w in self.weights],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NeuralBrain":
        """
        从字典恢复 NeuralBrain 实例。

        Args:
            data: 由 to_dict() 生成的字典

        Returns:
            NeuralBrain: 恢复的大脑实例
        """
        weights = [np.array(w) for w in data["weights"]]
        return cls(weights=weights)

    def __repr__(self) -> str:
        return f"NeuralBrain(layers={self.LAYER_SIZES})"
