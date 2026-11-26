# Episode 1 — The Ising model: the key results (≈ 20 min)

Audience: no background (same as Rare Events). Voice-over `af_heart`, no captions.
Colours: gold = spin up, blue = spin down (the coins of Rare Events).

| Seq | Title | Content | Key visual (simulation) |
|-----|-------|---------|-------------------------|
| s00 | Cold open | A lattice swept through temperature: it melts, it freezes, and in between, strange patterns. *How do magnets that only talk to their neighbours decide together?* | slow cooling 1024² |
| s01 | The model | Spins, energy H, Boltzmann weight; temperature arbitrates energy vs entropy; Metropolis in one sentence | live lattice |
| s02 | 1D: Ising gets it wrong (1925) | One domain wall costs 2J but can sit anywhere: disorder always wins. Ising wrongly concludes: no transition in any dimension | 1D chain as space-time diagram |
| s03 | 2D: Peierls fixes it (1936) | Cost of a wall ∝ its length vs number of walls ~ 3^L: order survives at low T (counting, as in Rare Events) | quench / shrinking islands |
| s04 | Mean field (Weiss) | m = tanh(m T_c/T) solved graphically; the bowl of Rare Events splits into a double well. Right picture, wrong numbers | −(1/N) ln P(m) measured |
| s05 | Onsager (1944) & Yang (1952) | Exact T_c = 2/ln(1+√2) ≈ 2.269; m ~ (T_c − T)^{1/8} vs mean field's 1/2; specific-heat peak | m(T): simulation vs exact vs mean field |
| s06 | At the critical point | No typical size: zoom / block spins look the same; clusters of every size | block-spin flow (3 rows), coloured clusters |
| s07 | Universality | Liquid–gas critical point, alloys: same exponents. Critical opalescence. 3D Ising still unsolved | structure factor glow |
| s08 | Legacy & recap | Hopfield (Nobel 2024): memories are energy minima; recap table | Hopfield reconstruction |

Advanced topics kept for the website ("going further") or a later episode: Kramers–Wannier duality,
SLE interfaces (dimension 11/8), Wolff vs Metropolis, nucleation & hysteresis, frustration.
