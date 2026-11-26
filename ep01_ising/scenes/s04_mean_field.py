"""s04 · Mean field (Weiss): m = tanh(4m/T), the bowl that splits in two, right picture / wrong numbers."""
from _common import Narrated, SpinGrid, load, axes, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN, GRID
from manim import (VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, ValueTracker, always_redraw,
                   Dot, DecimalNumber, Square, ReplacementTransform, DashedLine, linear, smooth)

PANEL_X = 3.6


def mf_solution(T):
    """Positive solution of m = tanh(4m/T) (0 if T >= 4)."""
    if T >= 4:
        return 0.0
    m = 1.0
    for _ in range(500):
        m = np.tanh(4 * m / T)
    return m


def rate(m):
    """I(m) = ln 2 - s(m): the rate function of fair coin flips (Rare Events, ep. 1)."""
    return float(sum(x * np.log(2 * x) for x in ((1 + m) / 2, (1 - m) / 2) if x > 0))


class MeanField(Narrated):
    def construct(self):
        self.chapter("4 · Mean field")
        self.say("Before anyone could solve the model, physicists had a shortcut, invented by Pierre Weiss "
                 "for real magnets, as early as 1907: mean field theory.")

        # replace neighbours by their average
        g = SpinGrid(np.array([[1, -1, 1], [1, 1, -1], [-1, 1, 1]]), size=0.9).move_to([-3.6, 0.3, 0])
        self.play(FadeIn(g), run_time=0.8)
        avg = VGroup()
        for (i, j) in g.neighbours(1, 1):
            sq = Square(0.9, stroke_color=GRID, stroke_width=3, fill_color=MUTED, fill_opacity=1).move_to(g.sq[i, j])
            avg.add(VGroup(sq, MathTex("m", font_size=40, color=FG).move_to(sq)))
        self.say("The idea: a spin doesn't see its four neighbours individually. "
                 "Replace each of them by the average spin, m.", *[ReplacementTransform(g.cell(*n), a)
                                                                  for n, a in zip(g.neighbours(1, 1), avg)])
        eq = MathTex(r"m=\tanh\!\left(\frac{4m}{T}\right)", font_size=58, color=EXACT).move_to([PANEL_X, 1.5, 0])
        self.say("Then the centre spin feels a pull of four m. Its own average must be m again. "
                 "That gives one self-consistent equation.", Write(eq),
                 speech="Then the centre spin feels a pull of four m, and its own average must be m again. "
                        "That gives one self-consistent equation: m equals the hyperbolic tangent of four m over T.")
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob not in (eq, self.chapter_tag)],
                  eq.animate.move_to([PANEL_X, 2.6, 0]).scale(0.85), run_time=0.8)

        # graphical solution
        ax, labs = axes([-1.2, 1.2, 0.5], [-1.2, 1.2, 0.5], x_length=6.2, y_length=6.2, x_label="m")
        ax.move_to([-3.0, -0.3, 0])
        T = ValueTracker(6.0)
        diag = ax.plot(lambda x: x, x_range=[-1.2, 1.2], color=MUTED, stroke_width=3)
        curve = always_redraw(lambda: ax.plot(lambda x: np.tanh(4 * x / T.get_value()), x_range=[-1.2, 1.2],
                                              color=MEANFIELD, stroke_width=4))
        dots = always_redraw(lambda: VGroup(*[Dot(ax.c2p(m, m), radius=0.09, color=EXACT)
                                              for m in sorted({0.0, mf_solution(T.get_value()), -mf_solution(T.get_value())})]))
        tl = always_redraw(lambda: VGroup(MathTex("T=", font_size=48, color=FG),
                                          DecimalNumber(T.get_value(), num_decimal_places=2, font_size=48, color=FG))
                           .arrange(RIGHT, buff=0.12).move_to([PANEL_X, 1.2, 0]))
        yl = MathTex(r"y=m", font_size=32, color=MUTED).move_to(ax.c2p(0.95, 1.18))
        tn = MathTex(r"y=\tanh(4m/T)", font_size=32, color=MEANFIELD).move_to(ax.c2p(-0.55, 1.0))
        self.say("Solve it graphically: the solutions are where the curve crosses the diagonal.",
                 Create(ax), FadeIn(labs), Create(diag), Create(curve), FadeIn(yl), FadeIn(tn), FadeIn(tl), FadeIn(dots))
        self.say("When it's hot, the only crossing is m equals zero: no magnetisation.")
        d = self.voice("Cool down. When T drops below four, the curve gets steeper than the diagonal at the "
                       "centre, and two new solutions split off: plus m and minus m. Spontaneous magnetisation.")
        self.play(T.animate.set_value(2.0), run_time=d + 0.3, rate_func=smooth)
        mf = MathTex(r"T_c^{\text{mean field}}=4", font_size=44, color=MEANFIELD).move_to([PANEL_X, 0.0, 0])
        self.say("Mean field predicts a phase transition, at T equals four.", FadeIn(mf))
        self.play(FadeOut(VGroup(ax, labs, diag, curve, dots, yl, tn, tl, eq, mf)), run_time=0.8)

        # free-energy landscape
        ax2, labs2 = axes([-1, 1, 0.5], [-0.8, 0.5, 0.4], x_length=6.4, y_length=4.6, x_label="m",
                          y_label=r"f(m)")
        ax2.move_to([-2.9, -0.4, 0])
        labs2.shift(0)
        T2 = ValueTracker(6.0)

        def fcurve():
            t = T2.get_value()
            f = lambda m: -2 * m * m + t * rate(m)
            xs = np.linspace(0, 0.999, 500)
            mmax = max(x for x in xs if f(x) <= 0.5)          # stay inside the axes
            return ax2.plot(f, x_range=[-mmax, mmax, 0.005],
                            color=CRITICAL, stroke_width=4)
        fl = always_redraw(fcurve)
        fe = MathTex(r"f(m)=", r"-2m^2", r"+", r"T\,I(m)", font_size=48).move_to([PANEL_X, 2.3, 0])
        fe[1].set_color(COLD)
        fe[3].set_color(HOT)
        notes = VGroup(Tex(r"energy: pulls to the edges", font_size=30, color=COLD),
                       Tex(r"entropy: pulls to the middle", font_size=30, color=HOT)).arrange(DOWN, buff=0.2).next_to(fe, DOWN, buff=0.35)
        tl2 = always_redraw(lambda: VGroup(MathTex("T=", font_size=44, color=FG),
                                           DecimalNumber(T2.get_value(), num_decimal_places=2, font_size=44, color=FG))
                            .arrange(RIGHT, buff=0.12).move_to([PANEL_X, -0.6, 0]))
        self.say("The same story, as a landscape: the free energy per spin, as a function of m. "
                 "Energy pulls towards the edges, entropy towards the middle.",
                 Create(ax2), FadeIn(labs2), Create(fl), Write(fe), FadeIn(notes), FadeIn(tl2))
        d = self.voice("Hot, it's a single bowl, centred on zero. Cool down past four, and the bowl splits "
                       "in two: a double well, one valley for each colour.")
        self.play(T2.animate.set_value(2.6), run_time=d + 0.3, rate_func=smooth)
        re = Tex(r"$I(m)$: the rate function of coin flips (\emph{Rare Events}, ep.\,1)", font_size=28,
                 color=MUTED)
        re.scale_to_fit_width(min(re.width, 6.0)).move_to([PANEL_X, -1.6, 0])
        self.say("If you've watched Rare Events, you know the entropy part: I of m is exactly the rate "
                 "function of coin flips, the bowl of that episode.", FadeIn(re))
        self.play(FadeOut(VGroup(ax2, labs2, fl, fe, notes, tl2, re)), run_time=0.8)

        # the real thing, measured
        pm = load("pm")
        ax3, labs3 = axes([-1, 1, 0.5], [0, 0.03, 0.01], x_length=8.5, y_length=4.6, x_label="m",
                          y_label=r"-\tfrac{1}{N}\ln P(m)", decimals=2)
        ax3.move_to([-0.6, -0.4, 0])
        cols = ["#5A6B85", "#8C86B8", CRITICAL, "#E98AA8", UP_SPIN]
        curves, keys = VGroup(), VGroup()
        for T_, y, c in zip(pm["T"], pm["y"], cols):
            ok = np.isfinite(y) & (y <= 0.03)
            x = pm["x"]
            # split into contiguous runs so gaps are not bridged
            runs, cur = [], []
            for xi, yi, k in zip(x, y, ok):
                if k:
                    cur.append(ax3.c2p(xi, yi))
                elif cur:
                    runs.append(cur)
                    cur = []
            if cur:
                runs.append(cur)
            grp = VGroup()
            for r in runs:
                if len(r) > 1:
                    from manim import VMobject
                    grp.add(VMobject(stroke_color=c, stroke_width=4).set_points_smoothly(r))
            curves.add(grp)
            keys.add(VGroup(Line_(c), MathTex(("T_c" if abs(T_ - 2.269) < 0.01 else f"T={T_:.1f}"), font_size=28, color=FG)).arrange(RIGHT, buff=0.12))
        keys.arrange(DOWN, buff=0.18, aligned_edge=LEFT).next_to(ax3, RIGHT, buff=0.3)
        title = Tex(r"measured in\\simulations\\($16\times16$)", font_size=30, color=MUTED).next_to(keys, UP, buff=0.4)
        self.say("And here is the real thing, measured in simulations: the probability of each magnetisation. "
                 "The bowl does split in two.",
                 Create(ax3), FadeIn(labs3), FadeIn(title), FadeIn(keys),
                 *[Create(c) for c in curves])
        self.wait(2.5)
        self.play(FadeOut(VGroup(ax3, labs3, title, keys, curves)), run_time=0.8)

        verdict = VGroup(
            Tex(r"right picture,", font_size=54, color=COLD),
            Tex(r"wrong numbers", font_size=54, color=MEANFIELD),
            MathTex(r"T_c^{\text{mean field}}=4\qquad\text{vs}\qquad T_c\approx 2.27", font_size=44, color=FG),
        ).arrange(DOWN, buff=0.4)
        self.say("Mean field gets the picture right, but the numbers wrong. It predicts four. "
                 "The true critical temperature is two point two seven.", FadeIn(verdict[0]), FadeIn(verdict[1]), Write(verdict[2]))
        self.say("By replacing neighbours with an average, it ignores fluctuations, and fluctuations "
                 "are exactly what fights order. To get the real numbers, someone had to solve the model.")
        self.play(FadeOut(verdict), FadeOut(self.chapter_tag), run_time=0.8)


def Line_(c):
    from manim import Line
    return Line(LEFT * 0.3, RIGHT * 0.3, color=c, stroke_width=5)
