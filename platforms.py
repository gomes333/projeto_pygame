"""Plataformas. (Nomeado platforms.py para não colidir com o módulo `platform` do Python.)"""
import math

import pygame

from settings import DIM_COLORS, NEUTRAL_COLOR


class Platform:
    """dimension=None -> sempre sólida (neutra). BLUE/PURPLE -> sólida só nessa dimensão."""

    def __init__(self, x, y, w, h, dimension=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.dimension = dimension
        self.solidity = 1.0 if dimension is None else 0.0  # 0..1, só para o visual

    @property
    def color(self):
        return NEUTRAL_COLOR if self.dimension is None else DIM_COLORS[self.dimension]

    def is_solid(self, current):
        return self.dimension is None or self.dimension == current

    def update(self, current):
        target = 1.0 if self.is_solid(current) else 0.0
        self.solidity += (target - self.solidity) * 0.25
        if abs(target - self.solidity) < 0.01:
            self.solidity = target

    def snap(self, current):
        self.solidity = 1.0 if self.is_solid(current) else 0.0

    def draw(self, surface, time):
        a = self.solidity
        r = self.rect
        pad = 12
        layer = pygame.Surface((r.w + pad * 2, r.h + pad * 2), pygame.SRCALPHA)
        inner = pygame.Rect(pad, pad, r.w, r.h)
        c = self.color

        if a > 0.02:  # brilho neon
            glow = int(38 * a)
            pygame.draw.rect(layer, (*c, glow), inner.inflate(20, 20), border_radius=8)
            pygame.draw.rect(layer, (*c, glow * 2), inner.inflate(8, 8), border_radius=5)

        fill = tuple(int(v * 0.28) for v in c)
        pygame.draw.rect(layer, (*fill, int(22 + 233 * a)), inner)

        flicker = 0 if a > 0.5 else int(25 * math.sin(time * 4 + r.x * 0.01))
        pygame.draw.rect(layer, (*c, max(0, min(255, int(75 + 180 * a) + flicker))), inner, 2)

        if a > 0.5:  # textura pixelada + brilho no topo
            for x in range(inner.left + 8, inner.right - 6, 16):
                pygame.draw.rect(layer, (*c, int(90 * a)), (x, inner.top + 6, 3, 3))
            pygame.draw.line(layer, (255, 255, 255, int(170 * a)),
                             (inner.left + 2, inner.top + 1), (inner.right - 3, inner.top + 1))
        surface.blit(layer, (r.x - pad, r.y - pad))
