"""s05 · Onsager (1944) and Yang (1952): exact T_c, exact m(T) with exponent 1/8, specific heat peak."""
from _common import Narrated, load, axes, TC, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN
from manim import (VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, Dot, DashedLine, LaggedStart,
                   Indicate, Line)
from s04_mean_field import mf_solution


def m_exact(T):
    return (1 - np.sinh(2 / T) ** -4) ** 0.125 if T < TC else 0.0


def key(color, text, dot=False):
    mark = Dot(radius=0.08, color=color) if dot else Line(LEFT * 0.3, RIGHT * 0.3, color=color, stroke_width=5)
    return VGroup(mark, Tex(text, font_size=28, color=FG)).arrange(RIGHT, buff=0.15)


class Onsager(Narrated):
    def construct(self):
        self.chapter("5 · The exact solution")
        self.say("In 1944, Lars Onsager did what seemed impossible. He solved the two-dimensional model "
                 "exactly, with pen and paper.")
        tc = MathTex(r"T_c=\frac{2}{\ln\!\left(1+\sqrt{2}\right)}\approx 2.2692", font_size=72, color=EXACT).shift(0.6 * UP)
        self.say("The critical temperature has a closed form: two, over the logarithm of one plus root two.",
                 Write(tc), speech="The critical temperature has a closed form: two, over the logarithm of "
                                   "one plus the square root of two. Two point two six nine.")
        note = Tex(r"(the 2.27 of the opening)", font_size=34, color=MUTED).next_to(tc, DOWN, buff=0.4)
        self.say("That's the number we saw at the very beginning.", FadeIn(note))
        self.play(FadeOut(note), tc.animate.scale(0.55).to_corner(UP + RIGHT, buff=0.5), run_time=0.8)

        mform = MathTex(r"m=\Big(1-\sinh^{-4}\tfrac{2}{T}\Big)^{1/8}", font_size=60, color=EXACT)
        story = Tex(r"Onsager, 1949: written on a blackboard, no proof\\Chen Ning Yang, 1952: the proof",
                    font_size=32, color=MUTED).next_to(mform, DOWN, buff=0.45)
        self.say("His method was so intricate that others took years to follow it. In 1949, he simply "
                 "wrote the magnetisation on a blackboard at a conference, without proof. "
                 "Chen Ning Yang proved it in 1952.", Write(mform), FadeIn(story))
        self.play(FadeOut(story), mform.animate.scale(0.6).next_to(tc, DOWN, buff=0.35, aligned_edge=RIGHT), run_time=0.8)

        # m(T): exact vs simulation vs mean field
        th = load("thermo")
        ax, labs = axes([0, 5, 1], [0, 1.05, 0.25], x_length=8.4, y_length=4.8, x_label="T", y_label=r"|m|",
                        decimals=2)
        ax.move_to([-1.6, -0.6, 0])
        ex = ax.plot(m_exact, x_range=[0.3, TC - 1e-4, 0.005], color=EXACT, stroke_width=5)
        ex0 = Line(ax.c2p(TC, 0), ax.c2p(5, 0), color=EXACT, stroke_width=5)
        sim = VGroup(*[Dot(ax.c2p(T, m), radius=0.06, color=UP_SPIN) for T, m in zip(th["T"], th["m128"])])
        mf = ax.plot(lambda T: mf_solution(T), x_range=[0.3, 4.0, 0.01], color=MEANFIELD, stroke_width=4)
        mf0 = Line(ax.c2p(4, 0), ax.c2p(5, 0), color=MEANFIELD, stroke_width=4)
        keys = VGroup(key(EXACT, "Onsager--Yang (exact)"), key(UP_SPIN, r"simulation, $128\times128$", dot=True),
                      key(MEANFIELD, "mean field")).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        keys.move_to(ax.c2p(4.1, 0.8))
        self.say("Here it is, the exact magnetisation, as a function of temperature.",
                 Create(ax), FadeIn(labs), Create(ex), Create(ex0), FadeIn(keys[0]))
        self.say("And here are our simulations. They sit right on Onsager's curve.",
                 LaggedStart(*[FadeIn(d, scale=0.5) for d in sim], lag_ratio=0.05), FadeIn(keys[1]))
        self.say("Mean field, in comparison, is way off.", Create(mf), Create(mf0), FadeIn(keys[2]))
        tcl = DashedLine(ax.c2p(TC, 0), ax.c2p(TC, 1.0), color=CRITICAL)
        exps = VGroup(MathTex(r"\text{exact: }m\propto (T_c-T)^{1/8}", font_size=40, color=EXACT),
                      MathTex(r"\text{mean field: }m\propto (T_c-T)^{1/2}", font_size=40, color=MEANFIELD)
                      ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(ax.c2p(1.15, 0.4))
        self.say("Look at how it vanishes: near T c, like T c minus T, to the power one eighth. "
                 "Mean field says one half. One eighth is so small that the curve drops almost vertically.",
                 Create(tcl), FadeIn(exps))
        self.say("That one eighth is our first critical exponent. Remember it.", Indicate(exps[0]))
        self.play(FadeOut(VGroup(ax, labs, ex, ex0, sim, mf, mf0, keys, tcl, exps)), run_time=0.8)

        # specific heat
        ax2, labs2 = axes([1.5, 3.5, 0.5], [0, 3.0, 1], x_length=8.4, y_length=4.8, x_label="T",
                          y_label=r"C/N", decimals=1)
        ax2.move_to([-1.6, -0.6, 0])
        cols = {32: "#8C86B8", 64: "#E98AA8", 128: UP_SPIN}
        curves, ks = VGroup(), VGroup()
        for L, c in cols.items():
            pts = [ax2.c2p(T, C) for T, C in zip(th["T"], th[f"c{L}"]) if 1.5 <= T <= 3.5]
            from manim import VMobject
            curves.add(VMobject(stroke_color=c, stroke_width=4).set_points_smoothly(pts))
            ks.add(key(c, rf"$L={L}$"))
        ks.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to(ax2.c2p(3.15, 2.4))
        tcl2 = DashedLine(ax2.c2p(TC, 0), ax2.c2p(TC, 3.0), color=CRITICAL)
        self.say("Another clue: the specific heat, how much energy it takes to warm the system up. "
                 "It has a peak at T c.", Create(ax2), FadeIn(labs2), Create(tcl2), Create(curves[0]), FadeIn(ks[0]))
        self.say("And the bigger the system, the higher the peak. For an infinite system, Onsager showed "
                 "that it diverges, logarithmically.", Create(curves[1]), FadeIn(ks[1]), Create(curves[2]), FadeIn(ks[2]))
        self.say("So something singular happens at T c. What does the system actually look like there?")
        self.play(FadeOut(VGroup(ax2, labs2, curves, ks, tcl2, tc, mform)), FadeOut(self.chapter_tag), run_time=0.8)
