"""
生态系统模拟入口示例

演示：
1. 创建生态系统
2. 添加 5 个环境因素（温度、食物、水、光照、疾病）
3. 添加 10 株植物、8 只草食动物、3 只捕食者
4. 订阅 tick_end 事件，每步打印统计信息
5. 无限运行，直到 Ctrl+C 为止
6. 打印最终状态
"""

import time

from core.ecosystem import Ecosystem
from factors.temperature import TemperatureFactor
from factors.food_supply import FoodSupplyFactor
from factors.water import WaterFactor
from factors.light import LightFactor
from factors.disease import DiseaseFactor
from organisms.plant import Plant
from organisms.herbivore import Herbivore
from organisms.predator import Predator


def make_tick_handler(eco):
    """创建 tick_end 回调（闭包，捕获 eco 以实现迁入救援机制）。"""
    prev_species: dict = {}

    def on_tick_end(event_name: str, data: dict) -> None:
        nonlocal prev_species
        status = data["status"]
        tick = status["tick"]
        total = status["total"]
        species = status["species"]
        species_str = ", ".join(f"{k}: {v}" for k, v in sorted(species.items()))
        print(f"[Tick {tick:>3}] 总生物数: {total:>4} | {species_str}")

        # 检测种群显著变化事件（跳过第一个 tick，prev 为空无意义）
        if prev_species:
            all_names = set(prev_species) | set(species)
            for name in all_names:
                prev = prev_species.get(name, 0)
                curr = species.get(name, 0)
                if prev > 0 and curr == 0:
                    print(f"  ⚠️  [灭绝] {name} 在 Tick {tick} 全部死亡！")
                elif prev == 0 and curr > 0:
                    print(f"  🌱 [复苏] {name} 重新出现，当前数量: {curr}")
                elif prev > 0 and curr <= prev * 0.4:
                    print(f"  📉 [骤降] {name}: {prev} → {curr}（本轮减少 {prev - curr}）")
                elif prev > 0 and curr >= prev * 2.5:
                    print(f"  📈 [爆发] {name}: {prev} → {curr}（本轮增加 {curr - prev}）")
        prev_species = dict(species)

        # 迁入救援机制：种群濒危时模拟外部个体迁入，防止永久灭绝
        if species.get("Plant", 0) < 5:
            for _ in range(3):
                eco.organisms.append(Plant())
        if species.get("Herbivore", 0) < 3:
            for _ in range(2):
                eco.organisms.append(Herbivore())
        if species.get("Predator", 0) < 2:
            eco.organisms.append(Predator(hunt_chance=0.25))
    return on_tick_end


def make_evolution_handler(eco):
    """创建 evolution_occurred 回调，打印每个物种的进化统计信息。"""
    def on_evolution(event_name: str, data: dict) -> None:
        tick = data["tick"]
        by_species: dict = {}
        for org in eco.organisms:
            by_species.setdefault(org.name, []).append(org)

        lines = []
        for name, group in sorted(by_species.items()):
            scores = [o.fitness_score for o in group]
            avg = sum(scores) / len(scores)
            best = max(scores)
            lines.append(f"{name}({len(group)}只) avg={avg:.1f} best={best:.1f}")
        print(f"  🧬 [进化] Tick {tick} | " + " | ".join(lines))
    return on_evolution


def main():
    """主函数：创建并运行生态系统模拟。"""
    print("=" * 60)
    print("🌿 生态系统模拟启动")
    print("=" * 60)

    # 1. 创建生态系统
    eco = Ecosystem()

    # 2. 添加环境因素
    eco.add_factor(TemperatureFactor(base_temp=20.0, amplitude=15.0, period=40))
    eco.add_factor(FoodSupplyFactor(initial_food=500.0, regen_rate=30.0, max_food=800.0, consumption_per_animal=3.0, energy_penalty=3.0))
    eco.add_factor(WaterFactor(initial_level=200.0, regen_rate=8.0, max_level=400.0))
    eco.add_factor(LightFactor(day_length=12, energy_gain=4.0, energy_loss=1.0))
    eco.add_factor(DiseaseFactor(infection_rate=0.02, damage=1.0, recovery_chance=0.2))

    # 3. 添加生物（不通过事件总线打印，避免启动时刷屏）
    for _ in range(10):
        eco.organisms.append(Plant())
    for _ in range(8):
        eco.organisms.append(Herbivore())
    for _ in range(3):
        eco.organisms.append(Predator(hunt_chance=0.25))

    print(f"初始状态: {eco.status()}")
    print("-" * 60)

    # 4. 订阅事件
    eco.event_bus.subscribe("tick_end", make_tick_handler(eco))
    eco.event_bus.subscribe("evolution_occurred", make_evolution_handler(eco))

    # 5. 无限运行，直到 Ctrl+C
    print("按 Ctrl+C 停止模拟...\n")
    try:
        while True:
            eco.step()
            time.sleep(0.5)  # 每步暂停 0.5 秒，可调整
    except KeyboardInterrupt:
        print("\n\n模拟已中断。")

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
