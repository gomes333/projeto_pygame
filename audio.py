"""Sons e música gerados por código (sem arquivos). Se não houver áudio, o jogo fica mudo."""
import array
import math

import pygame


class Sfx:
    def __init__(self):
        self.sounds = {}
        self.music = None
        try:
            init = pygame.mixer.get_init()
            if not init:
                pygame.mixer.init(44100, -16, 1, 512)
                init = pygame.mixer.get_init()
            if not init or abs(init[1]) != 16:
                return
            self.rate, _, self.channels = init
            tone = self._tone
            self.sounds = {
                "jump": self._make(tone(300, 620, 0.12, 0.35)),
                "land": self._make(tone(140, 60, 0.08, 0.4)),
                "switch": self._make(tone(180, 900, 0.28, 0.35)),
                "denied": self._make(tone(130, 100, 0.18, 0.35, square=True)),
                "death": self._make(tone(420, 70, 0.35, 0.3, square=True)),
                "win": self._make(tone(523, 523, 0.12, 0.35) + tone(659, 659, 0.12, 0.35)
                                  + tone(784, 784, 0.12, 0.35) + tone(1047, 1047, 0.35, 0.35)),
            }
            self.music = self._make(self._drone())
        except Exception:
            self.sounds, self.music = {}, None

    def _tone(self, f0, f1, dur, vol, square=False):
        n = int(self.rate * dur)
        out, phase = [], 0.0
        for i in range(n):
            t = i / n
            phase += math.tau * (f0 + (f1 - f0) * t) / self.rate
            s = math.sin(phase)
            if square:
                s = 1.0 if s >= 0 else -1.0
            out.append(vol * s * (1 - t) ** 1.5 * min(1.0, i / 200))
        return out

    def _drone(self, seconds=4, vol=0.3):
        out = []
        for i in range(int(self.rate * seconds)):
            t = i / self.rate
            s = (0.6 * math.sin(math.tau * 55 * t) + 0.4 * math.sin(math.tau * 82.5 * t)
                 + 0.15 * math.sin(math.tau * 110 * t)) * (0.75 + 0.25 * math.sin(math.tau * 0.5 * t))
            out.append(vol * s / 1.2)
        return out

    def _make(self, samples):
        buf = array.array("h")
        for s in samples:
            v = int(32767 * max(-1, min(1, s)))
            for _ in range(self.channels):
                buf.append(v)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play(self, name):
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def start_music(self):
        if self.music:
            self.music.set_volume(0.35)
            self.music.play(loops=-1)
