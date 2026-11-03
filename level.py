"""Fase única, portal e sistema de partículas."""
import math
import random

import pygame

from platforms import Platform
from settings import *


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
    """Sala única. Para editar a fase, mexa na lista de plataformas abaixo."""

    def __init__(self):
        B, P = BLUE, PURPLE
        self.platforms = [
            Platform(0, 640, 280, 80),            # início (neutra)
            Platform(350, 590, 100, 20, B),
            Platform(520, 540, 100, 20, P),
            Platform(690, 490, 100, 20, B),
            Platform(680, 380, 120, 20, P),       # "teto" roxo: bloqueia a troca ao passar por baixo
            Platform(860, 440, 100, 20, P),
            Platform(1030, 390, 100, 20, B),
            Platform(1160, 340, 120, 20),         # descanso (neutra)
            Platform(1000, 280, 100, 20, P),
            Platform(830, 230, 100, 20, B),
            Platform(660, 180, 100, 20, P),
            Platform(490, 230, 100, 20, B),
            Platform(320, 280, 100, 20, P),
            Platform(0, 330, 220, 20),            # saída (neutra)
        ]
        self.spawn = (60, 640 - 36)
        self.portal = pygame.Rect(0, 0, 44, 72)
        self.portal.midbottom = (110, 330)

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
