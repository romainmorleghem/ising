"""s02 · One dimension: Ising's thesis (1925). A wall costs 2J but can sit anywhere -> no order."""
from _common import Narrated, SpinGrid, load, lattice_image, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT
from manim import (VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, LaggedStart, Transform,
                   RoundedRectangle, Arrow, Indicate)

BROKEN = MEANFIELD


def card(year, text, col=EXACT):
    t = VGroup(Tex(year, font_size=44, color=col), Tex(text, font_size=30, color=FG)).arrange(DOWN, buff=0.15)
    box = RoundedRectangle(corner_radius=0.15, width=t.width + 0.6, height=t.height + 0.4, stroke_color=MUTED, stroke_width=2)
    return VGroup(box, t)


class OneDimension(Narrated):
    def construct(self):
        self.chapter("2 · One dimension")
        c1 = card("1920", "Wilhelm Lenz proposes the model")
        c2 = card("1925", "Ernst Ising solves it\\\\in one dimension")
        cards = VGroup(c1, c2).arrange(RIGHT, buff=1.2).shift(1.2 * UP)
        self.say("The model was proposed in 1920 by Wilhelm Lenz, who gave it to his student, "
                 "Ernst Ising, as a thesis problem.", FadeIn(c1, shift=0.2 * UP))
        self.say("Ising solved the simplest case: a single line of spins.", FadeIn(c2, shift=0.2 * UP))

        n = 14
        chain = SpinGrid(np.ones((1, n)), size=0.7).shift(1.3 * DOWN)
        self.say("At zero temperature, everyone agrees. Now let in a little heat. "
                 "What does it cost to break the order?",
                 FadeOut(cards, shift=0.3 * UP), LaggedStart(*[FadeIn(c) for c in chain], lag_ratio=0.05))

        # one wall
        k = 8
        flips = [chain.flip(0, j) for j in range(k, n)]
        self.play(LaggedStart(*flips, lag_ratio=0.05), run_time=1.2)
        wall = chain.edge((0, k - 1), (0, k), BROKEN, width=10)
        cost = MathTex(r"+2J", font_size=46, color=BROKEN).next_to(wall, UP, buff=0.55)
        self.say("Flip all the spins on one side, and you create a single wall between gold and blue. "
                 "It costs just two J, however long the chain.", Create(wall), FadeIn(cost))

        # the wall can sit anywhere
        ghosts = VGroup(*[chain.edge((0, j - 1), (0, j), BROKEN, width=4).set_opacity(0.45) for j in range(1, n)])
        npos = Tex(r"$N$ possible places", font_size=36, color=CRITICAL).next_to(chain, DOWN, buff=0.5)
        self.say("But that wall could sit between any two neighbours: in a chain of N spins, "
                 "that's about N different places.", LaggedStart(*[FadeIn(g) for g in ghosts], lag_ratio=0.06),
                 FadeIn(npos))
        F = MathTex(r"\Delta F", r"=", r"2J", r"-", r"T\ln N", font_size=60).move_to(2.0 * UP)
        F[2].set_color(COLD)
        F[4].set_color(HOT)
        self.say("Count the free energy: two J of energy, minus T log N of entropy.", Write(F),
                 speech="So the free energy of a wall is two J of energy, minus T times log N of entropy.")
        big = MathTex(r"N=10^{23}:\;\ln N\approx 53\;\Rightarrow\;\Delta F<0\text{ as soon as }T>0.04",
                      font_size=38, color=MUTED).next_to(F, DOWN, buff=0.4)
        self.say("For a real piece of material, N is huge, and the entropy wins at any temperature above zero. "
                 "Walls are free to appear.", FadeIn(big))
        self.play(FadeOut(VGroup(chain, wall, cost, ghosts, npos, F, big)), run_time=0.8)

        # space-time diagrams
        d = load("chain")
        cold = lattice_image(d["cold"], height=5.2).shift(0.2 * DOWN)
        tlab = VGroup(Arrow(UP, DOWN, color=MUTED, buff=0).scale(1.2), Tex("time", font_size=30, color=MUTED)).arrange(DOWN)
        tlab.next_to(cold, LEFT, buff=0.3)
        slab = Tex(r"360 spins, $T=0.7$", font_size=30, color=MUTED).next_to(cold, UP, buff=0.2)
        self.say("Here is a simulated chain of three hundred and sixty spins, with time running downwards. "
                 "It starts perfectly ordered, at a low temperature.", FadeIn(cold), FadeIn(tlab), FadeIn(slab))
        self.say("Walls appear in pairs, wander, and annihilate. The order never comes back.")
        warm = lattice_image(d["warm"], height=5.2).move_to(cold)
        slab2 = Tex(r"360 spins, $T=1.6$", font_size=30, color=MUTED).move_to(slab)
        self.say("Warmer, the domains are simply shorter. On average, the magnetisation is zero, "
                 "at every temperature.", FadeIn(warm), Transform(slab, slab2))
        self.play(FadeOut(cold), FadeOut(warm), FadeOut(VGroup(tlab, slab)), run_time=0.8)

        # Ising's conclusion
        ok = Tex(r"one dimension: no phase transition \;\checkmark", font_size=40, color=COLD)
        ko = Tex(r"any dimension: no phase transition \;\texttimes", font_size=40, color=BROKEN)
        concl = VGroup(ok, ko).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(0.5 * UP)
        self.say("Ising concluded, correctly, that his chain has no phase transition.", FadeIn(ok))
        self.say("Then, incorrectly, that the same would be true in any dimension.", FadeIn(ko))
        fate = Tex(r"Ising left research and became a teacher.\\He learned of his model's fame decades later.",
                   font_size=32, color=MUTED).next_to(concl, DOWN, buff=0.8)
        self.say("He left research, and became a school teacher. He only learned decades later "
                 "that his model had become famous.", FadeIn(fate))
        self.play(FadeOut(VGroup(concl, fate)), FadeOut(self.chapter_tag), run_time=0.8)
