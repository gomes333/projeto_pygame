"""Constantes globais de ECHOES."""

WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "ECHOES — The Lost Room"

# Física
GRAVITY = 0.62
MAX_FALL = 15
MOVE_SPEED = 5.0
GROUND_ACCEL = 0.35
AIR_ACCEL = 0.22
JUMP_SPEED = -13.5
COYOTE_FRAMES = 6        # tolerância para pular logo após sair da borda
JUMP_BUFFER_FRAMES = 7   # tolerância para apertar pulo um pouco antes de pousar

# Dimensões
BLUE = 0
PURPLE = 1
DIM_NAMES = {BLUE: "AZUL", PURPLE: "ROXA"}
DIM_COLORS = {BLUE: (70, 170, 255), PURPLE: (190, 95, 255)}
DIM_BG_TOP = {BLUE: (6, 12, 30), PURPLE: (20, 6, 36)}
DIM_BG_BOTTOM = {BLUE: (14, 40, 84), PURPLE: (54, 18, 84)}

NEUTRAL_COLOR = (140, 150, 175)
PORTAL_COLOR = (120, 255, 200)
DANGER_COLOR = (255, 80, 90)
WHITE = (240, 244, 255)
