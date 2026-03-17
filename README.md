# 🌿 Ecosystem Simulation — 模拟生态系统

一个结构清晰、高度可扩展的 Python 生态系统模拟框架。生态系统中的生物会受到各种环境因素的影响，可以繁殖，并提供清晰的接口方便后续扩展。

---

## 项目结构

```
ecosystem/
├── core/
│   ├── __init__.py
│   ├── ecosystem.py          # 生态系统主类，驱动每一个时间步
│   ├── organism.py           # 生物基类
│   └── interfaces.py         # 所有抽象接口定义（环境因素、繁殖策略、事件）
├── factors/
│   ├── __init__.py
│   ├── temperature.py        # 🌡️ 温度因素
│   ├── food_supply.py        # 🌿 食物供应因素
│   ├── water.py              # 💧 水资源因素
│   ├── light.py              # ☀️ 光照因素
│   └── disease.py            # 🦠 疾病因素
├── organisms/
│   ├── __init__.py
│   ├── plant.py              # 🌱 植物
│   ├── herbivore.py          # 🐇 草食动物
│   └── predator.py           # 🐺 捕食者
├── reproduction/
│   ├── __init__.py
│   ├── sexual.py             # 有性繁殖策略
│   └── asexual.py            # 无性繁殖策略
├── events/
│   ├── __init__.py
│   └── event_bus.py          # 事件总线（观察者模式）
├── main.py                   # 示例入口，演示生态系统运行
├── README.md
└── requirements.txt
```

---

## 快速开始

**环境要求：** Python 3.10+，仅使用标准库，无第三方依赖。

```bash
# 克隆仓库
git clone https://github.com/Kevinlan888/ecosystem-simulation.git
cd ecosystem-simulation

# 直接运行
python main.py
```

运行后将输出每个时间步的统计信息（各物种数量），以及最终生态系统状态。

---

## 如何扩展

### 添加新的环境因素

继承 `EnvironmentalFactor` 抽象类并实现三个方法：

```python
from core.interfaces import EnvironmentalFactor

class PollutionFactor(EnvironmentalFactor):
    def __init__(self):
        self._name = "pollution"
        self.level = 0.0

    @property
    def name(self) -> str:
        return self._name

    def update(self, ecosystem) -> None:
        # 每步污染增加
        self.level = min(100.0, self.level + 0.5)

    def apply(self, organism, ecosystem) -> None:
        # 污染高时损害所有生物健康
        if self.level > 50:
            organism.apply_effect("health", -self.level * 0.01)

# 使用
eco = Ecosystem()
eco.add_factor(PollutionFactor())
```

### 添加新的繁殖策略

继承 `ReproductionStrategy` 抽象类：

```python
from core.interfaces import ReproductionStrategy

class BuddingReproduction(ReproductionStrategy):
    """出芽繁殖：能量 > 60 时产生一个较弱的后代。"""

    def can_reproduce(self, organism) -> bool:
        return organism.energy > 60

    def reproduce(self, organism, ecosystem) -> list:
        organism.apply_effect("energy", -30)
        bud = organism.__class__(name=organism.name, health=40.0, energy=30.0)
        return [bud]
```

### 添加新的生物

继承 `Organism` 基类，可覆盖 `step()` 实现自定义行为：

```python
from core.organism import Organism
from reproduction.asexual import AsexualReproduction

class Fungi(Organism):
    """真菌：分解有机物，无性繁殖。"""

    def __init__(self, name="Fungi"):
        super().__init__(
            name=name,
            health=60.0,
            energy=50.0,
            max_age=20,
            reproduction_strategy=AsexualReproduction(),
            traits={"min_temp": 5, "max_temp": 35, "is_plant": False, "is_fungi": True},
        )
```

---

## 设计模式说明

| 设计模式 | 位置 | 用途 |
|----------|------|------|
| **抽象基类 (ABC)** | `core/interfaces.py` | 定义 `EnvironmentalFactor`、`ReproductionStrategy`、`EventListener` 的标准接口，强制子类实现必要方法 |
| **策略模式 (Strategy)** | `reproduction/` | 繁殖方式封装为可替换的策略对象，可在运行时动态切换 |
| **观察者模式 (Observer)** | `events/event_bus.py` | `EventBus` 解耦事件发布者和订阅者，支持 `tick_end`、`organism_born`、`organism_died` 等事件 |

---

## 可选依赖

如需美化终端输出，可安装 `rich` 库：

```bash
pip install rich
```

然后在 `main.py` 中使用 `rich.print()` 或 `rich.table.Table` 来渲染彩色表格。
