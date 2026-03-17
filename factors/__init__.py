"""
factors 包

公开所有预设环境因素类。
"""

from factors.temperature import TemperatureFactor
from factors.food_supply import FoodSupplyFactor
from factors.water import WaterFactor
from factors.light import LightFactor
from factors.disease import DiseaseFactor

__all__ = [
    "TemperatureFactor",
    "FoodSupplyFactor",
    "WaterFactor",
    "LightFactor",
    "DiseaseFactor",
]
