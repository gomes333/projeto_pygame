"""Fases, portal e sistema de partículas.

Cada fase é um dicionário em LEVELS. Plataformas: (x, y, largura, altura, dimensão)
  dimensão = N (neutra, sempre sólida), B (azul) ou P (roxa).
"platforms" = caminho principal, em ordem. "blockers" = plataformas extras que
atrapalham (ex.: tetos que bloqueiam a troca de dimensão).
"""
import math
import random

import pygame

from platforms import Platform
from settings import *

N, B, P = None, BLUE, PURPLE

LEVELS = [
    # ---------------------------------------------------------------- FASE 1 — FÁCIL
    {
        "name": "DESPERTAR",
        "difficulty": "FÁCIL",
        "color": (120, 255, 160),
        "hint": "Em plataformas cinzas é seguro apertar SHIFT. Troque antes de pular!",
        "spawn": (60, 224),
        "portal": (480, 650),
        "platforms": [
            (0, 260, 240, 20, N),      # início
            (320, 300, 140, 20, N),
            (540, 340, 140, 20, B),    # você começa na dimensão azul
            (760, 380, 140, 20, N),    # descanse aqui e aperte SHIFT (roxo)
            (980, 420, 140, 20, P),
            (1160, 480, 110, 20, N),   # descanse aqui e aperte SHIFT (azul)
            (1000, 540, 130, 20, B),
            (820, 580, 130, 20, N),    # descanse aqui e aperte SHIFT (roxo)
            (640, 620, 130, 20, P),
            (380, 650, 200, 20, N),    # saída
        ],
        "blockers": [],
    },
    # ---------------------------------------------------------------- FASE 2 — MÉDIO
    {
        "name": "ECOS",
        "difficulty": "MÉDIO",
        "color": (255, 200, 90),
        "hint": "Troque de dimensão NO AR. Cuidado: o teto roxo bloqueia a troca.",
        "spawn": (50, 604),
        "portal": (100, 330),
        "platforms": [
            (0, 640, 220, 80, N),
            (290, 590, 90, 20, B),
            (450, 540, 90, 20, P),
            (610, 490, 90, 20, B),
            (790, 450, 90, 20, P),
            (950, 400, 90, 20, B),
            (1110, 350, 90, 20, P),
            (950, 290, 90, 20, B),
            (790, 240, 90, 20, P),
            (630, 190, 90, 20, B),
            (470, 240, 90, 20, P),
            (310, 290, 90, 20, B),
            (0, 330, 200, 20, N),
        ],
        "blockers": [
            (590, 390, 130, 20, P),    # teto roxo sobre a 3ª plataforma
        ],
    },
    # ---------------------------------------------------------------- FASE 3 — DIFÍCIL
    {
        "name": "O ÚLTIMO ECO",
        "difficulty": "DIFÍCIL",
        "color": (255, 90, 100),
        "hint": "Plataformas da cor oposta podem bloquear a troca. Escolha o momento.",
        "spawn": (40, 614),
        "portal": (50, 370),
        "platforms": [
            (0, 650, 130, 70, N),      # troque para roxo ainda aqui (é seguro)
            (300, 610, 60, 20, P),
            (530, 570, 60, 20, B),
            (760, 520, 60, 20, P),
            (990, 470, 60, 20, B),
            (1190, 410, 60, 20, P),
            (1010, 330, 60, 20, B),
            (800, 270, 60, 20, P),
            (590, 230, 60, 20, B),
            (390, 280, 60, 20, P),
            (210, 320, 60, 20, B),
            (0, 370, 100, 20, N),
        ],
        "blockers": [
            (510, 460, 100, 20, P),    # teto roxo sobre a 1ª plataforma azul
            (1170, 310, 100, 20, B),   # teto azul sobre a plataforma roxa da direita
            (570, 120, 100, 20, P),    # teto roxo sobre a plataforma azul do topo
            (370, 170, 100, 20, B),    # teto azul sobre a última plataforma roxa
        ],
    },
]

NUM_LEVELS = len(LEVELS)


class ParticleSystem:
    def __init__(self):
        self.items = []

    def emit(self, x, y, color, count=10, speed=3.0, life=(20, 40), gravity=0.08,
             size=(2, 4), angle=None, arc=math.pi * 2):
        for _ in range(count):
            a = random.uniform(0, math.tau) if angle is None else angle + random.uniform(-arc / 2, arc / 2)
            s = random.uniform(0.3, 1.0) * speed
            l = random.randint(*life)
            self.items.append([x, y, math.cos(a) * s, math.sin(a) * s, l, l, color,
                               random.randint(*size), gravity])

    def update(self):
        for p in self.items:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += p[8]
            p[4] -= 1
        self.items = [p for p in self.items if p[4] > 0]

    def draw(self, layer):
        for x, y, _, _, life, maxlife, color, size, _ in self.items:
            pygame.draw.rect(layer, (*color, int(255 * life / maxlife)), (int(x), int(y), size, size))


class Level:
    def __init__(self, index=0):
        data = LEVELS[index]
        self.index = index
        self.name = data["name"]
        self.difficulty = data["difficulty"]
        self.color = data["color"]
        self.hint = data["hint"]
        self.platforms = [Platform(*t) for t in data["platforms"] + data["blockers"]]
        self.spawn = data["spawn"]
        self.portal = pygame.Rect(0, 0, 44, 72)
        self.portal.midbottom = data["portal"]

    def snap(self, dim):
        for p in self.platforms:
            p.snap(dim)

    def update(self, dim):
        for p in self.platforms:
            p.update(dim)

    def solids(self, dim):
        return [p.rect for p in self.platforms if p.is_solid(dim)]

    def blocks(self, rect, new_dim):
        """True se alternar para new_dim deixaria uma plataforma sólida dentro do jogador."""
        return any(p.dimension == new_dim and rect.colliderect(p.rect) for p in self.platforms)

    def draw_portal(self, surface, time):
        cx, cy = self.portal.center
        for i in range(6):
            pulse = math.sin(time * 3 + i * 0.8)
            w = self.portal.w - i * 6 + pulse * 3
            h = self.portal.h - i * 9 + pulse * 4
            rect = pygame.Rect(0, 0, max(4, w), max(4, h))
            rect.center = (cx, cy)
            t = i / 5
            col = tuple(int(a + (255 - a) * t) for a in PORTAL_COLOR)
            pygame.draw.ellipse(surface, col, rect, 2)
