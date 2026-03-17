"""
生态系统模拟入口示例

演示：
1. 创建生态系统
2. 添加 5 个环境因素（温度、食物、水、光照、疾病）
3. 添加 10 株植物、8 只草食动物、3 只捕食者
4. 订阅 tick_end 事件，每步打印统计信息
5. 运行 50 步
6. 打印最终状态
"""

from core.ecosystem import Ecosystem
from factors.temperature import TemperatureFactor
from factors.food_supply import FoodSupplyFactor
from factors.water import WaterFactor
from factors.light import LightFactor
from factors.disease import DiseaseFactor
from organisms.plant import Plant
from organisms.herbivore import Herbivore
from organisms.predator import Predator


def on_tick_end(event_name: str, data: dict) -> None:
    """每个时间步结束时打印统计信息。"""
    status = data["status"]
    tick = status["tick"]
    total = status["total"]
    species = status["species"]
    species_str = ", ".join(f"{k}: {v}" for k, v in sorted(species.items()))
    print(f"[Tick {tick:>3}] 总生物数: {total:>4} | {species_str}")


def main():
    """主函数：创建并运行生态系统模拟。"""
    print("=" * 60)
    print("🌿 生态系统模拟启动")
    print("=" * 60)

    # 1. 创建生态系统
    eco = Ecosystem()

    # 2. 添加环境因素
    eco.add_factor(TemperatureFactor(base_temp=20.0, amplitude=15.0, period=40))
    eco.add_factor(FoodSupplyFactor(initial_food=300.0, regen_rate=15.0, max_food=600.0))
    eco.add_factor(WaterFactor(initial_level=200.0, regen_rate=8.0, max_level=400.0))
    eco.add_factor(LightFactor(day_length=12, energy_gain=4.0, energy_loss=1.0))
    eco.add_factor(DiseaseFactor(infection_rate=0.04, damage=2.0, recovery_chance=0.15))

    # 3. 添加生物（不通过事件总线打印，避免启动时刷屏）
    for _ in range(10):
        eco.organisms.append(Plant())
    for _ in range(8):
        eco.organisms.append(Herbivore())
    for _ in range(3):
        eco.organisms.append(Predator())

    print(f"初始状态: {eco.status()}")
    print("-" * 60)

    # 4. 订阅 tick_end 事件
    eco.event_bus.subscribe("tick_end", on_tick_end)

    # 5. 运行 50 步
    eco.run(50)

    # 6. 打印最终状态
    print("=" * 60)
    final = eco.status()
    print("🏁 最终状态:")
    print(f"  总 Tick 数: {final['tick']}")
    print(f"  存活生物数: {final['total']}")
    print("  各物种数量:")
    for species, count in sorted(final["species"].items()):
        print(f"    {species}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
