"""s06 · At the critical point: no typical size, block spins (Kadanoff), renormalisation (Wilson), clusters."""
from _common import (Narrated, SpinGrid, load, lattice_image, rgb_image, block2, unpack, axes, TC, np,
                     LEFT, RIGHT, UP, DOWN)
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN, DOWN_SPIN
from manim import (Group, VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, LaggedStart, Transform,
                   SurroundingRectangle, Dot, Line, DashedLine, FadeTransform, ReplacementTransform)
from matplotlib.colors import hsv_to_rgb


class CriticalPoint(Narrated):
    def construct(self):
        self.chapter("6 · The critical point")
        snaps = load("snapshots")
        idx = {T: int(np.argmin(np.abs(snaps["T"] - T))) for T in (2.0, TC, 2.5)}
        imgs = Group(*[lattice_image(snaps["frames"][idx[T]], height=3.9) for T in (2.0, TC, 2.5)]).arrange(RIGHT, buff=0.45)
        imgs.shift(0.2 * DOWN)
        labs = VGroup(*[Tex(t, font_size=30, color=c).next_to(im, DOWN, buff=0.2) for t, c, im in
                        zip([r"$T=2.0$", r"$T=T_c$", r"$T=2.5$"], [COLD, CRITICAL, HOT], imgs)])
        self.say("Let's compare. Below T c, the islands are small. Above T c, the patches of noise are small too.",
                 FadeIn(imgs[0]), FadeIn(imgs[2]), FadeIn(labs[0]), FadeIn(labs[2]))
        xi = MathTex(r"\xi\;\propto\;|T-T_c|^{-1}", font_size=50, color=EXACT).next_to(imgs, UP, buff=0.45)
        self.say("That typical size has a name: the correlation length. As we approach T c, it grows, "
                 "like one over the distance to T c.", Write(xi))
        self.say("So at T c itself, there is no typical size at all. Islands of every size, nested inside "
                 "each other, all the way up to the size of the system.", FadeIn(imgs[1]), FadeIn(labs[1]))
        self.play(FadeOut(Group(imgs, labs, xi)), run_time=0.8)

        # Kadanoff's block spins: small demo
        rng = np.random.default_rng(2)
        s = np.where(rng.random((8, 8)) < 0.55, 1, -1)
        g = SpinGrid(s, size=0.55).move_to([-3.3, -0.2, 0])
        blocks = VGroup(*[SurroundingRectangle(VGroup(g.cell(2 * a, 2 * b), g.cell(2 * a + 1, 2 * b + 1)),
                                               buff=0, color=FG, stroke_width=4) for a in range(4) for b in range(4)])
        sb = block2(s.astype(np.int8), np.random.default_rng(0))
        gb = SpinGrid(sb, size=1.1).move_to([3.3, -0.2, 0])
        arrow = MathTex(r"\longrightarrow", font_size=80, color=MUTED)
        rule = Tex(r"each $2\times2$ block votes:\\majority wins", font_size=32, color=MUTED).next_to(arrow, UP, buff=0.3)
        self.say("Here is a way to see it, due to Leo Kadanoff, in 1966. Group the spins into blocks of four.",
                 FadeIn(g), Create(blocks))
        self.say("Each block votes, and becomes a single spin: majority wins, with a coin toss for ties. "
                 "We get a smaller lattice: the same system, seen from twice as far.",
                 FadeIn(arrow), FadeIn(rule), FadeIn(gb, shift=0.3 * LEFT))
        self.play(FadeOut(VGroup(g, blocks, arrow, rule, gb)), run_time=0.8)

        # block-spin flow on three big lattices
        bl = load("blocks")
        W = 128
        rng = np.random.default_rng(1)
        states = [unpack(f) for f in bl["frames"]]
        cols = [COLD, CRITICAL, HOT]
        names = [r"$T=2.20$", r"$T=T_c$", r"$T=2.35$"]
        pics = Group(*[lattice_image(st[:W, :W], height=3.9) for st in states]).arrange(RIGHT, buff=0.45).shift(0.3 * DOWN)
        tags = VGroup(*[Tex(n, font_size=30, color=c).next_to(p, DOWN, buff=0.2) for n, c, p in zip(names, cols, pics)])
        zoom = Tex(r"zoom-out $\times1$", font_size=34, color=FG).next_to(pics, UP, buff=0.35)
        self.say("Now do it to three large simulations: just below T c, at T c, and just above. "
                 "At first, they look rather alike.", FadeIn(pics), FadeIn(tags), FadeIn(zoom))
        lines = ["One step.", "Two steps.", "Three.", "Four."]
        for k, line in enumerate(lines):
            states = [block2(st, rng) for st in states]
            new = Group(*[lattice_image(st[:W, :W], height=3.9).move_to(p) for st, p in zip(states, pics)])
            z2 = Tex(rf"zoom-out $\times{2 ** (k + 1)}$", font_size=34, color=FG).move_to(zoom)
            self.say(line, *[FadeTransform(p, q) for p, q in zip(pics, new)], FadeTransform(zoom, z2), run_time=0.8)
            pics, zoom = new, z2
        self.say("Below T c, the picture flows to a single colour. Above, to pure noise. "
                 "At T c, nothing changes: zooming out gives back the same statistics.")
        self.say("The critical point is a fixed point of zooming out. Kenneth Wilson turned this idea into "
                 "a precise theory, the renormalisation group, and won the Nobel prize for it in 1982.")
        self.play(FadeOut(Group(pics, tags, zoom)), run_time=0.8)

        # clusters
        cl = load("clusters")
        labels = cl["labels"]
        n = labels.max() + 1
        r = np.random.default_rng(7)
        hsv = np.stack([r.random(n), r.uniform(.45, .85, n), r.uniform(.6, 1, n)], 1)
        sizes = np.bincount(labels.ravel(), minlength=n)
        hsv[sizes < 30, 1:] = [.15, .22]
        for k, h in enumerate([.11, .58, .95, .33]):
            hsv[k] = [h, .8, 1]
        rgb = (hsv_to_rgb(hsv) * 255).astype(np.uint8)
        base = np.full((1024, 1024, 3), 30, np.uint8)
        stages = []
        for top in (1, 4, 40, n):
            img = rgb[labels].copy()
            img[labels >= top] = base[labels >= top]
            stages.append(img)
        pic = rgb_image(stages[0], height=6.4).shift(2.8 * LEFT + 0.2 * DOWN)
        self.say("One more way to look at T c. Group aligned neighbours into clusters, the way the fastest simulation algorithms do, "
                 "and give each cluster its own colour. Here is the largest one.", FadeIn(pic))
        for k, txt in ((1, "The next three."), (2, "The next thirty-six.")):
            nxt = rgb_image(stages[k], height=6.4).move_to(pic)
            self.say(txt, FadeTransform(pic, nxt), run_time=1.0)
            pic = nxt
        nxt = rgb_image(stages[3], height=6.4).move_to(pic)
        self.say("And all the others. Clusters of every size, from single spins to one that spans the whole system.",
                 FadeTransform(pic, nxt), run_time=1.5)
        pic = nxt

        ax, labs2 = axes([0, 6, 1], [-12, 0, 2], x_length=5.0, y_length=4.4, x_label=r"\log_{10} s",
                         y_label=r"\log_{10} n(s)", decimals=0)
        ax.move_to([3.9, -0.3, 0])
        b, h = cl["bins"], cl["density"]
        xs = np.log10(np.sqrt(b[:-1] * np.maximum(b[1:] - 1, b[:-1])))
        ok = h > 0
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.05, color=UP_SPIN) for x, y in zip(xs[ok], np.log10(h[ok]))
                        if -12 <= y <= 0 and x <= 6])
        tau = 31 / 15
        y0 = np.log10(h[ok][2]) + tau * xs[ok][2]
        fit = Line(ax.c2p(0, y0), ax.c2p(min(6, (y0 + 12) / tau), max(-12, y0 - 6 * tau)), color=CRITICAL, stroke_width=3)
        law = MathTex(r"n(s)\propto s^{-31/15}", font_size=38, color=CRITICAL).next_to(ax, UP, buff=0.2)
        self.say("Count them by size: the number of clusters of size s falls as a power law, a straight line "
                 "on a log-log plot. A power law has no scale: that is what scale-free means.",
                 Create(ax), FadeIn(labs2), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.03), Create(fit), FadeIn(law),
                 speech="Count them by size: the number of clusters of size s falls as a power law, a straight line "
                        "on a log-log plot. A power law has no scale. That is what scale-free means.")
        self.play(FadeOut(Group(pic, ax, labs2, dots, fit, law)), FadeOut(self.chapter_tag), run_time=0.8)
