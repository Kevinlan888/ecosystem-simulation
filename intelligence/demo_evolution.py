"""
进化演示脚本

独立可运行的演示脚本，展示神经网络大脑 + 遗传算法在生态系统中的进化过程。

运行方式：
    python intelligence/demo_evolution.py
"""

import sys
import os

# 将项目根目录加入 Python 路径（支持从任意目录运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ecosystem import Ecosystem
from factors.temperature import TemperatureFactor
from factors.food_supply import FoodSupplyFactor
from factors.water import WaterFactor
from factors.light import LightFactor
from factors.disease import DiseaseFactor
from organisms.plant import Plant
from organisms.herbivore import Herbivore
from organisms.predator import Predator
from intelligence.neural_brain import NeuralBrain
from intelligence.genetic_algorithm import GeneticAlgorithm


def compute_avg_fitness(organisms, ga: GeneticAlgorithm) -> float:
    """计算种群平均适应度（使用 GeneticAlgorithm.compute_fitness）。"""
    if not organisms:
        return 0.0
    scores = [ga.compute_fitness(o) for o in organisms]
    return sum(scores) / len(scores)


def compute_max_fitness(organisms, ga: GeneticAlgorithm) -> float:
    """计算种群最高适应度（使用 GeneticAlgorithm.compute_fitness）。"""
    if not organisms:
        return 0.0
    return max(ga.compute_fitness(o) for o in organisms)


def get_avg_decisions(organisms) -> dict:
    """
    计算所有携带 NeuralBrain 的生物的平均决策权重。

    Returns:
        dict: 各行为策略的平均决策值
    """
    neural_orgs = [o for o in organisms if isinstance(o.brain, NeuralBrain)]
    if not neural_orgs:
        return {"seek_food": 0.5, "flee": 0.5, "seek_mate": 0.5, "rest": 0.5}

    n = len(neural_orgs)
    seek_food = sum(o.decisions[0] for o in neural_orgs) / n
    flee = sum(o.decisions[1] for o in neural_orgs) / n
    seek_mate = sum(o.decisions[2] for o in neural_orgs) / n
    rest = sum(o.decisions[3] for o in neural_orgs) / n
    return {"seek_food": seek_food, "flee": flee, "seek_mate": seek_mate, "rest": rest}


def main():
    """主函数：创建生态系统，运行 200 步，展示进化过程。"""
    print("=" * 70)
    print("🧠 神经网络 + 遗传算法 进化演示")
    print("=" * 70)

    # 1. 创建生态系统（每 20 步触发一次进化）
    eco = Ecosystem(evolve_interval=20)
    # 2. 添加所有环境因素
    eco.add_factor(TemperatureFactor(base_temp=20.0, amplitude=15.0, period=40))
    eco.add_factor(FoodSupplyFactor(initial_food=400.0, regen_rate=20.0, max_food=800.0))
    eco.add_factor(WaterFactor(initial_level=300.0, regen_rate=10.0, max_level=600.0))
    eco.add_factor(LightFactor(day_length=12, energy_gain=4.0, energy_loss=1.0))
    eco.add_factor(DiseaseFactor(infection_rate=0.03, damage=1.5, recovery_chance=0.2))

    # 3. 添加生物：20只草食动物 + 5只捕食者 + 15株植物
    for _ in range(15):
        eco.organisms.append(Plant())
    for _ in range(20):
        eco.organisms.append(Herbivore())
    for _ in range(5):
        eco.organisms.append(Predator())

    print(f"\n初始状态: {eco.status()}")
    print("-" * 70)
    print(f"{'Tick':>5} | {'种群数':>6} | {'平均适应度':>10} | {'最高适应度':>10} | {'seek_food':>9} | {'flee':>6} | {'seek_mate':>9} | {'rest':>6}")
    print("-" * 70)

    # 记录每 20 步时的决策均值，用于最终统计
    history = []

    # 4. 运行 200 步，每 20 步打印一次统计
    for tick in range(1, 201):
        eco.step()
        if tick % 20 == 0:
            avg_fit = compute_avg_fitness(eco.organisms, eco.ga)
            max_fit = compute_max_fitness(eco.organisms, eco.ga)
            decisions = get_avg_decisions(eco.organisms)
            history.append({"tick": tick, "decisions": decisions, "avg_fit": avg_fit, "population": len(eco.organisms)})
            print(
                f"{tick:>5} | {len(eco.organisms):>6} | {avg_fit:>10.2f} | {max_fit:>10.2f} | "
                f"{decisions['seek_food']:>9.3f} | {decisions['flee']:>6.3f} | "
                f"{decisions['seek_mate']:>9.3f} | {decisions['rest']:>6.3f}"
            )

    # 5. 最终打印进化历程统计
    print("=" * 70)
    print("\n📊 进化历程 - 行为策略平均权重变化：")
    print(f"{'Tick':>5} | {'seek_food':>9} | {'flee':>6} | {'seek_mate':>9} | {'rest':>6}")
    print("-" * 45)
    for record in history:
        d = record["decisions"]
        print(
            f"{record['tick']:>5} | {d['seek_food']:>9.3f} | {d['flee']:>6.3f} | "
            f"{d['seek_mate']:>9.3f} | {d['rest']:>6.3f}"
        )

    # 比较首末决策变化
    if len(history) >= 2:
        first = history[0]["decisions"]
        last = history[-1]["decisions"]
        print("\n策略演变趋势（末期 vs 初期）：")
        for key in ["seek_food", "flee", "seek_mate", "rest"]:
            delta = last[key] - first[key]
            trend = "↑" if delta > 0.01 else ("↓" if delta < -0.01 else "→")
            print(f"  {key:>12}: {first[key]:.3f} → {last[key]:.3f}  {trend} ({delta:+.3f})")

    print("\n最终种群状态:")
    final = eco.status()
    print(f"  总 Tick 数: {final['tick']}")
    print(f"  存活生物数: {final['total']}")
    print("  各物种数量:")
    for species, count in sorted(final["species"].items()):
        print(f"    {species}: {count}")
    print("=" * 70)
    print("\n✅ 演示完成！进化过程详见上方表格。")


if __name__ == "__main__":
    main()
