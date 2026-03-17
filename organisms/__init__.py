"""
organisms 包

公开所有预设生物类。
"""

from organisms.plant import Plant
from organisms.herbivore import Herbivore
from organisms.predator import Predator

__all__ = ["Plant", "Herbivore", "Predator"]
