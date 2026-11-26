"""s01 · The model: spins, neighbours, energy = length of the borders, Boltzmann weight,
energy vs entropy, and the Metropolis rule."""
from _common import Narrated, SpinGrid, Movie, TC, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN, DOWN_SPIN
from manim import (VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, Indicate, SurroundingRectangle,
                   LaggedStart, ReplacementTransform, Circumscribe, FadeTransform)

PANEL_X = 3.4          # centre of the right-hand panel
BROKEN = MEANFIELD     # colour of a broken bond / domain wall


def panel(*mobs, buff=0.45):
    return VGroup(*mobs).arrange(DOWN, buff=buff).move_to([PANEL_X, 0.2, 0])


class Model(Narrated):
    def construct(self):
        self.chapter("1 · The model")
        rng = np.random.default_rng(5)
        s = np.where(rng.random((8, 8)) < 0.5, 1, -1)
        grid = SpinGrid(s, size=0.66).move_to([-3.5, -0.2, 0])

        # --- spins ---------------------------------------------------------------------------
        self.say("Let's zoom in. Each little square holds a spin: an arrow that can point only up, or down.",
                 LaggedStart(*[FadeIn(c, scale=0.6) for c in grid], lag_ratio=0.02))
        sp = panel(MathTex(r"s_i=+1", font_size=54, color=UP_SPIN),
                   MathTex(r"s_i=-1", font_size=54, color=DOWN_SPIN))
        self.say("We write it as a number: s equals plus one for up, and minus one for down.", FadeIn(sp))

        # --- neighbours ------------------------------------------------------------------------
        c = (3, 4)
        others = VGroup(*[grid.cell(i, j) for (i, j) in grid.sq if (i, j) != c and (i, j) not in grid.neighbours(*c)])
        ring = SurroundingRectangle(grid.cell(*c), color=FG, buff=0.02, stroke_width=5)
        nb = VGroup(*[SurroundingRectangle(grid.cell(*n), color=CRITICAL, buff=0.02, stroke_width=4)
                      for n in grid.neighbours(*c)])
        self.say("Each spin feels only its four nearest neighbours: left, right, above, and below.",
                 FadeOut(sp), others.animate.set_opacity(0.25), Create(ring), Create(nb))

        # --- pair energy -------------------------------------------------------------------------
        def pair(a, b, e, col):
            g = SpinGrid(np.array([[a, b]]), size=0.66)
            return VGroup(g, MathTex(e, font_size=46, color=col).next_to(g, RIGHT, buff=0.5))
        pairs = panel(pair(1, 1, r"-J", COLD), pair(-1, -1, r"-J", COLD), pair(1, -1, r"+J", HOT), buff=0.5)
        self.say("Between two neighbours, the rule is simple. If they agree, their bond has energy minus J. "
                 "If they disagree, plus J.", LaggedStart(*[FadeIn(p) for p in pairs], lag_ratio=0.4))
        self.say("Low energy is favoured, so neighbours like to agree.", Indicate(pairs[0][1]), Indicate(pairs[1][1]))
        self.play(others.animate.set_opacity(1), FadeOut(VGroup(ring, nb)), run_time=0.8)

        # --- total energy = borders ----------------------------------------------------------------
        H = MathTex(r"H=-J\sum_{\langle i,j\rangle} s_i\,s_j", font_size=50, color=FG).move_to([PANEL_X, 2.0, 0])
        self.say("Add up all the bonds, and you get the energy of the whole grid.", FadeOut(pairs), Write(H),
                 speech="Add up all the bonds, and you get the energy of the whole grid: H equals minus J, "
                        "times the sum over neighbouring pairs, of s i times s j.")
        walls = grid.borders(BROKEN, width=7)
        H2 = MathTex(r"H=H_{\min}+2J\times\ell", font_size=50, color=FG).next_to(H, DOWN, buff=0.6)
        ell = Tex(r"$\ell$ = total length of the borders", font_size=34, color=BROKEN).next_to(H2, DOWN, buff=0.3)
        cnt = MathTex(rf"\text{{here: }}\ell={len(walls)}", font_size=40, color=MUTED).next_to(ell, DOWN, buff=0.35)
        self.say("There's a nicer way to see it. Every border between gold and blue costs energy. "
                 "The energy is just the total length of the borders.",
                 LaggedStart(*[Create(w) for w in walls], lag_ratio=0.03), Write(H2), FadeIn(ell))
        self.say(f"Here, {len(walls)} units of border.", FadeIn(cnt))

        # --- ground states -------------------------------------------------------------------------
        g_up = SpinGrid(np.ones((4, 4)), size=0.42)
        g_dn = SpinGrid(-np.ones((4, 4)), size=0.42)
        gs = VGroup(g_up, g_dn).arrange(RIGHT, buff=0.6)
        gl = Tex(r"no border: lowest energy", font_size=34, color=MUTED).next_to(gs, DOWN, buff=0.3)
        ground = VGroup(gs, gl).move_to([PANEL_X, -1.9, 0])
        self.say("So the lowest energy is reached when everyone agrees: all gold, or all blue. "
                 "If energy were all that mattered, the story would end here.",
                 FadeOut(VGroup(cnt, ell)), H2.animate.set_opacity(0.4), FadeIn(ground))
        self.play(FadeOut(VGroup(H, H2, ground, walls)), run_time=0.8)

        # --- temperature: Boltzmann ------------------------------------------------------------------
        boltz = MathTex(r"P(\text{grid})\;\propto\;e^{-H/T}", font_size=58, color=EXACT)
        units = Tex(r"(temperature in units of $J$)", font_size=30, color=MUTED)
        lowT = Tex(r"low $T$: costly borders are exponentially rare", font_size=32, color=COLD)
        highT = Tex(r"high $T$: almost anything goes", font_size=32, color=HOT)
        bp = panel(boltz, units, VGroup(lowT, highT).arrange(DOWN, buff=0.25, aligned_edge=LEFT), buff=0.4)
        self.say("But there is heat. At temperature T, each grid appears with a probability proportional "
                 "to e, to the minus H over T.", Write(boltz))
        self.say("We measure temperature in units of J. That's where the two point two seven came from.",
                 FadeIn(units))
        self.say("At low temperature, grids with long borders are exponentially rare. "
                 "At high temperature, almost anything goes.", FadeIn(lowT), FadeIn(highT, shift=0.1 * DOWN))
        self.play(FadeOut(bp), run_time=0.8)

        # --- energy vs entropy --------------------------------------------------------------------------
        ordered = VGroup(Tex("ordered grids", font_size=34, color=MUTED), MathTex("2", font_size=60, color=FG)).arrange(DOWN)
        messy = VGroup(Tex("messy grids", font_size=34, color=MUTED),
                       MathTex(r"\approx 2^{N}", font_size=60, color=FG)).arrange(DOWN)
        count = VGroup(ordered, messy).arrange(RIGHT, buff=1.2)
        n64 = MathTex(r"N=64:\;\;2^{64}\approx 1.8\times10^{19}", font_size=38, color=MUTED)
        tug = MathTex(r"F", r"=", r"E", r"-", r"T", r"S", font_size=62)
        tug[2].set_color(COLD); tug[5].set_color(HOT); tug[4].set_color(EXACT)
        tl = VGroup(Tex("energy: wants order", font_size=30, color=COLD),
                    Tex("entropy: wants disorder", font_size=30, color=HOT)).arrange(DOWN, buff=0.2)
        ep = panel(count, n64, tug, tl, buff=0.42)
        self.say("And disorder has numbers on its side. There are only two perfectly ordered grids, "
                 "but about two to the power N messy ones, where N is the number of spins.", FadeIn(count))
        self.say("Even for this tiny grid of sixty-four spins, that's eighteen billion billion.", FadeIn(n64))
        self.say("Temperature referees a tug of war: energy wants order, entropy wants disorder. "
                 "The winner is whoever lowers the free energy, F equals E minus T S.",
                 Write(tug), FadeIn(tl))
        self.play(FadeOut(ep), run_time=0.8)

        # --- Metropolis --------------------------------------------------------------------------------
        rules = VGroup(
            Tex(r"1. pick a spin, propose to flip it", font_size=32, color=FG),
            Tex(r"2. if $\Delta E\le 0$: accept", font_size=32, color=COLD),
            Tex(r"3. if $\Delta E>0$: accept with probability $e^{-\Delta E/T}$", font_size=32, color=HOT),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rules.scale_to_fit_width(min(rules.width, 6.0))
        title = Tex("The Metropolis rule (1953)", font_size=40, color=EXACT)
        rp = VGroup(title, rules).arrange(DOWN, buff=0.5).move_to([PANEL_X, 1.4, 0])
        interior = [(i, j) for i in range(1, 7) for j in range(1, 7)]
        down_c = next(c for c in interior if grid.delta_E(*c) < 0)
        up_c = next(c for c in interior if grid.delta_E(*c) == 4 and abs(c[0] - down_c[0]) + abs(c[1] - down_c[1]) > 1)

        ring = SurroundingRectangle(grid.cell(*down_c), color=FG, buff=0.03, stroke_width=6)
        self.say("To simulate it, we use one rule, due to Metropolis and his colleagues. "
                 "Pick a spin at random, and propose to flip it.", FadeIn(title), FadeIn(rules[0]), Create(ring))
        dE1 = MathTex(rf"\Delta E={grid.delta_E(*down_c)}J", font_size=44, color=COLD).move_to([PANEL_X, -1.3, 0])
        self.say("If the flip lowers the energy, accept it.", FadeIn(rules[1]), FadeIn(dE1))
        self.play(grid.flip(*down_c), run_time=0.8)
        self.wait(0.3)

        ring2 = SurroundingRectangle(grid.cell(*up_c), color=FG, buff=0.03, stroke_width=6)
        dE2 = MathTex(r"\Delta E=+4J", font_size=44, color=HOT).move_to([PANEL_X, -1.3, 0])
        p = float(np.exp(-4 / TC))
        prob = MathTex(rf"e^{{-4/2.27}}\approx {p:.2f}", font_size=40, color=FG).next_to(dE2, DOWN, buff=0.3)
        draw = MathTex(r"\text{random number } 0.11<%.2f\;\Rightarrow\;\text{flip}" % p, font_size=34,
                       color=MUTED).next_to(prob, DOWN, buff=0.3)
        self.say("If it raises the energy, accept it anyway, but only with probability e, to the minus "
                 "the energy cost, over T.",
                 ReplacementTransform(ring, ring2), FadeIn(rules[2]), FadeTransform(dE1, dE2))
        self.say(f"At two point two seven, a cost of four J is accepted about {round(p * 100)} percent of the time. "
                 "Here, we roll the dice, and it goes through.", FadeIn(prob), FadeIn(draw))
        self.play(grid.flip(*up_c), run_time=0.8)

        # --- zoom out to the big lattice -----------------------------------------------------------------
        mv = Movie("cooling")
        big = mv.image("tc", len(mv["tc"][0]) - 1, height=6.8).shift(0.2 * DOWN)
        self.say("Repeat this billions of times, and the grid settles into exactly the right statistics. "
                 "That is how every simulation in this video is made.",
                 FadeOut(VGroup(rp, ring2, dE2, prob, draw)), FadeOut(grid, scale=0.3), FadeIn(big, scale=1.6))
        self.say("That's the whole model: one arrow per site, one rule between neighbours. "
                 "Now, what does it actually do?")
        self.play(FadeOut(big), FadeOut(self.chapter_tag), run_time=1.0)
