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

## Mecânica

- **Dimensão azul:** plataformas azuis ficam sólidas.
- **Dimensão roxa:** plataformas roxas ficam sólidas.
- Plataformas cinza são sempre sólidas.
- Se uma plataforma da outra dimensão estiver ocupando o espaço do personagem, a troca é **bloqueada**.
- Cair da tela reinicia a fase (conta como morte).

## Estrutura

```
ECHOES/
├── main.py        # loop, estados (menu/jogo/vitória), efeitos, HUD
├── settings.py    # constantes (física, cores, tela)
├── player.py      # sprite pixel art, movimento, colisão
├── level.py       # fase, portal, partículas
├── platforms.py   # plataformas (não usar o nome platform.py: conflita com o módulo do Python)
├── audio.py       # sons e música gerados por código
└── assets/        # espaço para sprites/sons próprios
```

## Editando a fase

Em `level.py`, cada plataforma é `Platform(x, y, largura, altura, dimensão)`.
Use `BLUE`, `PURPLE` ou nada (neutra). A tela tem 1280x720.

## Ajustando a sensação do pulo

Em `settings.py`: `GRAVITY`, `JUMP_SPEED`, `MOVE_SPEED`, `COYOTE_FRAMES`.
