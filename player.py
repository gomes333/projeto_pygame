"""Jogador: sprite pixel art procedural, física e colisões."""
import pygame

from settings import *

S = 3  # escala do pixel art (sprite 8x12 -> 24x36)

BODY = [
    "..hhhh..",
    ".hhhhhh.",
    ".hhhhEE.",
    ".hhhhEE.",
    ".hhhhhh.",
    "..ssss..",
    ".bbbbbb.",
    ".bbbbbb.",
    ".bbbbbb.",
    "..bbbb..",
]
LEGS = {
    "idle":  ["..ll.ll.", "..ll.ll."],
    "walk1": ["..ll.ll.", ".ll...ll"],
    "walk2": ["...llll.", "...l..l."],
    "jump":  ["..l...l.", ".ll...ll"],
}
_cache = {}


def build_sprite(legs, dim, facing):
    key = (legs, dim, facing)
    if key in _cache:
        return _cache[key]
    c = DIM_COLORS[dim]
    palette = {
        "h": (74, 82, 126), "b": (50, 58, 98), "l": (34, 40, 72),
        "s": c, "E": tuple(min(255, v + 90) for v in c),
    }
    surf = pygame.Surface((8, 12), pygame.SRCALPHA)
    for y, row in enumerate(BODY + LEGS[legs]):
        for x, ch in enumerate(row):
            if ch != ".":
                surf.set_at((x, y), palette[ch])
    surf = pygame.transform.scale(surf, (8 * S, 12 * S))
    if facing < 0:
        surf = pygame.transform.flip(surf, True, False)
    _cache[key] = surf
    return surf


class Player:
    W, H = 8 * S, 12 * S

    def __init__(self, spawn):
        self.spawn = spawn
        self.reset()

    def reset(self):
        self.pos = pygame.Vector2(self.spawn)
        self.rect = pygame.Rect(round(self.pos.x), round(self.pos.y), self.W, self.H)
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.coyote = 0
        self.jump_buffer = 0
        self.anim = 0.0
        self.dead = False
        self.just_jumped = False
        self.just_landed = False

    # --- entrada ---
    def press_jump(self):
        self.jump_buffer = JUMP_BUFFER_FRAMES

    def release_jump(self):
        if self.vy < -4:           # pulo variável: soltar cedo = pulo menor
            self.vy *= 0.5

    # --- física ---
    def update(self, keys, solids):
        self.just_jumped = self.just_landed = False

        move = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        accel = GROUND_ACCEL if self.on_ground else AIR_ACCEL
        self.vx += (move * MOVE_SPEED - self.vx) * accel
        if move == 0 and abs(self.vx) < 0.1:
            self.vx = 0
        if move:
            self.facing = move

        self.coyote = COYOTE_FRAMES if self.on_ground else max(0, self.coyote - 1)
        self.jump_buffer = max(0, self.jump_buffer - 1)
        if self.jump_buffer and self.coyote:
            self.vy = JUMP_SPEED
            self.jump_buffer = self.coyote = 0
            self.on_ground = False
            self.just_jumped = True

        # eixo X
        self.pos.x = max(0, min(WIDTH - self.W, self.pos.x + self.vx))
        self.rect.x = round(self.pos.x)
        for r in solids:
            if self.rect.colliderect(r):
                if self.vx > 0:
                    self.rect.right = r.left
                elif self.vx < 0:
                    self.rect.left = r.right
                self.pos.x = self.rect.x
                self.vx = 0

        # eixo Y
        was_ground = self.on_ground
        impact = self.vy
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.pos.y += self.vy
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        for r in solids:
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = r.bottom
                self.pos.y = self.rect.y
                self.vy = 0
        if self.on_ground and not was_ground and impact > 4:
            self.just_landed = True

        if self.rect.top > HEIGHT + 60:
            self.dead = True

        if abs(self.vx) > 0.5:
            self.anim += 0.2

    def draw(self, surface, dim):
        if not self.on_ground:
            legs = "jump"
        elif abs(self.vx) > 0.5:
            legs = "walk1" if int(self.anim) % 2 == 0 else "walk2"
        else:
            legs = "idle"
        surface.blit(build_sprite(legs, dim, self.facing), self.rect.topleft)
