"""s03 · Two dimensions: Peierls' argument (1936). A wall is a line: its cost grows with its length."""
from _common import Narrated, SpinGrid, load, lattice_image, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT
from manim import (VGroup, Group, MathTex, Tex, FadeIn, FadeOut, Write, Create, LaggedStart, Transform,
                   Arrow, Dot, Line, ReplacementTransform, AnimationGroup)

BROKEN = MEANFIELD
PANEL_X = 3.5


class Peierls(Narrated):
    def construct(self):
        self.chapter("3 · Two dimensions")
        self.say("Eleven years later, in 1936, Rudolf Peierls looked again at two dimensions, "
                 "and found a simple argument that Ising had missed.")

        g = SpinGrid(np.ones((10, 10)), size=0.56).move_to([-3.4, -0.3, 0])
        self.play(LaggedStart(*[FadeIn(c) for c in g], lag_ratio=0.01), run_time=1.2)
        island = [(4, 3), (4, 4), (5, 3), (5, 4), (5, 5), (6, 4)]
        self.play(LaggedStart(*[g.flip(*c) for c in island], lag_ratio=0.1), run_time=1.2)
        walls = g.borders(BROKEN, width=7)
        E = MathTex(r"\Delta E=2J\times\ell", font_size=54, color=FG).move_to([PANEL_X, 2.0, 0])
        L1 = MathTex(rf"\ell={len(walls)}", font_size=46, color=BROKEN).next_to(E, DOWN, buff=0.4)
        self.say("In two dimensions, an island of flipped spins is surrounded by a wall, and the wall "
                 "costs two J per unit of length.", Create(walls), Write(E), FadeIn(L1))
        more = [(3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (6, 5), (6, 3), (7, 4)]
        self.play(LaggedStart(*[g.flip(*c) for c in more], lag_ratio=0.08), FadeOut(walls), run_time=1.2)
        walls2 = g.borders(BROKEN, width=7)
        L2 = MathTex(rf"\ell={len(walls2)}", font_size=46, color=BROKEN).move_to(L1)
        self.say("A bigger island has a longer wall, and costs more. Unlike in one dimension, "
                 "the price grows with the size.", Create(walls2), Transform(L1, L2))

        # counting contours: <= 3 choices per step
        c0 = g.sq[2, 7].get_corner(UP + RIGHT)
        s = g.size
        steps = [RIGHT, DOWN, DOWN, RIGHT, DOWN, LEFT, DOWN]
        pts = [c0]
        for d in steps:
            pts.append(pts[-1] + d * s)
        path = VGroup(*[Line(a, b, color=CRITICAL, stroke_width=8) for a, b in zip(pts, pts[1:])])
        count = MathTex(r"\#\{\text{walls of length }\ell\}\;\lesssim\;3^{\ell}", font_size=44, color=CRITICAL)
        count.move_to([PANEL_X, -0.4, 0])
        self.say("Entropy pushes back: how many different walls of length ell are there? "
                 "Draw one step by step: at each step, there are at most three ways to go on.",
                 FadeOut(VGroup(walls2)), Create(path, run_time=3), Write(count))
        forks = VGroup()
        tip, prev = pts[3], pts[3] - pts[2]
        for d in (prev, np.array([prev[1], -prev[0], 0]), np.array([-prev[1], prev[0], 0])):
            forks.add(Arrow(tip, tip + d / np.linalg.norm(d) * s * 0.9, buff=0, color=EXACT, stroke_width=4,
                            max_tip_length_to_length_ratio=0.3))
        self.say("Straight, left or right: never back. So at most about three to the power ell shapes.",
                 Create(forks))
        F = MathTex(r"\Delta F\;\approx\;\ell\,(", r"2J", r"-", r"T\ln 3", r")", font_size=54).move_to([PANEL_X, -1.9, 0])
        F[1].set_color(COLD)
        F[3].set_color(HOT)
        self.say("So each unit of wall costs two J of energy, and buys at most T log three of entropy.", Write(F),
                 speech="So each unit of wall costs two J of energy, and buys at most T times log three of entropy.")
        Tb = MathTex(r"T<\frac{2}{\ln 3}\approx 1.82\;\Rightarrow\;\text{order survives}", font_size=40,
                     color=EXACT).next_to(F, DOWN, buff=0.35)
        self.say("Below two over log three, about one point eight two, the cost wins. Large islands are "
                 "exponentially suppressed, and the order survives.", FadeIn(Tb))
        self.play(FadeOut(VGroup(g, path, forks, E, L1, count, F, Tb)), run_time=0.8)

        # what it means
        true = Tex(r"Peierls: a transition exists, with $T_c\ge 1.82$\\(the true value: $T_c\approx 2.27$)",
                   font_size=40, color=FG).shift(2.6 * UP)
        snaps = load("snapshots")
        i20 = int(np.argmin(np.abs(snaps["T"] - 2.0)))
        i25 = int(np.argmin(np.abs(snaps["T"] - 2.5)))
        a = lattice_image(snaps["frames"][i20], height=4.6)
        b = lattice_image(snaps["frames"][i25], height=4.6)
        pics = Group(a, b).arrange(RIGHT, buff=0.8).shift(0.6 * DOWN)
        la = Tex(r"$T=2.0$: small islands in a sea", font_size=30, color=MUTED).next_to(a, DOWN, buff=0.2)
        lb = Tex(r"$T=2.5$: no sea at all", font_size=30, color=MUTED).next_to(b, DOWN, buff=0.2)
        self.say("Peierls' bound is not sharp: the true critical temperature is higher. "
                 "But it proves that a phase transition exists.", FadeIn(true))
        self.say("And that's exactly what simulations show. Below T c, islands stay small, "
                 "and the sea keeps its colour. Above, there's no sea at all.",
                 FadeIn(a), FadeIn(la), FadeIn(b), FadeIn(lb))
        self.say("One dimension versus two: in a line, a wall is a point, and points are cheap. "
                 "In a plane, a wall is a line, and lines get expensive.")
        self.play(FadeOut(Group(a, b, la, lb, true)), FadeOut(self.chapter_tag), run_time=0.8)
