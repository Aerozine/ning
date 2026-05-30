#import "@preview/cetz:0.3.4": canvas, draw as cdraw

#set page(width: 841mm, height: 1189mm, margin: (top: 20mm, rest: 14mm), fill: rgb("#F8F9FA"))
#set text(font: "XITS", size: 28pt, fill: rgb("#17212B"))
#set par(justify: true, leading: 0.72em)
#set list(indent: 6pt, body-indent: 6pt)

#let blue   = rgb("#3D7FD8")
#let violet = rgb("#8B63D9")
#let pink   = rgb("#E84D8A")
#let grey   = rgb("#737985")
#let dark   = rgb("#27323C")
#let muted  = rgb("#59616F")
#let light  = rgb("#FFFFFF")
#let border = rgb("#E1DFE8")
#let amber  = rgb("#E8830A")

// Panel: subtle card with thin rounded border and coloured title bar
#let panel(title, body) = block(
  width: 100%,
  fill: white,
  stroke: (paint: rgb("#D0D4DC"), thickness: 0.8pt),
  radius: 4pt,
  inset: (x: 11pt, top: 0pt, bottom: 13pt),
)[
  // Coloured title strip
  #block(
    width: 100%,
    fill: blue.lighten(88%),
    inset: (x: 0pt, y: 8pt),
    radius: (top-left: 4pt, top-right: 4pt),
  )[
    #text(size: 28pt, weight: "bold", fill: blue)[#h(11pt)#title]
  ]
  #v(4pt)
  #body
]

#let tag(color, body) = box(
  fill: color.lighten(64%),
  stroke: color.lighten(38%),
  radius: 3pt,
  inset: (x: 6pt, y: 3pt),
)[#text(fill: color.darken(18%), weight: "bold", size: 23pt)[#body]]

#let metric(label, value, note, color: blue) = block(
  fill: color.lighten(84%),
  stroke: color.lighten(58%),
  radius: 4pt,
  inset: 9pt,
  width: 100%,
)[
  #text(size: 23pt, fill: grey, weight: "bold")[#label]
  #linebreak()
  #text(size: 32pt, fill: color, weight: "bold")[#value]
  #linebreak()
  #text(size: 23pt, fill: rgb("#44505C"))[#note]
]

#let caption(body) = text(size: 23pt, fill: muted)[#body]
#let smallnote(body) = text(size: 23pt, fill: muted)[#body]

// ─── Typst-native schematics ──────────────────────────────────────────────────

// Superconductivity R(T) diagram
#let draw_superconductivity = canvas(length: 1.55cm, {
  import cdraw: *

  // ── R(T) axes ──
  set-style(stroke: (paint: black, thickness: 1.4pt))
  line((0.5, 0.4), (0.5, 4.6), mark: (end: ">", size: .22))
  line((0.5, 0.4), (8.2, 0.4), mark: (end: ">", size: .22))
  content((0.15, 4.5), text(size: 8pt)[R], anchor: "east")
  content((8.3, 0.15), text(size: 8pt)[T], anchor: "north")

  // Rn dashed horizontal
  set-style(stroke: (paint: grey, thickness: 0.9pt, dash: "dashed"))
  line((0.5, 3.65), (7.8, 3.65))
  content((0.15, 3.65), text(size: 7pt, fill: grey)[$R_n$], anchor: "east")

  // Tc vertical dashed
  set-style(stroke: (paint: blue, thickness: 1.1pt, dash: "dashed"))
  line((4.5, 0.4), (4.5, 3.65))
  content((4.5, 0.1), text(size: 8pt, fill: blue)[$T_c$], anchor: "north")

  // R(T) curve
  set-style(stroke: (paint: black, thickness: 2.2pt, dash: "solid"))
  line((0.6, 0.5), (3.6, 0.5))
  bezier((3.6, 0.5), (5.4, 3.65), (3.9, 0.6), (5.1, 3.5))
  line((5.4, 3.65), (7.8, 3.65))

  // Region labels
  content((2.5, 1.4), text(size: 8.5pt, fill: violet, weight: "bold")[Superconducting], anchor: "center")
  content((6.8, 4.3), text(size: 8.5pt, fill: grey,   weight: "bold")[Normal], anchor: "center")

  // ── Meissner / vortex sketches ──
  set-style(stroke: (paint: rgb("#555"), thickness: 1.0pt))

  // ── Type I: complete flux expulsion ──
  content((1.8, -0.5), text(size: 8pt, fill: dark, weight: "bold")[Type I — Meissner], anchor: "center")
  rect((0.7, -2.8), (2.9, -1.0), fill: blue.lighten(80%), stroke: (paint: blue.darken(10%), thickness: 1.1pt))
  content((1.8, -1.9), text(size: 7pt, fill: blue.darken(20%), weight: "bold")[B = 0], anchor: "center")
  line((0.05, -1.35), (0.7, -1.35), mark: (end: ">", size: .13))
  line((0.05, -1.9),  (0.7, -1.9),  mark: (end: ">", size: .13))
  line((0.05, -2.45), (0.7, -2.45), mark: (end: ">", size: .13))
  bezier((0.7, -1.0), (1.8, -0.55), (1.0, -0.6), (1.6, -0.55))
  bezier((1.8, -0.55), (2.9, -1.0), (2.0, -0.55), (2.6, -0.6))
  bezier((0.7, -2.8), (1.8, -3.25), (1.0, -3.2), (1.6, -3.25))
  bezier((1.8, -3.25), (2.9, -2.8), (2.0, -3.25), (2.6, -3.2))
  line((2.9, -1.35), (3.55, -1.35), mark: (end: ">", size: .13))
  line((2.9, -1.9),  (3.55, -1.9),  mark: (end: ">", size: .13))
  line((2.9, -2.45), (3.55, -2.45), mark: (end: ">", size: .13))
  content((0.02, -2.0), text(size: 7pt)[$arrow.r B$], anchor: "east")

  // ── Type II: partial flux penetration (vortex state) ──
  content((6.3, -0.5), text(size: 8pt, fill: dark, weight: "bold")[Type II — Vortex state], anchor: "center")
  rect((5.2, -2.8), (7.4, -1.0), fill: violet.lighten(80%), stroke: (paint: violet.darken(10%), thickness: 1.1pt))
  set-style(stroke: (paint: rgb("#555"), thickness: 1.0pt))
  line((4.55, -1.5),  (8.05, -1.5),  mark: (end: ">", size: .13))
  line((4.55, -2.3),  (8.05, -2.3),  mark: (end: ">", size: .13))
  set-style(stroke: none)
  circle((5.65, -1.5),  radius: 0.20, fill: violet.lighten(30%))
  circle((6.30, -1.5),  radius: 0.20, fill: violet.lighten(30%))
  circle((6.95, -1.5),  radius: 0.20, fill: violet.lighten(30%))
  circle((5.65, -2.3),  radius: 0.20, fill: violet.lighten(30%))
  circle((6.30, -2.3),  radius: 0.20, fill: violet.lighten(30%))
  circle((6.95, -2.3),  radius: 0.20, fill: violet.lighten(30%))
  set-style(stroke: (paint: rgb("#555"), thickness: 1.0pt))
  bezier((5.2, -1.0), (6.3, -0.55), (5.5, -0.6), (6.1, -0.55))
  bezier((6.3, -0.55), (7.4, -1.0), (6.5, -0.55), (7.1, -0.6))
  bezier((5.2, -2.8), (6.3, -3.25), (5.5, -3.2), (6.1, -3.25))
  bezier((6.3, -3.25), (7.4, -2.8), (6.5, -3.25), (7.1, -3.2))
  content((5.0, -2.0), text(size: 7pt)[$arrow.r B$], anchor: "east")
  content((6.3, -3.5), text(size: 6.5pt, fill: muted)[vortex lattice], anchor: "center")
})

// RF Magnetron sputtering — tilted target head
#let draw_sputtering = canvas(length: 1.12cm, {
  import cdraw: *

  // ── Vacuum chamber ──
  set-style(stroke: (paint: grey, thickness: 0.9pt, dash: "dashed"))
  rect((0.3, 0.3), (11.0, 11.2))

  // ── Substrate (anode) — horizontal at top, rotating ──
  set-style(stroke: (paint: dark, thickness: 1.2pt, dash: "solid"))
  rect((2.0, 10.0), (9.0, 10.6), fill: rgb("#C8DCEF"), stroke: (paint: dark, thickness: 1.2pt))
  content((5.5, 10.95), text(size: 7.5pt, weight: "bold")[Substrate (anode) — rotating], anchor: "center")
  // Rotation arrow
  bezier((8.8, 10.3), (9.6, 10.2), (9.1, 10.55), (9.6, 10.4))
  content((9.85, 10.3), text(size: 9pt)[↻], anchor: "center")

  // ── Sputtered Nb atoms — diagonal toward substrate ──
  set-style(stroke: (paint: grey.darken(20%), thickness: 0.9pt))
  line((4.5, 7.0), (3.5, 10.0), mark: (end: ">", size: .15))
  line((5.2, 7.0), (5.5, 10.0), mark: (end: ">", size: .15))
  line((5.9, 7.0), (7.5, 10.0), mark: (end: ">", size: .15))
  content((6.5, 8.5), text(size: 7pt, fill: grey)[Nb+NbN], anchor: "west")

  // ── Plasma (elongated along target face) ──
  set-style(stroke: (paint: pink, thickness: 1.1pt))
  circle((4.8, 6.3), radius: (1.75, 0.55),
         fill: pink.lighten(82%), stroke: (paint: pink, thickness: 1.1pt))
  content((4.8, 6.3), text(size: 7pt, fill: pink.darken(30%))[Ar#super[+] plasma], anchor: "center")

  // ── Magnetron head — tilted ~25° ──
  // Tilt: right end higher.  All four polygons are parallelograms shifted
  // perpendicular to the face (normal direction ≈ (-0.42, 0.91)).

  // Target face (cathode): front face at left, tilted
  // Corners: TL=(2.8,4.2), TR=(6.8,6.0), BR=(7.0,5.4), BL=(3.0,3.6)
  // Fill: steel blue
  line((2.8,4.2),(6.8,6.0),(7.0,5.4),(3.0,3.6),(2.8,4.2),
       fill: rgb("#7A8EBC"), stroke: (paint: dark, thickness: 1.1pt))
  content((4.9, 4.85), text(size: 7pt, fill: white, weight: "bold")[Nb target (cathode)],
          anchor: "center")

  // Magnet row (N/S Halbach) — behind target
  // Corners: same parallelogram shifted by (+0.2, -0.6)
  // BL=(3.2,3.0), BR=(7.2,4.8), TR=(7.0,5.4) — shared with target back
  let m1 = (3.0,3.6); let m2 = (7.0,5.4); let m3 = (7.2,4.8); let m4 = (3.2,3.0)
  // N-pole segments (red)
  line(m1, (4.3,4.2), (4.5,3.6), m4, m1, fill: rgb("#F5A0A0"), stroke: (paint: dark, thickness: 0.6pt))
  line((4.3,4.2),(5.6,4.9),(5.8,4.3),(4.5,3.6),(4.3,4.2), fill: rgb("#A0C0F5"), stroke: (paint: dark, thickness: 0.6pt))
  line((5.6,4.9),(6.8,5.55),(7.0,4.95),(5.8,4.3),(5.6,4.9), fill: rgb("#F5A0A0"), stroke: (paint: dark, thickness: 0.6pt))
  line((6.8,5.55),m2,m3,(7.0,4.95),(6.8,5.55), fill: rgb("#A0C0F5"), stroke: (paint: dark, thickness: 0.6pt))
  set-style(stroke: none)
  content((3.65,3.65), text(size: 6pt, weight: "bold")[N], anchor: "center")
  content((5.05,4.4),  text(size: 6pt, weight: "bold")[S], anchor: "center")
  content((6.35,5.15), text(size: 6pt, weight: "bold")[N], anchor: "center")
  content((6.9,5.22),  text(size: 6pt, weight: "bold")[S], anchor: "center")

  // Magnetic field arcs (confine electrons near target)
  set-style(stroke: (paint: rgb("#7777CC"), thickness: 0.75pt, dash: "dotted"))
  bezier((3.2,4.2),(3.8,5.0),(3.0,4.7),(3.6,5.0))
  bezier((3.8,5.0),(4.4,4.3),(4.0,5.0),(4.2,4.7))
  bezier((5.0,4.8),(5.6,5.6),(4.8,5.3),(5.4,5.6))
  bezier((5.6,5.6),(6.2,4.9),(5.8,5.5),(6.0,5.2))
  content((8.0,5.5), text(size: 6.5pt, fill: rgb("#5555AA"))[B trap], anchor: "west")

  // Water cooling — behind magnets
  line(m4,(3.2,3.0),(3.4,2.4),(7.4,4.2),(7.2,4.8),m3,m2, // outline only
       fill: rgb("#A8D8F0"), stroke: (paint: dark, thickness: 1.0pt))
  content((5.2, 3.65), text(size: 7pt)[🌊 water cooling], anchor: "center")

  // ── RF supply connection — from target back to right ──
  set-style(stroke: (paint: grey.darken(30%), thickness: 1.0pt, dash: "solid"))
  line((7.0,5.4),(9.2,5.4))
  line((9.2,5.4),(9.2,3.5))
  content((9.5,4.5), text(size: 7pt)[RF\nsupply], anchor: "west")

  // ── Gas inlets ──
  set-style(stroke: (paint: grey, thickness: 0.85pt))
  line((0.6, 8.5), (2.0, 8.0), mark: (end: ">", size: .14))
  content((0.45, 8.8), text(size: 7pt)[Ar], anchor: "center")
  line((0.6, 7.3), (2.0, 7.0), mark: (end: ">", size: .14))
  content((0.4, 7.3), text(size: 7pt)[N#sub[2]], anchor: "center")

  // ── Labels ──
  set-style(stroke: none)
  content((2.0, 1.9), text(size: 7pt, fill: dark)[Magnetron head (inclined)], anchor: "center")
})

// EBL resist-stack diagram — 4 steps
#let draw_ebl = canvas(length: 1.38cm, {
  import cdraw: *

  let si_col   = rgb("#B0B8C8")
  let copmma_c = rgb("#9FC8E8")
  let pmma_c   = rgb("#BDE3F7")
  let nbn_c    = rgb("#8B9DC3")

  // 2×2 grid layout
  // Row 1 (top):    y_base = 6.5   — steps 1 (left) and 2 (right)
  // Row 2 (bottom): y_base = 0.0   — steps 4 (left) and 3 (right)
  // Serpentine flow: 1 →(right)→ 2 →(down)→ 3 →(left)→ 4

  // ─ STEP 1: initial resist stack (top-left) ─
  content((2.0, 11.1), text(size: 23pt, weight: "bold")[1. Stack], anchor: "center")
  rect((0.2, 6.5), (3.8, 7.4), fill: si_col,    stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 6.95), text(size: 23pt)[Si], anchor: "center")
  rect((0.2, 7.4), (3.8, 8.4), fill: copmma_c,  stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 7.9),  text(size: 23pt)[co-PMMA], anchor: "center")
  rect((0.2, 8.4), (3.8, 9.4), fill: pmma_c,    stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 8.9),  text(size: 23pt)[PMMA], anchor: "center")

  // ─ arrow 1 →(right)→ 2 ─
  set-style(stroke: (paint: dark, thickness: 1.2pt))
  line((4.0, 8.0), (4.9, 8.0), mark: (end: ">", size: .18))

  // ─ STEP 2: EBL exposure + development (top-right) ─
  content((7.0, 11.1), text(size: 23pt, weight: "bold")[2. EBL + develop], anchor: "center")
  set-style(stroke: (paint: blue, thickness: 1.3pt))
  line((7.0, 10.6), (7.0, 9.4), mark: (end: ">", size: .16))
  content((7.0, 10.85), text(size: 23pt, fill: blue)[$e^-$], anchor: "center")
  set-style(stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 6.5), (8.8, 7.4), fill: si_col,   stroke: (paint: dark, thickness: 0.8pt))
  content((7.0, 6.95), text(size: 23pt)[Si], anchor: "center")
  rect((5.2, 7.4), (6.3, 8.4), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  rect((7.7, 7.4), (8.8, 8.4), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  set-style(stroke: (paint: dark, thickness: 0.6pt, dash: "dashed"))
  line((6.3, 7.4), (6.5, 8.4))
  line((7.7, 7.4), (7.5, 8.4))
  set-style(stroke: (paint: dark, thickness: 0.8pt, dash: "solid"))
  rect((5.2, 8.4), (6.5, 9.4), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  rect((7.5, 8.4), (8.8, 9.4), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  set-style(stroke: (paint: pink, thickness: 0.7pt))

  // ─ arrow 2 →(down)→ 3 ─
  set-style(stroke: (paint: dark, thickness: 1.2pt, dash: "solid"))
  line((7.0, 6.3), (7.0, 5.1), mark: (end: ">", size: .18))

  // ─ STEP 3: NbN deposition (bottom-right) ─
  content((7.0, 4.6), text(size: 23pt, weight: "bold")[3. NbN dep.], anchor: "center")
  set-style(stroke: (paint: grey, thickness: 0.8pt))
  for xd in (5.7, 6.3, 6.8, 7.3, 7.8, 8.3) {
    line((xd, 4.0), (xd, 3.3), mark: (end: ">", size: .12))
  }
  set-style(stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 0.0), (8.8, 0.9), fill: si_col,   stroke: (paint: dark, thickness: 0.8pt))
  content((7.0, 0.45), text(size: 23pt)[Si], anchor: "center")
  rect((5.2, 0.9), (6.3, 1.9), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  rect((7.7, 0.9), (8.8, 1.9), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 1.9), (6.5, 2.9), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  rect((7.5, 1.9), (8.8, 2.9), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 2.9), (6.5, 3.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  rect((7.5, 2.9), (8.8, 3.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  rect((6.3, 0.9), (7.7, 1.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  content((7.0, 1.05), text(size: 23pt, fill: white)[NbN], anchor: "center")

  // ─ arrow 3 →(left)→ 4 ─
  set-style(stroke: (paint: dark, thickness: 1.2pt))
  line((5.0, 1.5), (4.1, 1.5), mark: (end: ">", size: .18))

  // ─ STEP 4: lift-off result (bottom-left) ─
  content((2.0, 4.6), text(size: 23pt, weight: "bold")[4. Lift-off], anchor: "center")
  rect((0.2, 0.0), (3.8, 0.9), fill: si_col,  stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 0.45), text(size: 23pt)[Si], anchor: "center")
  rect((1.3, 0.9), (2.7, 1.2), fill: nbn_c,   stroke: (paint: dark, thickness: 1.0pt))
  content((2.0, 1.05), text(size: 23pt, fill: white)[NbN], anchor: "center")
  set-style(stroke: (paint: nbn_c, thickness: 0.7pt))
  line((2.0, 1.2), (2.0, 1.7), mark: (end: ">", size: .12))
  content((2.0, 1.95), text(size: 23pt, fill: nbn_c)[bridge], anchor: "center")
  content((3.5, 3.5), text(size: 23pt, fill: pink)[resist removed], anchor: "east")

  // Layer colour legend (below bottom-right panel)
  content((8.7, -0.5), text(size: 23pt, fill: si_col.darken(40%))[▪ Si],        anchor: "east")
  content((8.7, -0.9), text(size: 23pt, fill: copmma_c.darken(40%))[▪ co-PMMA], anchor: "east")
  content((8.7, -1.3), text(size: 23pt, fill: pmma_c.darken(40%))[▪ PMMA],      anchor: "east")
  content((8.7, -1.7), text(size: 23pt, fill: nbn_c.darken(10%))[▪ NbN],        anchor: "east")
})

// ─── Poster layout ────────────────────────────────────────────────────────────

// ── Header ──
#grid(
  columns: (1.2fr, 5.7fr, 1.2fr),
  gutter: 9mm,
  align(left + horizon)[#image("../researchproposal/ulgfsa.svg", width: 160mm)],
  align(center)[
    #text(size: 56pt, weight: "bold", fill: blue)[Growth Optimisation of Superconducting NbN]
    #linebreak()
    #text(size: 31pt, fill: dark)[Tuning reactive RF magnetron sputtering · Evaluating finite-width NbN bridges]
    #v(4pt)
    #text(size: 22pt, fill: muted)[
      APRI0006 Experimental Project | Loïc Delbarre | Supervisors: Cyril Delforge & Abhishek Naik | Advisor: A. V. Silhanek
    ]
  ],
  align(right + horizon)[#image("../researchproposal/epnm.png", width: 136mm)],
)

#v(8mm)

// ── Research question — prominent centred box ──
#block(
  width: 100%,
  fill: blue.lighten(88%),
  stroke: (paint: blue, thickness: 1.5pt),
  radius: 6pt,
  inset: (x: 22pt, y: 18pt),
)[
  #align(center)[
    #text(size: 38pt, weight: "bold", fill: blue)[Research Question]
    #v(6pt)
    #text(size: 32pt, fill: dark)[
      What N#sub[2] fraction in reactive RF sputtering maximises $T_c$ of NbN thin films,
      and does EBL nano-patterning preserve superconductivity in finite-width bridges?
    ]
    #v(8pt)
    #text(size: 26pt, fill: muted)[
      *Answer:* $P_(N_2)=10%$ gives plain-film $T_c=10.99$ K · EBL-patterned bridges remain supra-conducting at ~8 K · $Delta T_c approx 3$ K (confinement + scattering, not a defect)
    ]
  ]
]

#v(8mm)

// ══════════════════════════════════════════════════════════════════════════════
// 2-COLUMN LAYOUT — nested sub-grids to fill white space
// Left = RF process & growth study  |  Right = SC physics + bridge study
// ══════════════════════════════════════════════════════════════════════════════
#grid(
  columns: (1fr, 1fr),
  gutter: 14mm,

  // ══ LEFT — RF sputtering, deposition rate, Tc study ═══════════════════════
  [
    // ── Row 1: Introduction + Methods side-by-side ──
    #grid(
      columns: (1fr, 1fr),
      gutter: 7mm,
      [#panel([1. Introduction])[
        #set par(leading: 0.85em)
        #v(4pt)
        - NbN: *Type II superconductor*, $T_c$ up to 17.3 K (Keskar 1971) — exceeds pure Nb (~8 K)
        #v(6pt)
        - $T_c$ tuned by N#sub[2] fraction: $P_(N_2)=100 F_(N_2)\/(F_("Ar")+F_(N_2))$
        #v(6pt)
        - Three structural zones R#sub[I/II/III] give distinct $T_c$ — Kalal et al. 2021
        #v(6pt)
        - *Goal 1:* find optimal $P_(N_2)$ for highest reproducible $T_c$
        #v(6pt)
        - *Goal 2:* verify EBL-patterned bridges stay superconducting after nano-patterning
        #v(4pt)
      ]],
      [#panel([2. Methods])[
        #v(4pt)
        #tag(blue)[Deposition] 50 nm NbN deposited by reactive RF magnetron sputtering (210 W, $10^(-8)$ Torr, 20 sccm), $P_(N_2)$ varied 2–20 %
        #v(10pt)
        #tag(violet)[Transport] 4-point $R(T)$ in cryostat; $T_c$ = midpoint of resistive transition (max $|"dR"/"dT"|$); onset (90 %) and offset (10 %) provide two alternative $T_c$ definitions
        #v(10pt)
        #tag(pink)[EBL] PMMA/co-PMMA bilayer patterned by e-beam lithography (Raith Pioneer Two); NbN deposited and lifted off → bridges C1 (10 µm) and D1 (20 µm)
        #v(4pt)
      ]],
    )
    #v(8mm)
    // ── Row 2: RF Sputtering ──
    #panel([3. Reactive RF Sputtering])[
      #align(center)[#image("../plot/sputtering_diagram.pdf", width: 94%)]
      #caption([Inclined magnetron: N/S magnets trap electrons (B-field arches), Ar#super[+] sputters Nb → NbN on rotating anode. RF supply connected via anode and cathode cables.])
    ]
    #v(8mm)
    // ── Row 3: Deposition Rate + Tc vs PN2 side-by-side ──
    #grid(
      columns: (1fr, 1fr),
      gutter: 7mm,
      [
        #panel([4. Deposition Rate vs $P_(N_2)$])[
          #align(center)[#image("../plot/deposition_rate_n2_fraction.pdf", width: 98%)]
          #caption([Higher $P_(N_2)$ dilutes Ar, reducing plasma density and Ar#super[+] mean free path → fewer sputtering events → lower deposition rate.])
        ]
        #v(8mm)
        #block(
          width: 100%,
          fill: amber.lighten(88%),
          stroke: (paint: amber.lighten(55%), thickness: 0.7pt),
          radius: 4pt,
          inset: (x: 11pt, y: 10pt),
        )[
          #text(size: 20pt, fill: dark)[
            *Acknowledgements* — *Cyril Delforge* and *Abhishek Naik* provided daily supervision and prepared several NbN samples for this study. *Julia Baumgarten* contributed the C1 & D1 bridge transport measurements and several $T_c$ vs $P_(N_2)$ data points. *Nicolas Lejeune* retrieved all additional $T_c$ measurements from the NbN samples used in this study.
          ]
        ]
      ],
      [#panel([5. $T_c$ vs $P_(N_2)$ — Growth results])[
        #align(center)[#image("../plot/tc_vs_n2_fraction.pdf", width: 98%)]
        #caption([$T_c$ peaks in zone *R#sub[II]* (#sym.delta\u{2011}NbN) at $P_(N_2)=10%$ — balance between N incorporation and over-nitridation. $T_c$ defined as midpoint (max $|"dR"/"dT"|$); error bars span onset (90 %) to offset (10 %). Results agree qualitatively with Kalal et al. 2021.])
        #v(3pt)
        #grid(
          columns: (1fr, 1fr, 1fr, 1fr, auto),
          rows: (36mm, auto),
          gutter: (1mm, 2pt),
          align(center + horizon)[#image("../molecule3d_split_pure_nb_4x.png", height: 33mm)],
          align(center + horizon)[#image("../molecule3d_split_r1_4x.png",      height: 33mm)],
          align(center + horizon)[#image("../molecule3d_split_r2_4x.png",      height: 33mm)],
          align(center + horizon)[#image("../molecule3d_split_r3_4x.png",      height: 33mm)],
          [],
          align(center)[#caption([Nb])],
          align(center)[#caption([R#sub[I]])],
          align(center)[#caption([R#sub[II]])],
          align(center)[#caption([R#sub[III]])],
          align(center + horizon)[#image("../molecule3d_split_legend_nb_n_4x.png", height: 13mm)],
        )
      ]],
    )
  ],

  // ══ RIGHT — SC physics, bridge fabrication, results ═══════════════════════
  [
    // ── Row 1: SC field diagram ──
    #panel([6. Superconducting Transition — Type I vs Type II])[
      #align(center)[#image("../plot/sc_field_diagram.pdf", width: 90%)]
      #caption([
        *Normal* ($T>T_c$): B passes through. *Type I* (Pb): Meissner — $B=0$ inside. *Type II* (NbN): vortex lattice above $H_(c 1)$; $R=0$ until $H_(c 2)$.
      ])
    ]
    #v(8mm)
    // ── Row 2: R(T) + EBL side-by-side ──
    #grid(
      columns: (1fr, 1fr),
      gutter: 7mm,
      [#panel([7. R(T) — Plain Film \& Bridges])[
        #align(center)[#image("../plot/transition_and_bridge.pdf", width: 98%)]
        #caption([
          4-point geometry. Bridges transition ~3 K below the plain film. The $Delta T_c$ is *width-independent* (C1 ≈ D1): drop reflects lithography transfer (edge roughness, contacts, EBL scattering).
        ])
      ]],
      [#panel([8. EBL — Bridge Fabrication])[
        #align(center)[#draw_ebl]
        #caption([PMMA/co-PMMA bilayer; co-PMMA undercut → clean NbN lift-off. C1 (10 µm) and D1 (20 µm).])
      ]],
    )
    #v(8mm)
    // ── Row 3: Bridge Benchmark + Conclusions side-by-side ──
    #grid(
      columns: (1fr, 1fr),
      gutter: 7mm,
      [#panel([9. Finite-Width Benchmark])[
        #align(center)[#image("../plot/bridge_tc_reference.pdf", width: 98%)]
        #v(3mm)
        #table(
          columns: (auto, auto, auto, auto),
          stroke: (paint: border, thickness: 0.6pt),
          inset: 4pt,
          align: center,
          table.header[*Dev.*][*W*][$T_c$][$Delta T_c$],
          [C1], [10 µm], [~8.1 K], [−2.9 K],
          [D1], [20 µm], [~8.0 K], [−3.0 K],
          [Film], [—], [10.99 K], [ref],
        )
        #v(3mm)
        #grid(
          columns: (1fr, 1fr),
          gutter: 7mm,
          [
            #align(center)[#image("images/gds_C1.png", width: 90%)]
            #align(center)[#caption([GDS — C1 (W = 10 µm)])]
          ],
          [
            #align(center)[#image("images/gds_D1.png", width: 90%)]
            #align(center)[#caption([GDS — D1 (W = 20 µm)])]
          ],
        )
        #v(3pt)
        #caption([Both bridges SC at ~8 K. Width-independent $Delta T_c approx 3$ K → lithography transfer effects.])
      ]],
      [
        #panel([Conclusions])[
          #set par(leading: 0.65em)
          #text(size: 23pt)[A nitrogen fraction of $P_(N_2) approx 10%$ in reactive RF magnetron sputtering yields an optimal $T_c = 10.99$ K (zone R#sub[II], #sym.delta\u{2011}NbN phase), confirming process reproducibility.]
          #v(5pt)
          #text(size: 23pt)[Four-point transport measurements on EBL-patterned bridges show that nano-patterning preserves the superconducting properties, with both C1 and D1 remaining superconducting at ~8 K.]
          #v(5pt)
          #text(size: 23pt)[The $Delta T_c approx 3$ K reduction is attributed to electronic confinement and the higher interface-to-volume ratio of narrow bridges, which enhances electron scattering.]
          #v(5pt)
          #text(size: 23pt)[The $T_c$–thickness relation is well established (cf. Gavaler *[5]*):
          $ T_c (d) = T_(c 0) lr((1 - d_c / d)) $
          with $T_(c 0)$ the bulk limit and $d_c$ the critical thickness below which superconductivity is suppressed.]
        ]
        #v(2mm)
        #panel([References])[
          #text(size: 23pt, fill: muted)[
            *[1]* Keskar et al., _Jpn. J. Appl. Phys._ *10* (1971) #linebreak()
            *[2]* Sugimoto & Motohiro, _Vacuum_ *93* (2013) #linebreak()
            *[3]* Kalal et al., _J. Alloys Compd._ *851* (2021) #linebreak()
            *[4]* Glowacka et al., _arXiv:1401.2276_ (2014) #linebreak()
            *[5]* Gavaler et al., _Physica_ *55* (1971)
          ]
        ]
        #v(2mm)
        #block(
          width: 100%,
          fill: blue.lighten(92%),
          stroke: (paint: blue.lighten(60%), thickness: 0.7pt),
          radius: 3pt,
          inset: (x: 8pt, y: 8pt),
        )[
          #text(size: 20pt, fill: muted)[All raw data and analysis source code are openly available at: #text(fill: blue)[*github.com/Aerozine/ning*]]
        ]
      ],
    )
  ],
)

#v(1.5mm)

#block(
  width: 100%,
  fill: violet.lighten(84%),
  stroke: border,
  radius: 4pt,
  inset: (x: 8pt, y: 3pt),
)[
  #text(size: 16pt, fill: muted)[APRI0006 Experimental Project · Engineering Physics · University of Liège · Loïc Delbarre]
]
