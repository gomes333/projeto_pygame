"""ECHOES — The Lost Room
Controles: A/D ou setas = mover | ESPAÇO = pular | SHIFT = alternar dimensão | R = reiniciar
3 fases: Fácil, Média e Difícil.
"""
import math
import random
import sys

import pygame

from audio import Sfx
from level import LEVELS, NUM_LEVELS, Level, ParticleSystem
from player import Player
from settings import *


# ---------- utilidades ----------
def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


_fonts = {}


def draw_text(surface, msg, size, color, pos, anchor="center", scale=1, alpha=255):
    """Texto sem antialias (+ escala 'nearest') para manter o visual pixelado."""
    font = _fonts.get(size) or _fonts.setdefault(size, pygame.font.Font(None, size))
    img = font.render(msg, False, color).convert_alpha()
    if scale != 1:
        img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
    if alpha < 255:
        img.set_alpha(alpha)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(img, rect)
    return rect


def make_background(dim):
    surf = pygame.Surface((WIDTH, HEIGHT))
    top, bottom = DIM_BG_TOP[dim], DIM_BG_BOTTOM[dim]
    for y in range(HEIGHT):
        pygame.draw.line(surf, lerp_color(top, bottom, y / HEIGHT), (0, y), (WIDTH, y))
    grid = lerp_color(bottom, DIM_COLORS[dim], 0.12)
    for x in range(0, WIDTH, 80):
        pygame.draw.line(surf, grid, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 80):
        pygame.draw.line(surf, grid, (0, y), (WIDTH, y))
    return surf.convert()


def make_glow(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    for r in range(radius, 0, -3):
        k = (1 - r / radius) ** 2.2 * 0.6
        pygame.draw.circle(surf, tuple(int(c * k) for c in color), (radius, radius), r)
    return surf.convert()


def make_vignette():
    small = pygame.Surface((80, 45), pygame.SRCALPHA)
    for y in range(45):
        for x in range(80):
            d = math.hypot((x - 40) / 40, (y - 22.5) / 22.5)
            small.set_at((x, y), (0, 0, 0, int(max(0, min(255, (d - 0.6) * 1.5 * 255)))))
    return pygame.transform.smoothscale(small, (WIDTH, HEIGHT)).convert_alpha()


def fmt_time(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


# ---------- jogo ----------
class Game:
    GLOW_R = 140

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.sfx = Sfx()
        self.sfx.start_music()

        self.bg = {BLUE: make_background(BLUE), PURPLE: make_background(PURPLE)}
        self.glows = {BLUE: make_glow(self.GLOW_R, DIM_COLORS[BLUE]),
                      PURPLE: make_glow(self.GLOW_R, DIM_COLORS[PURPLE]),
                      "portal": make_glow(self.GLOW_R, PORTAL_COLOR)}
        self.vignette = make_vignette()
        self.world = pygame.Surface((WIDTH, HEIGHT))
        self.fx = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.flash_surf = pygame.Surface((WIDTH, HEIGHT))
        self.dark = pygame.Surface((WIDTH, HEIGHT))

        rng = random.Random(7)
        self.stars = [[rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT), rng.uniform(4, 14),
                       rng.choice((2, 2, 3)), rng.uniform(0, 6.28)] for _ in range(70)]
        self.particles = ParticleSystem()
        self.waves = []
        self.time = 0.0
        self.state = "menu"
        self.reset_session()

    def reset_session(self):
        self.level_index = 0
        self.level = Level(0)                  # também serve de fundo do menu
        self.player = Player(self.level.spawn)
        self.dim = BLUE
        self.dim_mix = 0.0
        self.level.snap(self.dim)
        self.deaths = 0
        self.level_deaths = 0
        self.level_time = 0.0
        self.total_time = 0.0
        self.results = []                      # (nome, tempo, mortes) de cada fase concluída
        self.flash = 0.0
        self.flash_color = DIM_COLORS[BLUE]
        self.shake = 0.0
        self.message = ("", 0.0)
        self.waves.clear()
        self.particles.items.clear()

    def load_level(self, index):
        self.level_index = index
        self.level = Level(index)
        self.player = Player(self.level.spawn)
        self.dim = BLUE
        self.dim_mix = 0.0
        self.level.snap(BLUE)
        self.level_time = 0.0
        self.level_deaths = 0
        self.message = ("", 0.0)
        self.waves.clear()
        self.particles.items.clear()
        self.flash, self.flash_color = 0.5, WHITE
        self.state = "play"

    # ---------- ações ----------
    def new_game(self, start=0):
        self.reset_session()
        self.load_level(start)

    def respawn(self):
        self.player.reset()
        self.dim = BLUE
        self.level.snap(BLUE)
        self.flash, self.flash_color = 0.5, WHITE

    def die(self):
        self.deaths += 1
        self.level_deaths += 1
        r = self.player.rect
        self.particles.emit(r.centerx, min(r.centery, HEIGHT - 10), DANGER_COLOR, 30, 5, gravity=0.1)
        self.shake = 10
        self.sfx.play("death")
        self.respawn()

    def complete_level(self):
        self.results.append((self.level.name, self.level_time, self.level_deaths))
        self.state = "level_clear" if self.level_index < NUM_LEVELS - 1 else "win"
        cx, cy = self.level.portal.center
        self.particles.emit(cx, cy, PORTAL_COLOR, 90, 7, life=(30, 80), gravity=0.05, size=(2, 5))
        self.sfx.play("win")

    def switch_dimension(self):
        new = 1 - self.dim
        r = self.player.rect
        if self.level.blocks(r, new):
            self.shake = 8
            self.message = ("SEM ESPAÇO PARA ALTERNAR AQUI", 1.3)
            self.particles.emit(r.centerx, r.centery, DANGER_COLOR, 10, 3, life=(10, 25), gravity=0)
            self.sfx.play("denied")
            return
        self.dim = new
        self.waves.append([r.centerx, r.centery, 0.0, DIM_COLORS[new]])
        self.flash, self.flash_color = 0.6, DIM_COLORS[new]
        self.particles.emit(r.centerx, r.centery, DIM_COLORS[new], 28, 5, life=(20, 45), gravity=0.02)
        self.sfx.play("switch")

    # ---------- eventos ----------
    JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)

    def handle_event(self, e):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYUP and self.state == "play" and e.key in self.JUMP_KEYS:
            self.player.release_jump()
        if e.type != pygame.KEYDOWN:
            return
        if self.state == "menu":
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.new_game(0)
            elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.new_game(e.key - pygame.K_1)
            elif e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif self.state == "play":
            if e.key in self.JUMP_KEYS:
                self.player.press_jump()
            elif e.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.switch_dimension()
            elif e.key == pygame.K_r:
                self.respawn()
            elif e.key == pygame.K_ESCAPE:
                self.reset_session()
                self.state = "menu"
        elif self.state == "level_clear":
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.load_level(self.level_index + 1)
            elif e.key == pygame.K_ESCAPE:
                self.reset_session()
                self.state = "menu"
        elif self.state == "win":
            if e.key == pygame.K_RETURN:
                self.new_game(0)
            elif e.key == pygame.K_ESCAPE:
                self.reset_session()
                self.state = "menu"

    # ---------- atualização ----------
    def update(self, dt):
        self.time += dt
        self.particles.update()
        self.flash = max(0.0, self.flash - dt * 2.2)
        self.shake = self.shake * 0.85 if self.shake > 0.3 else 0.0
        self.message = (self.message[0], max(0.0, self.message[1] - dt))
        for w in self.waves:
            w[2] += dt
        self.waves = [w for w in self.waves if w[2] < 0.8]
        for s in self.stars:
            s[1] -= s[2] * dt
            if s[1] < -4:
                s[0], s[1] = random.uniform(0, WIDTH), HEIGHT + 4

        # brasas ambiente
        if random.random() < 0.3:
            c = lerp_color(DIM_COLORS[BLUE], DIM_COLORS[PURPLE], self.dim_mix)
            self.particles.emit(random.uniform(0, WIDTH), HEIGHT, c, 1, 1.0, life=(80, 160),
                                gravity=-0.005, size=(2, 3), angle=-math.pi / 2, arc=0.5)

        if self.state == "menu":  # demonstra a mecânica alternando sozinho
            self.dim = int(self.time / 2.2) % 2
        self.dim_mix += (self.dim - self.dim_mix) * min(1.0, dt * 9)
        self.level.update(self.dim)

        if random.random() < 0.25:  # partículas do portal
            r = self.level.portal
            self.particles.emit(random.uniform(r.left, r.right), r.bottom - 6, PORTAL_COLOR, 1, 1.2,
                                life=(30, 60), gravity=-0.01, angle=-math.pi / 2, arc=0.6)

        if self.state != "play":
            return
        self.level_time += dt
        self.total_time += dt
        p = self.player
        p.update(pygame.key.get_pressed(), self.level.solids(self.dim))
        if p.just_jumped:
            self.sfx.play("jump")
            self.particles.emit(p.rect.centerx, p.rect.bottom, (200, 210, 255), 6, 1.5, life=(10, 22), gravity=0.03)
        if p.just_landed:
            self.sfx.play("land")
            self.particles.emit(p.rect.centerx, p.rect.bottom, (200, 210, 255), 8, 2, life=(10, 25), gravity=0.03)
        if p.dead:
            self.die()
        elif p.rect.colliderect(self.level.portal.inflate(-12, -8)):
            self.complete_level()

    # ---------- desenho ----------
    def draw_world(self, show_player):
        w = self.world
        w.blit(self.bg[BLUE], (0, 0))
        self.bg[PURPLE].set_alpha(int(255 * self.dim_mix))
        w.blit(self.bg[PURPLE], (0, 0))

        star_col = lerp_color(DIM_COLORS[BLUE], DIM_COLORS[PURPLE], self.dim_mix)
        for x, y, _, size, ph in self.stars:
            b = (0.35 + 0.65 * (0.5 + 0.5 * math.sin(self.time * 2 + ph))) * 0.7
            pygame.draw.rect(w, tuple(int(v * b) for v in star_col), (int(x), int(y), size, size))

        for plat in self.level.platforms:
            plat.draw(w, self.time)
        self.level.draw_portal(w, self.time)

        R = self.GLOW_R
        px, py = self.level.portal.center
        w.blit(self.glows["portal"], (px - R, py - R), special_flags=pygame.BLEND_RGB_ADD)
        if show_player:
            cx, cy = self.player.rect.center
            w.blit(self.glows[self.dim], (cx - R, cy - R), special_flags=pygame.BLEND_RGB_ADD)
            self.player.draw(w, self.dim)

        self.fx.fill((0, 0, 0, 0))
        self.particles.draw(self.fx)
        for x, y, t, color in self.waves:
            pygame.draw.circle(self.fx, (*color, int(200 * (1 - t / 0.8))), (int(x), int(y)), int(t * 1800), 5)
        w.blit(self.fx, (0, 0))
        w.blit(self.vignette, (0, 0))

    def draw_hud(self):
        s, c = self.screen, DIM_COLORS[self.dim]
        lv = self.level
        pygame.draw.rect(s, c, (24, 24, 20, 20))
        pygame.draw.rect(s, WHITE, (24, 24, 20, 20), 2)
        draw_text(s, f"DIMENSÃO {DIM_NAMES[self.dim]}", 16, c, (54, 22), "topleft", 2)
        draw_text(s, fmt_time(self.level_time), 16, WHITE, (WIDTH - 24, 22), "topright", 2)
        draw_text(s, f"MORTES {self.deaths}", 16, WHITE, (WIDTH - 24, 52), "topright", 2, 170)
        draw_text(s, f"FASE {lv.index + 1}/{NUM_LEVELS} · {lv.difficulty}", 16, lv.color,
                  (WIDTH // 2, 22), "midtop", 2)
        draw_text(s, "A/D mover  ·  ESPAÇO pular  ·  SHIFT alternar dimensão  ·  R reiniciar",
                  20, WHITE, (WIDTH // 2, HEIGHT - 16), "midbottom", 1, 120)
        t = self.level_time
        if t < 2.4:  # banner de início de fase
            a = int(255 * min(1, t * 3, (2.4 - t) * 2))
            draw_text(s, f"FASE {lv.index + 1}", 20, WHITE, (WIDTH // 2, 330), "center", 3, a)
            draw_text(s, lv.name, 32, lv.color, (WIDTH // 2, 392), "center", 3, a)
        elif t < 9:
            a = int(255 * min(1, t - 2.4, (9 - t)))
            draw_text(s, lv.hint, 18, WHITE, (WIDTH // 2, 110), "center", 2, a)
        msg, mt = self.message
        if mt > 0:
            draw_text(s, msg, 18, DANGER_COLOR, (WIDTH // 2, 160), "center", 2, int(255 * min(1, mt * 2)))

    def draw_menu(self):
        s = self.screen
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(130)
        s.blit(self.dark, (0, 0))
        cx = WIDTH // 2
        jit = 7 if int(self.time * 10) % 17 == 0 else 3   # "glitch" ocasional
        draw_text(s, "ECHOES", 32, DIM_COLORS[BLUE], (cx - jit, 190), "center", 7, 200)
        draw_text(s, "ECHOES", 32, DIM_COLORS[PURPLE], (cx + jit, 190), "center", 7, 200)
        draw_text(s, "ECHOES", 32, WHITE, (cx, 190), "center", 7)
        draw_text(s, "THE LOST ROOM", 22, DIM_COLORS[self.dim], (cx, 280), "center", 2)
        for i, line in enumerate(("Você acordou em um lugar desconhecido.",
                                  "A realidade tem dois estados. Somente observando",
                                  "os dois será possível encontrar a saída.")):
            draw_text(s, line, 18, WHITE, (cx, 370 + i * 34), "center", 2, 210)
        if int(self.time * 2) % 2 == 0:
            draw_text(s, "[ ENTER ]  COMEÇAR", 20, PORTAL_COLOR, (cx, 520), "center", 2)
        draw_text(s, "ou escolha a fase:  1 FÁCIL   ·   2 MÉDIO   ·   3 DIFÍCIL",
                  18, WHITE, (cx, 575), "center", 2, 190)
        draw_text(s, "A/D ou SETAS: mover   ·   ESPAÇO: pular   ·   SHIFT: alternar dimensão   ·   R: reiniciar",
                  20, WHITE, (cx, HEIGHT - 50), "center", 1, 150)

    def draw_level_clear(self):
        s = self.screen
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(170)
        s.blit(self.dark, (0, 0))
        cx = WIDTH // 2
        lv = self.level
        name, t, d = self.results[-1]
        nxt = LEVELS[self.level_index + 1]
        draw_text(s, f"FASE {lv.index + 1} COMPLETA", 32, lv.color, (cx, 200), "center", 4)
        draw_text(s, f"{name}  ·  Tempo {fmt_time(t)}  ·  Mortes {d}", 20, WHITE, (cx, 300), "center", 2)
        draw_text(s, f"Próxima: FASE {lv.index + 2} — {nxt['name']} ({nxt['difficulty']})",
                  18, nxt["color"], (cx, 390), "center", 2)
        if int(self.time * 2) % 2 == 0:
            draw_text(s, "[ ENTER ]  CONTINUAR", 20, PORTAL_COLOR, (cx, 490), "center", 2)
        draw_text(s, "ESC: menu", 20, WHITE, (cx, 560), "center", 1, 150)

    def draw_win(self):
        s = self.screen
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(185)
        s.blit(self.dark, (0, 0))
        cx = WIDTH // 2
        draw_text(s, "VOCÊ ESCAPOU", 32, PORTAL_COLOR, (cx, 150), "center", 5)
        for i, (name, t, d) in enumerate(self.results):
            lv = next(l for l in LEVELS if l["name"] == name)
            draw_text(s, f"{name:<14} {fmt_time(t)}   mortes {d}", 20, lv["color"],
                      (cx, 270 + i * 40), "center", 2)
        draw_text(s, f"TOTAL  {fmt_time(sum(r[1] for r in self.results))}   mortes {sum(r[2] for r in self.results)}",
                  20, WHITE, (cx, 270 + len(self.results) * 40 + 20), "center", 2)
        draw_text(s, "Mas ecos de outras salas ainda sussurram...", 18, WHITE, (cx, 520), "center", 2, 170)
        draw_text(s, "ENTER: jogar de novo    ESC: menu", 20, WHITE, (cx, 590), "center", 2)

    def draw(self):
        self.draw_world(show_player=self.state == "play")
        s = int(self.shake)
        ox, oy = (random.randint(-s, s), random.randint(-s, s)) if s else (0, 0)
        if s:
            self.screen.fill((0, 0, 0))
        self.screen.blit(self.world, (ox, oy))
        if self.flash > 0:
            self.flash_surf.fill(self.flash_color)
            self.flash_surf.set_alpha(int(self.flash * 90))
            self.screen.blit(self.flash_surf, (0, 0))
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "play":
            self.draw_hud()
        elif self.state == "level_clear":
            self.draw_level_clear()
        else:
            self.draw_win()

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
