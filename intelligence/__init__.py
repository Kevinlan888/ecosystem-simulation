"""
intelligence 包

导出智慧系统的公共 API：
    - BaseBrain: 大脑抽象基类
    - NeuralBrain: 神经网络大脑（numpy 实现）
    - NoBrain: 无智慧占位大脑（向后兼容）
    - GeneticAlgorithm: 遗传算法
"""

from intelligence.base_brain import BaseBrain
from intelligence.neural_brain import NeuralBrain
from intelligence.no_brain import NoBrain
from intelligence.genetic_algorithm import GeneticAlgorithm

__all__ = ["BaseBrain", "NeuralBrain", "NoBrain", "GeneticAlgorithm"]
