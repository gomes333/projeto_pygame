"""Simulador puro-Python da física do jogador (espelha player.py) para validar saltos."""
from settings import *

PW, PH = 24, 36


class Box:
    def __init__(self, x, y, w, h, dim=None):
        self.x, self.y, self.w, self.h, self.dim = x, y, w, h, dim
    @property
    def left(self): return self.x
    @property
    def right(self): return self.x + self.w
    @property
    def top(self): return self.y
    @property
    def bottom(self): return self.y + self.h
    def solid(self, d): return self.dim is None or self.dim == d


def overlap(ax, ay, aw, ah, b):
    return ax < b.right and ax + aw > b.left and ay < b.bottom and ay + ah > b.top


def kill_box(h):
    """Área mortal do espinho (igual a Hazard.kill_rect em platforms.py)."""
    if h.h <= 20:   # faixa de espinhos
        return Box(h.x + 4, h.y + 6, h.w - 8, h.h - 6)
    return Box(h.x + 4, h.y + 4, h.w - 8, h.h - 8)   # mina flutuante


def simulate(plats, haz, A, B, d0, x0, direction, delay, sf, max_frames=140):
    """Retorna True se, partindo de A, o jogador pousa em B."""
    dim = d0
    px, py = float(x0), float(A.top - PH)
    vx = vy = 0.0
    on_ground = True
    coyote = 0
    jumped = False
    jump_frame = None
    f = 0
    rnd = round
    while f < max_frames:
        # entrada
        want_jump = (f == delay)
        move = direction
        if jumped and sf is not None and f - jump_frame == sf:
            new = 1 - dim
            if not any(p.dim == new and overlap(rnd(px), rnd(py), PW, PH, p) for p in plats):
                dim = new
        solids = [p for p in plats if p.solid(dim)]
        accel = GROUND_ACCEL if on_ground else AIR_ACCEL
        vx += (move * MOVE_SPEED - vx) * accel
        if move == 0 and abs(vx) < 0.1:
            vx = 0
        coyote = COYOTE_FRAMES if on_ground else max(0, coyote - 1)
        if want_jump and coyote:
            vy = JUMP_SPEED; coyote = 0; on_ground = False
            jumped = True; jump_frame = f
        # X
        px = max(0, min(WIDTH - PW, px + vx))
        rx = rnd(px); ry = rnd(py)
        for r in solids:
            if overlap(rx, ry, PW, PH, r):
                if vx > 0: rx = r.left - PW
                elif vx < 0: rx = r.right
                px = rx; vx = 0
        # Y
        vy = min(vy + GRAVITY, MAX_FALL)
        py += vy
        ry = rnd(py)
        on_ground = False
        for r in solids:
            if overlap(rx, ry, PW, PH, r):
                if vy > 0:
                    ry = r.top - PH; on_ground = True
                elif vy < 0:
                    ry = r.bottom
                py = ry; vy = 0
                landed_on = r
        if ry > HEIGHT + 60:
            return False
        for h in haz:
            if h.solid(dim) and overlap(rx + 3, ry + 3, PW - 6, PH - 4, kill_box(h)):
                return False
        if jumped and on_ground and f > jump_frame:
            return landed_on is B
        f += 1
    return False


def hop_stats(plats, haz, A, B):
    dims = [A.dim] if A.dim is not None else [BLUE, PURPLE]
    total = ok = 0
    for d0 in dims:
        for x0 in range(int(A.left) - 0, int(A.right - PW) + 1, 16):
            if x0 < A.left or x0 + PW > A.right:
                continue
            for direction in (-1, 0, 1):
                for delay in (0, 6, 12, 24):
                    for sf in [None] + list(range(0, 60, 4)):
                        total += 1
                        if simulate(plats, haz, A, B, d0, x0, direction, delay, sf):
                            ok += 1
    return ok, total
