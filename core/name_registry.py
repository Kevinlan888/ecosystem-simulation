"""
个体名称注册模块

为每只新生物体生成独一无二的个体名称，模拟现实中对野生动物的标记追踪。
名字池耗尽后自动切换为"物种前缀-编号"格式。
"""

import itertools

# 每个物种的专属名字池
_POOLS: dict[str, list[str]] = {
    "Plant": [
        "Willow", "Oak", "Fern", "Sage", "Moss", "Thistle", "Clover", "Reed",
        "Ivy", "Cedar", "Birch", "Maple", "Briar", "Sorrel", "Lupin", "Nettle",
        "Rowan", "Hazel", "Elder", "Alder", "Beech", "Aspen", "Poplar", "Larch",
        "Juniper", "Heather", "Bracken", "Foxglove", "Primrose", "Yarrow",
    ],
    "Herbivore": [
        "Buck", "Doe", "Hazel", "Fawn", "Briar", "Daisy", "Rustle", "Flint",
        "Meadow", "Pippin", "Wren", "Ember", "Ash", "Dusty", "Sandy", "Stripe",
        "Swift", "Bonnie", "Bramble", "Acorn", "Berry", "Nutmeg", "Sorrel",
        "Thorn", "Biscuit", "Clove", "Maple", "Dew", "Pebble", "Thistle",
    ],
    "Predator": [
        "Alpha", "Shadow", "Fang", "Claw", "Storm", "Blaze", "Grim", "Talon",
        "Dusk", "Frost", "Sable", "Nero", "Hunter", "Raven", "Dagger", "Bane",
        "Reaper", "Havoc", "Savage", "Apex", "Viktor", "Draco", "Orion", "Rogue",
        "Cipher", "Vex", "Wraith", "Obsidian", "Titan", "Eclipse",
    ],
}

_used: dict[str, set] = {}
_counters: dict[str, "itertools.count"] = {}


def generate(species: str) -> str:
    """
    为指定物种生成一个唯一的个体名称。

    Args:
        species: 物种名称，如 "Herbivore"、"Predator"、"Plant"

    Returns:
        str: 唯一个体名称
    """
    pool = _POOLS.get(species, [])
    used = _used.setdefault(species, set())

    for candidate in pool:
        if candidate not in used:
            used.add(candidate)
            return candidate

    # 名字池耗尽，使用计数器后缀
    if species not in _counters:
        _counters[species] = itertools.count(len(pool) + 1)
    return f"{species[:3]}-{next(_counters[species])}"
