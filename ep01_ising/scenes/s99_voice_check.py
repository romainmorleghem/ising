"""Smoke test of the narration pipeline (not part of the episode): manim -ql s99_voice_check.py VoiceCheck"""
from _common import Narrated, spin_image, np
from manim import MathTex, FadeIn, Write, RIGHT, LEFT


class VoiceCheck(Narrated):
    def construct(self):
        self.chapter("Voice check")
        s = np.where(np.random.default_rng(0).random((48, 48)) < 0.5, 1, -1)
        grid = spin_image(s, 5).shift(3 * LEFT)
        eq = MathTex(r"H=-J\sum_{\langle i,j\rangle} s_i s_j", font_size=46).shift(3 * RIGHT)
        self.say("In 1925, Ernst Ising studied a toy model of a magnet.", FadeIn(grid))
        self.say(r"$H=-J\sum s_i s_j$", Write(eq),
                 speech="Its energy is minus J, times the sum over neighbouring pairs of s i times s j.")
        self.say("Below a critical temperature, T c, about two point two seven, the spins align.")
