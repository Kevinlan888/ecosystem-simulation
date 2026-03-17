"""
食物供应因素模块

管理生态系统中的食物总量，动物每步消耗食物，食物不足时扣除能量。
"""

from core.interfaces import EnvironmentalFactor


class FoodSupplyFactor(EnvironmentalFactor):
    """
    食物供应环境因素。

    - 草食动物和捕食者每步消耗食物，食物不足时扣除能量。
    - 每步按 regen_rate 再生食物，但有上限。
    """

    def __init__(
        self,
        initial_food: float = 200.0,
        regen_rate: float = 10.0,
        max_food: float = 500.0,
        consumption_per_animal: float = 5.0,
        energy_penalty: float = 5.0,
    ):
        """
        初始化食物供应因素。

        Args:
            initial_food: 初始食物总量
            regen_rate: 每步食物再生量
            max_food: 食物上限
            consumption_per_animal: 每只动物每步消耗的食物量
            energy_penalty: 食物不足时每步扣除的能量值
        """
        self._name = "food_supply"
        self.food_amount: float = initial_food
        self.regen_rate: float = regen_rate
        self.max_food: float = max_food
        self.consumption_per_animal: float = consumption_per_animal
        self.energy_penalty: float = energy_penalty

    @property
    def name(self) -> str:
        """环境因素名称。"""
        return self._name

    def update(self, ecosystem) -> None:
        """
        每步食物再生（不超过上限）。

        Args:
            ecosystem: 当前生态系统实例
        """
        self.food_amount = min(self.max_food, self.food_amount + self.regen_rate)

    def apply(self, organism, ecosystem) -> None:
        """
        动物消耗食物，食物不足则扣除能量。
        植物不受此因素影响。

        Args:
            organism: 被影响的生物实例
            ecosystem: 当前生态系统实例
        """
        # 植物不消耗食物供应
        if organism.traits.get("is_plant", False):
            return

        if self.food_amount >= self.consumption_per_animal:
            self.food_amount -= self.consumption_per_animal
        else:
            # 食物不足，扣除能量
            organism.apply_effect("energy", -self.energy_penalty)

    def __repr__(self) -> str:
        return f"FoodSupplyFactor(food_amount={self.food_amount:.1f})"
