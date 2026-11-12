"""Dados das 10 fases (Python puro, sem pygame, para poder ser validado por tools/validate_levels.py).

Formato de cada fase:
  name   : nome da fase
  hint   : dica mostrada no início (dificuldade e cor são adicionadas no fim do arquivo)
  route  : plataformas do caminho, EM ORDEM (a primeira é o início, a última é a saída)
  extra  : plataformas extras fora do caminho (tetos etc.)
  hazards: perigos (x, y, w, h, dimensão). Só existem (visíveis e mortais) na dimensão indicada.
           altura <= 20 -> faixa de espinhos; altura maior -> mina flutuante.
Cada plataforma: (x, y, largura, altura, dimensão)  — dimensão None = neutra (sempre sólida).
"""
from settings import BLUE as B, PURPLE as P

N = None  # neutra

LEVELS = [
    # 1 ---------------------------------------------------------------
    dict(name="Despertar",
         hint="SHIFT alterna a dimensão. Troque no ar para pousar na plataforma seguinte.",
         route=[(0, 640, 260, 80, N), (320, 610, 150, 20, B), (530, 580, 150, 20, P),
                (740, 550, 150, 20, B), (950, 520, 150, 20, P), (1160, 490, 120, 20, N)],
         extra=[], hazards=[]),
    # 2 ---------------------------------------------------------------
    dict(name="Dois Estados",
         hint="Cada cor só existe na sua dimensão.",
         route=[(0, 640, 200, 80, N), (290, 590, 110, 20, B), (500, 540, 110, 20, P),
                (710, 590, 110, 20, B), (920, 540, 110, 20, P), (1120, 480, 160, 20, N),
                (940, 410, 110, 20, B), (740, 350, 110, 20, P), (540, 300, 110, 20, B),
                (260, 250, 180, 20, N)],
         extra=[], hazards=[]),
    # 3 ---------------------------------------------------------------
    dict(name="Espinhos",
         hint="Espinhos só são perigosos na dimensão da cor deles.",
         route=[(0, 640, 200, 80, N), (270, 600, 420, 20, N), (770, 550, 110, 20, P),
                (950, 500, 110, 20, B), (1120, 440, 160, 20, N), (950, 370, 110, 20, P),
                (740, 320, 160, 20, N), (560, 270, 110, 20, B), (330, 230, 180, 20, N)],
         extra=[],
         hazards=[(400, 584, 140, 16, B), (780, 304, 80, 16, P)]),
    # 4 ---------------------------------------------------------------
    dict(name="Fenda",
         hint="Corra para saltos longos. Solte o pulo cedo para saltos curtos.",
         route=[(0, 640, 200, 80, N), (350, 610, 90, 20, B), (590, 590, 90, 20, P),
                (830, 560, 90, 20, B), (1070, 520, 90, 20, P), (1190, 460, 90, 20, N),
                (1010, 390, 90, 20, B), (790, 360, 90, 20, P), (570, 330, 90, 20, B),
                (350, 300, 90, 20, P), (80, 260, 190, 20, N)],
         extra=[], hazards=[]),
    # 5 ---------------------------------------------------------------
    dict(name="Escada",
         hint="Atravesse a plataforma da outra cor e troque quando estiver acima dela.",
         route=[(0, 640, 220, 80, N), (320, 610, 100, 20, B), (480, 540, 100, 20, P),
                (480, 435, 100, 20, B), (480, 330, 100, 20, P), (480, 225, 100, 20, B),
                (700, 200, 100, 20, P), (910, 240, 100, 20, B), (1090, 280, 190, 20, N)],
         extra=[], hazards=[]),
    # 6 ---------------------------------------------------------------
    dict(name="Pulsos",
         hint="Minas flutuantes: troque de dimensão para atravessá-las.",
         route=[(0, 640, 200, 80, N), (330, 600, 100, 20, B), (560, 560, 200, 20, N),
                (890, 520, 100, 20, P), (1110, 470, 170, 20, N), (940, 400, 100, 20, B),
                (760, 360, 100, 20, P), (580, 320, 100, 20, B), (400, 280, 100, 20, P),
                (120, 240, 180, 20, N)],
         extra=[],
         hazards=[(620, 544, 80, 16, P), (815, 400, 26, 26, B), (500, 215, 26, 26, B)]),
    # 7 ---------------------------------------------------------------
    dict(name="Tetos",
         hint="Não dá para trocar de dimensão dentro de uma plataforma.",
         route=[(0, 640, 200, 80, N), (320, 600, 100, 20, B), (540, 570, 100, 20, P),
                (760, 540, 100, 20, B), (980, 500, 100, 20, P), (1160, 440, 120, 20, N),
                (980, 360, 100, 20, B), (800, 320, 100, 20, P), (620, 280, 100, 20, B),
                (440, 240, 100, 20, P), (200, 200, 160, 20, N)],
         extra=[(300, 500, 190, 20, P), (520, 470, 190, 20, B), (740, 440, 190, 20, P),
                (960, 400, 190, 20, B), (960, 250, 190, 20, P), (780, 210, 190, 20, B)],
         hazards=[]),
    # 8 ---------------------------------------------------------------
    dict(name="Agulhas",
         hint="Plataformas estreitas e saltos longos.",
         route=[(0, 650, 150, 70, N), (300, 625, 70, 20, B), (520, 600, 70, 20, P),
                (740, 575, 70, 20, B), (960, 550, 70, 20, P), (1170, 505, 110, 20, N),
                (980, 420, 70, 20, B), (760, 400, 70, 20, P), (540, 380, 70, 20, B),
                (320, 360, 70, 20, P), (100, 340, 70, 20, B), (0, 230, 90, 20, N),
                (240, 210, 70, 20, P), (460, 190, 70, 20, B), (690, 160, 200, 20, N)],
         extra=[],
         hazards=[(1215, 489, 50, 16, B), (672, 300, 26, 26, P)]),
    # 9 ---------------------------------------------------------------
    dict(name="Torre",
         hint="Combine escadas, saltos longos e minas.",
         route=[(0, 650, 200, 70, N), (350, 620, 80, 20, B), (580, 570, 80, 20, P),
                (580, 465, 80, 20, B), (580, 360, 80, 20, P), (580, 255, 80, 20, B),
                (800, 215, 80, 20, P), (1020, 255, 80, 20, B), (1170, 160, 110, 20, N),
                (960, 120, 70, 20, P), (740, 100, 70, 20, B), (400, 80, 200, 20, N)],
         extra=[],
         hazards=[(1200, 144, 60, 16, B), (720, 150, 26, 26, B)]),
    # 10 --------------------------------------------------------------
    dict(name="O Último Eco",
         hint="Tudo o que você aprendeu. Boa sorte.",
         route=[(0, 650, 150, 70, N), (310, 630, 70, 20, B), (540, 610, 70, 20, P),
                (770, 590, 70, 20, B), (1000, 570, 70, 20, P), (1170, 470, 110, 20, N),
                (980, 400, 70, 20, B), (780, 380, 70, 20, P), (560, 360, 70, 20, B),
                (340, 340, 70, 20, P), (120, 300, 110, 20, N), (280, 230, 70, 20, B),
                (500, 200, 70, 20, P), (720, 170, 70, 20, B), (940, 140, 70, 20, P),
                (1140, 110, 140, 20, N)],
         extra=[],
         hazards=[(1215, 454, 50, 16, B)]),
]


# Rótulo de dificuldade e cor de cada fase (usados no HUD e nas telas)
TIERS = [
    ("MUITO FÁCIL", (120, 255, 160)), ("FÁCIL", (150, 255, 130)), ("FÁCIL", (190, 255, 110)),
    ("MÉDIO", (240, 240, 100)), ("MÉDIO", (255, 215, 90)), ("MÉDIO", (255, 185, 80)),
    ("DIFÍCIL", (255, 150, 80)), ("DIFÍCIL", (255, 115, 90)),
    ("MUITO DIFÍCIL", (255, 85, 105)), ("EXTREMO", (255, 70, 200)),
]
for _lv, (_label, _color) in zip(LEVELS, TIERS):
    _lv["difficulty"], _lv["color"] = _label, _color
