"""s00 · Cold open: a lattice is heated, then slowly cooled through T_c (Metropolis movie, 512²)."""
from _common import Narrated, Movie, Thermometer, LEFT, RIGHT, DOWN, UP
from common.narrative import PAUSE
from common.style import BG, FG, MUTED
from manim import FadeIn, FadeOut, Rectangle, Tex, VGroup, Create, Write, config


class ColdOpen(Narrated):
    def line(self, text, phase, a0=0.0, a1=1.0, extra=0.0, also=(), therm=True):
        d = self.voice(text)
        th = self.therm if therm else None     # an animated mobject is added to the scene: not before it shows
        self.play(self.movie.play(phase, self.img, th, a0, a1), *also, run_time=d + PAUSE + extra)

    def construct(self):
        self.movie = mv = Movie("cooling")
        self.img = img = mv.image("cold", 0, height=6.8).shift(1.3 * LEFT)
        self.therm = therm = Thermometer(T=1.5).shift(4.9 * RIGHT + 0.4 * DOWN)
        hot = Tex("hot", font_size=26, color=MUTED).next_to(therm.tube.get_corner(UP + RIGHT), RIGHT, buff=0.25)
        cold = Tex("cold", font_size=26, color=MUTED).next_to(therm.tube.get_corner(DOWN + RIGHT), RIGHT, buff=0.25)
        self.play(FadeIn(img), run_time=1.2)

        self.line("This is a magnet. Or rather, a cartoon of one: a grid of tiny arrows, "
                  "each pointing either up, in gold, or down, in blue.", "cold", therm=False)
        self.play(FadeIn(therm), FadeIn(hot), FadeIn(cold), run_time=0.8)
        self.line("Heat it up, and the order melts away into noise.", "heat")
        self.line("Now let's cool it down again, slowly, and watch.", "cool")
        self.line("Something strange happens on the way. Islands appear, inside islands, inside islands. "
                  "Patterns of every size, constantly boiling.", "tc", 0.0, 0.5)
        mark = therm.tc_mark()
        self.line("And it happens at one precise temperature, about two point two seven. "
                  "Keep that number in mind.", "tc", 0.5, 1.0, also=(Create(mark[0]), Write(mark[1])))
        self.line("Cool a little further, and one colour takes over.", "below", 0.0, 0.45)
        self.line("Yet each of these arrows only ever talks to its four nearest neighbours. "
                  "Nobody tells them which way to point. So how do a quarter of a million of them "
                  "end up deciding, together?", "below", 0.45, 1.0)

        veil = Rectangle(width=config.frame_width + 1, height=config.frame_height + 1,
                         stroke_width=0, fill_color=BG, fill_opacity=0.78)
        title = Tex(r"The Ising model", font_size=96, color=FG)
        sub = Tex(r"a century of key results", font_size=40, color=MUTED).next_to(title, DOWN, buff=0.35)
        d = self.voice("Answering that question took physicists twenty years, and produced one of the "
                       "most beautiful stories in science. This is the Ising model.")
        self.play(FadeIn(veil), FadeOut(VGroup(therm, hot, cold, mark)), run_time=1.5)
        self.play(Write(title), FadeIn(sub, shift=0.2 * UP), run_time=2)
        self.wait(max(0.5, d + PAUSE - 3.5) + 1.0)
        self.play(FadeOut(veil), FadeOut(title), FadeOut(sub), FadeOut(img), run_time=1.2)
