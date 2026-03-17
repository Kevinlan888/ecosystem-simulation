"""
core 包

公开 core 模块的主要类。
"""

from core.interfaces import EnvironmentalFactor, ReproductionStrategy, EventListener
from core.organism import Organism
from core.ecosystem import Ecosystem

__all__ = [
    "EnvironmentalFactor",
    "ReproductionStrategy",
    "EventListener",
    "Organism",
    "Ecosystem",
]
