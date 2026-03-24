"""
Pygame 可视化模拟器

运行方式：
    python visualizer.py

快捷键：
    Space       暂停 / 继续
    +  / =      加速（最高 x16）
    -           减速（最低 x1）
    R           重置模拟
    ESC / Q     退出
"""

import sys
import math
import pygame

from core.ecosystem import Ecosystem
from factors.temperature import TemperatureFactor
from factors.food_supply import FoodSupplyFactor
from factors.water import WaterFactor
from factors.light import LightFactor
from factors.disease import DiseaseFactor
from organisms.plant import Plant
from organisms.herbivore import Herbivore
from organisms.predator import Predator

# ── 画面常量 ──────────────────────────────────────────────────────────────────
WORLD_W, WORLD_H = 100.0, 100.0   # 生态世界单位尺寸
VIEW_W, VIEW_H   = 800, 800        # 世界视口像素尺寸
PANEL_W          = 260             # 右侧 HUD 面板宽度
WIN_W            = VIEW_W + PANEL_W
WIN_H            = VIEW_H
SCALE_X          = VIEW_W / WORLD_W
SCALE_Y          = VIEW_H / WORLD_H

FPS = 60

# ── 配色 ──────────────────────────────────────────────────────────────────────
BG_COLOR      = (15,  20,  15)
GRID_COLOR    = (30,  40,  30)
PANEL_COLOR   = (20,  25,  20)
BORDER_COLOR  = (60,  80,  60)
WHITE         = (230, 230, 230)
GRAY          = (130, 130, 130)
DIM           = (70,  70,  70)

SPECIES_COLOR = {
    "Plant":     (60,  190,  60),
    "Herbivore": (80,  160, 230),
    "Predator":  (220,  60,  60),
}
DEFAULT_COLOR = (180, 180, 100)


def world_to_screen(x: float, y: float) -> tuple[int, int]:
    return int(x * SCALE_X), int(y * SCALE_Y)


def make_ecosystem() -> Ecosystem:
    eco = Ecosystem(world_size=(WORLD_W, WORLD_H))
    eco.add_factor(TemperatureFactor(base_temp=20.0, amplitude=15.0, period=365))
    eco.add_factor(FoodSupplyFactor(initial_food=500.0, regen_rate=30.0,
                                    max_food=800.0, consumption_per_animal=3.0,
                                    energy_penalty=3.0))
    eco.add_factor(WaterFactor(initial_level=200.0, regen_rate=8.0, max_level=400.0))
    eco.add_factor(LightFactor(day_length=12, energy_gain=4.0, energy_loss=1.0))
    eco.add_factor(DiseaseFactor(infection_rate=0.02, damage=1.0, recovery_chance=0.2))

    for _ in range(14): eco.add_organism(Plant())
    for _ in range(10): eco.add_organism(Herbivore())
    for _ in range(4):  eco.add_organism(Predator(hunt_chance=0.3))

    # 迁入救援：种群过低时自动补充
    def rescue(event_name, data):
        sp = data["status"]["species"]
        if sp.get("Plant", 0) < 5:
            for _ in range(3): eco.add_organism(Plant())
        if sp.get("Herbivore", 0) < 3:
            for _ in range(2): eco.add_organism(Herbivore())
        if sp.get("Predator", 0) < 2:
            eco.add_organism(Predator(hunt_chance=0.25))
    eco.event_bus.subscribe("tick_end", rescue)
    return eco


# ── 绘图工具 ──────────────────────────────────────────────────────────────────

def draw_grid(surface: pygame.Surface) -> None:
    for gx in range(0, VIEW_W, 50):
        pygame.draw.line(surface, GRID_COLOR, (gx, 0), (gx, VIEW_H))
    for gy in range(0, VIEW_H, 50):
        pygame.draw.line(surface, GRID_COLOR, (0, gy), (VIEW_W, gy))


def draw_organism(surface: pygame.Surface, org) -> None:
    if org.x is None:
        return
    sx, sy = world_to_screen(org.x, org.y)
    color = SPECIES_COLOR.get(org.name, DEFAULT_COLOR)

    # 半径：基础 4px，健康越低越小，能量低时闪烁变暗
    radius = max(2, int(4 * (org.health / 100.0) ** 0.5 + 2))

    # 能量低时在外圈画一个警示橙环
    if org.energy < 30:
        pygame.draw.circle(surface, (220, 140, 0), (sx, sy), radius + 2, 1)

    pygame.draw.circle(surface, color, (sx, sy), radius)

    # 捕食者：额外画一个小尖角（三角形轮廓）让其更显眼
    if org.traits.get("is_predator", False):
        tip = (sx, sy - radius - 3)
        left = (sx - 3, sy + 1)
        right = (sx + 3, sy + 1)
        pygame.draw.polygon(surface, (255, 120, 80), [tip, left, right])


def draw_hud(surface: pygame.Surface, font_big, font_med, font_sm,
             eco: Ecosystem, paused: bool, speed_mul: int) -> None:
    ox = VIEW_W + 10  # HUD 左边距（相对整个窗口）
    y = 10
    status = eco.status()
    species = status["species"]

    # ── 标题 ──
    title = font_big.render("Ecosystem", True, (100, 200, 100))
    surface.blit(title, (ox, y)); y += 34

    # ── Tick / 状态 ──
    year = status['tick'] // 365
    day  = status['tick'] % 365
    txt = font_med.render(f"Year  {year:>4}", True, WHITE)
    surface.blit(txt, (ox, y)); y += 22
    txt = font_med.render(f"Day   {day:>4}", True, WHITE)
    surface.blit(txt, (ox, y)); y += 22
    txt = font_med.render(f"Total {status['total']:>5}", True, WHITE)
    surface.blit(txt, (ox, y)); y += 22

    state_col = (255, 200, 0) if paused else (100, 230, 100)
    state_str = "PAUSED" if paused else f"x{speed_mul}"
    txt = font_med.render(f"Speed  {state_str}", True, state_col)
    surface.blit(txt, (ox, y)); y += 30

    # ── 物种统计 ──
    pygame.draw.line(surface, BORDER_COLOR, (ox, y), (ox + PANEL_W - 20, y)); y += 8
    for name, count in sorted(species.items()):
        col = SPECIES_COLOR.get(name, DEFAULT_COLOR)
        pygame.draw.circle(surface, col, (ox + 6, y + 8), 5)
        txt = font_med.render(f"{name:<12}{count:>4}", True, col)
        surface.blit(txt, (ox + 16, y)); y += 22
    y += 6

    # ── 平均适应度（按物种） ──
    pygame.draw.line(surface, BORDER_COLOR, (ox, y), (ox + PANEL_W - 20, y)); y += 8
    by_sp: dict = {}
    for org in eco.organisms:
        by_sp.setdefault(org.name, []).append(org.fitness_score)
    for name, scores in sorted(by_sp.items()):
        avg = sum(scores) / len(scores) if scores else 0
        col = SPECIES_COLOR.get(name, DEFAULT_COLOR)
        txt = font_sm.render(f"{name} fit {avg:>5.1f}", True, col)
        surface.blit(txt, (ox, y)); y += 18
    y += 8

    # ── 环境因素 ──
    pygame.draw.line(surface, BORDER_COLOR, (ox, y), (ox + PANEL_W - 20, y)); y += 8
    for factor in eco.factors:
        val_str = ""
        if hasattr(factor, "current_temp"):
            val_str = f"{factor.current_temp:.1f}°C"
        elif hasattr(factor, "water_level"):
            val_str = f"{factor.water_level:.0f}/{factor.max_level:.0f}"
        elif hasattr(factor, "food_level"):
            val_str = f"{factor.food_level:.0f}"
        if val_str:
            txt = font_sm.render(f"{factor.name:<12}{val_str}", True, GRAY)
            surface.blit(txt, (ox, y)); y += 17
    y += 10

    # ── 快捷键提示 ──
    pygame.draw.line(surface, BORDER_COLOR, (ox, y), (ox + PANEL_W - 20, y)); y += 8
    hints = ["[Space] Pause", "[+/-] Speed", "[R] Reset", "[ESC] Quit"]
    for h in hints:
        txt = font_sm.render(h, True, DIM)
        surface.blit(txt, (ox, y)); y += 16


# ── 主循环 ────────────────────────────────────────────────────────────────────

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("🌿 Ecosystem Simulation")
    clock = pygame.time.Clock()

    try:
        font_big = pygame.font.SysFont("monospace", 20, bold=True)
        font_med = pygame.font.SysFont("monospace", 15)
        font_sm  = pygame.font.SysFont("monospace", 13)
    except Exception:
        font_big = font_med = font_sm = pygame.font.Font(None, 18)

    # 世界视口 surface（左侧）
    world_surf = pygame.Surface((VIEW_W, VIEW_H))

    eco = make_ecosystem()
    paused = False
    speed_mul = 1   # 每帧执行多少步模拟

    running = True
    while running:
        # ── 事件处理 ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed_mul = min(speed_mul * 2, 16)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed_mul = max(speed_mul // 2, 1)
                elif event.key == pygame.K_r:
                    eco = make_ecosystem()

        # ── 模拟步进 ──
        if not paused:
            for _ in range(speed_mul):
                eco.step()

        # ── 绘制世界视口 ──
        world_surf.fill(BG_COLOR)
        draw_grid(world_surf)
        for org in eco.organisms:
            draw_organism(world_surf, org)

        # ── 合成到屏幕 ──
        screen.fill(PANEL_COLOR)
        screen.blit(world_surf, (0, 0))
        # 视口边框
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, VIEW_W, VIEW_H), 1)

        draw_hud(screen, font_big, font_med, font_sm, eco, paused, speed_mul)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
