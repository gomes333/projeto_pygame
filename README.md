# ECHOES — The Lost Room

Jogo 2D de plataforma em Python + Pygame. Você acordou em uma instalação desconhecida.
A realidade tem duas dimensões — só alternando entre elas você encontra a saída.

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

## Controles

| Ação | Tecla |
|---|---|
| Mover | A / D ou setas |
| Pular | Espaço (segure para pulo alto, solte para pulo baixo) |
| Alternar dimensão | Shift |
| Reiniciar | R |
| Menu / sair | Esc |
| Escolher fase (no menu) | 1, 2 ou 3 |

## Fases

| # | Nome | Dificuldade | O que muda |
|---|---|---|---|
| 1 | DESPERTAR | Fácil | Percurso descendo, com plataformas cinzas para trocar de dimensão com segurança. |
| 2 | ECOS | Médio | Subida com troca de dimensão **no ar** a cada salto e um teto roxo que bloqueia a troca. |
| 3 | O ÚLTIMO ECO | Difícil | Plataformas estreitas, saltos longos e quatro tetos que bloqueiam a troca na hora errada. |

## Mecânica

- **Dimensão azul:** plataformas azuis ficam sólidas.
- **Dimensão roxa:** plataformas roxas ficam sólidas.
- Plataformas cinza são sempre sólidas.
- Se uma plataforma da outra dimensão estiver ocupando o espaço do personagem, a troca é **bloqueada**.
- Cair da tela reinicia a fase (conta como morte). R reinicia sem contar morte.

## Estrutura

```
ECHOES/
├── main.py        # loop, estados (menu/jogo/fase completa/vitória), efeitos, HUD
├── settings.py    # constantes (física, cores, tela)
├── player.py      # sprite pixel art, movimento, colisão
├── level.py       # as 3 fases, portal, partículas
├── platforms.py   # plataformas (não usar o nome platform.py: conflita com o módulo do Python)
├── audio.py       # sons e música gerados por código
└── assets/        # espaço para sprites/sons próprios
```

## Editando as fases

Em `level.py`, cada fase é um item da lista `LEVELS`. Cada plataforma é
`(x, y, largura, altura, dimensão)`, com dimensão `N` (neutra), `B` (azul) ou `P` (roxa).
`platforms` é o caminho principal e `blockers` são plataformas extras que atrapalham.
Para criar a fase 4, basta copiar um item da lista e ajustar. A tela tem 1280x720.

Referência de física: um pulo sobe até ~145 px e alcança ~200 px na horizontal em corrida.

## Ajustando a sensação do pulo

Em `settings.py`: `GRAVITY`, `JUMP_SPEED`, `MOVE_SPEED`, `COYOTE_FRAMES`.
