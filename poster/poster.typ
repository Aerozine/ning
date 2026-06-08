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
  stroke: (paint: blue.lighten(35%), thickness: 0.9pt),
  radius: 4pt,
  inset: 0pt,
)[
  // Coloured title strip
  #block(
    width: 100%,
    fill: blue.lighten(88%),
    inset: (x: 11pt, y: 8pt),
    radius: (top-left: 4pt, top-right: 4pt),
  )[
    #text(size: 28pt, weight: "bold", fill: blue)[#title]
  ]
  #block(width: 100%, inset: (x: 11pt, bottom: 13pt))[#v(-8pt)#body]
]

#let tag(color, body) = box(
  fill: color.lighten(64%),
  stroke: color.lighten(38%),
  radius: 3pt,
  inset: (x: 6pt, y: 3pt),
)[#text(fill: color.darken(18%), weight: "bold", size: 25pt)[#body]]

#let metric(label, value, note, color: blue) = block(
  fill: color.lighten(84%),
  stroke: color.lighten(58%),
  radius: 4pt,
  inset: 9pt,
  width: 100%,
)[
  #text(size: 25pt, fill: grey, weight: "bold")[#label]
  #linebreak()
  #text(size: 32pt, fill: color, weight: "bold")[#value]
  #linebreak()
  #text(size: 25pt, fill: rgb("#44505C"))[#note]
]

#let caption(body) = text(size: 25pt, fill: muted)[#body]
#let smallnote(body) = text(size: 25pt, fill: muted)[#body]

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
  content((6.8, 4.3), text(size: 17pt, fill: grey,   weight: "bold")[Normal], anchor: "center")

  // ── Meissner / vortex sketches ──
  set-style(stroke: (paint: rgb("#555"), thickness: 1.0pt))

  // ── Type I: complete flux expulsion ──
  content((1.8, -0.5), text(size: 16pt, fill: dark, weight: "bold")[Type I — Meissner], anchor: "center")
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
  content((6.3, -0.5), text(size: 16pt, fill: dark, weight: "bold")[Type II — Vortex state], anchor: "center")
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

// RF Magnetron sputtering — ported from process_nbn.py / plot_sputtering_diagram
#let draw_sputtering = canvas(length: 2.07cm, {
  import cdraw: *

  let arch_col   = rgb("#1A237E")
  let pdot_col   = rgb("#BE70CB")   // #9C27B0 @ 0.66 opacity on white
  let bdot_col   = rgb("#5790D2")   // #1565C0 @ 0.72 opacity on white
  let cone_col   = rgb("#F7EEF9")   // #CE93D8 @ 0.16 opacity on white

  // ── Chamber: dashed rect, left wall has two gaps for gas inlets ──
  let chs = (paint: rgb("#555"), thickness: 1.1pt, dash: "dashed")
  line((0.3, 0.3),  (9.7, 0.3),  stroke: chs)
  line((9.7, 0.3),  (9.7, 11.7), stroke: chs)
  line((0.3, 11.7), (9.7, 11.7), stroke: chs)
  line((0.3, 0.3),  (0.3, 7.58), stroke: chs)
  line((0.3, 8.02), (0.3, 8.78), stroke: chs)
  line((0.3, 9.22), (0.3, 11.7), stroke: chs)

  // ── Plasma cone FIRST (back layer) — trapezoid target face → substrate ──
  line((2.8, 3.6), (7.2, 3.6), (8.8, 10.5), (1.2, 10.5), (2.8, 3.6),
       fill: cone_col, stroke: none)

  // ── Target (cathode) ──
  rect((2.8, 3.0), (7.2, 3.6),
       fill: rgb("#B0BEC5"), stroke: (paint: rgb("#37474F"), thickness: 1.4pt))

  // ── N–S–N magnets (seg_w = 4.4/3 ≈ 1.467) ──
  rect((2.8,   2.35), (4.267, 3.0), fill: rgb("#E53935"), stroke: (paint: rgb("#333"), thickness: 0.7pt))
  rect((4.267, 2.35), (5.733, 3.0), fill: rgb("#9E9E9E"), stroke: (paint: rgb("#333"), thickness: 0.7pt))
  rect((5.733, 2.35), (7.2,   3.0), fill: rgb("#E53935"), stroke: (paint: rgb("#333"), thickness: 0.7pt))

  // ── Water cooling ──
  rect((2.8, 1.6), (7.2, 2.35),
       fill: rgb("#90CAF9"), stroke: (paint: rgb("#1565C0"), thickness: 0.9pt))

  // ── Ground shields ──
  rect((2.0, 1.6), (2.8, 4.0), fill: rgb("#78909C"), stroke: (paint: rgb("#37474F"), thickness: 1.1pt))
  rect((7.2, 1.6), (8.0, 4.0), fill: rgb("#78909C"), stroke: (paint: rgb("#37474F"), thickness: 1.1pt))

  // ── B-field arcs: bezier-approximated semicircles above target ──
  // Centers: left=(4.267,3.6), right=(5.733,3.6); radii r1=0.381, r2=0.660; k=0.5523
  set-style(stroke: (paint: arch_col, thickness: 2.0pt, dash: "dashed"))
  // Left r1: (4.648,3.6)→peak(4.267,3.981)→(3.886,3.6)
  bezier((4.648,3.6),   (4.267,3.981), (4.648,3.810), (4.477,3.981))
  bezier((4.267,3.981), (3.886,3.6),   (4.057,3.981), (3.886,3.810))
  // Left r2: (4.927,3.6)→peak(4.267,4.260)→(3.607,3.6)
  bezier((4.927,3.6),   (4.267,4.260), (4.927,3.965), (4.632,4.260))
  bezier((4.267,4.260), (3.607,3.6),   (3.902,4.260), (3.607,3.965))
  // Right r1: (6.114,3.6)→peak(5.733,3.981)→(5.352,3.6)
  bezier((6.114,3.6),   (5.733,3.981), (6.114,3.810), (5.943,3.981))
  bezier((5.733,3.981), (5.352,3.6),   (5.523,3.981), (5.352,3.810))
  // Right r2: (6.393,3.6)→peak(5.733,4.260)→(5.073,3.6)
  bezier((6.393,3.6),   (5.733,4.260), (6.393,3.965), (6.098,4.260))
  bezier((5.733,4.260), (5.073,3.6),   (5.368,4.260), (5.073,3.965))
  set-style(stroke: (paint: arch_col, thickness: 1.4pt, dash: "solid"))
  line((4.207,3.981), (4.327,3.981), mark: (end: ">", size: .10))
  line((4.207,4.260), (4.327,4.260), mark: (end: ">", size: .10))
  line((5.793,3.981), (5.673,3.981), mark: (end: ">", size: .10))
  line((5.793,4.260), (5.673,4.260), mark: (end: ">", size: .10))

  // ── Dots (drawn above cone, below substrate) ──
  set-style(stroke: none)
  for pt in (
    (3.02,9.62),(4.18,10.08),(6.04,9.70),(7.55,9.28),
    (2.45,8.72),(3.50,8.55),(4.95,8.92),(6.70,8.52),
    (2.70,7.83),(4.58,7.58),(5.72,7.92),(7.18,7.44),
    (3.30,6.82),(4.25,6.35),(5.48,6.62),(6.34,6.08),
    (3.76,5.68),(5.05,5.33),(6.78,5.14),(4.58,4.82),(5.70,4.54),
  ) { circle(pt, radius: 0.05, fill: pdot_col, stroke: none) }
  for pt in (
    (3.55,9.12),(5.30,9.42),(6.96,9.05),
    (2.90,8.28),(4.15,8.04),(6.10,8.12),
    (3.48,7.16),(5.05,7.02),(6.58,6.82),
    (4.06,6.05),(5.82,5.72),(6.92,5.62),
  ) { circle(pt, radius: 0.04, fill: bdot_col, stroke: none) }

  // ── NbN film then substrate (drawn last → on top of cone) ──
  rect((1.2, 10.28), (8.8, 10.5),
       fill: rgb("#90A4AE"), stroke: (paint: rgb("#455A64"), thickness: 0.8pt))
  rect((1.2, 10.5), (8.8, 11.05),
       fill: rgb("#4CAF50"), stroke: (paint: rgb("#1B5E20"), thickness: 1.5pt))

  // ── RF supply box and cables ──
  let wires = (paint: rgb("#555"), thickness: 1.2pt, dash: "solid")
  line((8.8,10.83),  (10.55,10.83), stroke: wires)
  line((10.55,10.83),(10.55,7.0),   stroke: wires)
  line((8.0,3.6),    (10.55,3.6),   stroke: wires)
  line((10.55,3.6),  (10.55,5.0),   stroke: wires)
  rect((9.9,5.0), (11.2,7.0),
       fill: rgb("#FFF9C4"), stroke: (paint: rgb("#555"), thickness: 1.2pt))

  // ── All text labels (drawn on top) ──
  set-style(stroke: none)
  content((5.0, 11.92), text(size: 24pt, fill: rgb("#555"))[Vacuum chamber], anchor: "south")
  content((5.0, 10.775),
    text(size: 28pt, fill: white, weight: "bold")[Substrate (anode) #sym.arrow.ccw],
    anchor: "center")
  content((5.0, 10.39),
    text(size: 18pt, fill: rgb("#37474F"), weight: "bold")[NbN thin film],
    anchor: "center")
  content((5.0, 3.3),
    text(size: 26pt, fill: rgb("#1A2A2A"), weight: "bold")[Nb target (cathode)],
    anchor: "center")
  content((3.533, 2.675), text(size: 20pt, fill: white, weight: "bold")[N], anchor: "center")
  content((5.0,   2.675), text(size: 20pt, fill: white, weight: "bold")[S], anchor: "center")
  content((6.467, 2.675), text(size: 20pt, fill: white, weight: "bold")[N], anchor: "center")
  content((5.0, 1.975), text(size: 20pt, fill: rgb("#0D47A1"))[Water cooling], anchor: "center")
  content((8.35, 2.8), text(size: 20pt, fill: rgb("#37474F"))[Ground\ shield], anchor: "west")
  content((7.63, 4.95),
    box(fill: none, inset: (x: 3pt, y: 2pt))[
      #text(size: 22pt, fill: arch_col)[B-field\ trap]
    ], anchor: "west")
  content((10.55, 6.0), text(size: 28pt, fill: rgb("#333"), weight: "bold")[RF], anchor: "center")

  // Plasma / atom labels with pointer arrows
  content((0.78,5.68),
    box(fill: none, inset: (x: 2pt, y: 1pt))[#text(size: 18pt, fill: rgb("#8E24AA"))[Ar#super[+] plasma]],
    anchor: "west")
  content((0.78,4.98),
    box(fill: none, inset: (x: 2pt, y: 1pt))[#text(size: 18pt, fill: rgb("#1565C0"))[Nb/NbN atoms]],
    anchor: "west")
  line((1.96,5.78), (2.55,6.65), mark: (end: ">", size: .09),
       stroke: (paint: rgb("#8E24AA"), thickness: 1.1pt))
  line((1.96,4.98), (4.06,6.05), mark: (end: ">", size: .09),
       stroke: (paint: rgb("#1565C0"), thickness: 1.1pt))

  // ── Gas inlet arrows with species labels ──
  line((0.3,9.0), (1.8,9.0), mark: (end: ">", size: .12),
       stroke: (paint: rgb("#E65100"), thickness: 1.8pt))
  content((0.25,9.0), text(size: 28pt, fill: rgb("#E65100"), weight: "bold")[Ar], anchor: "east")
  line((0.3,7.8), (1.8,7.8), mark: (end: ">", size: .09),
       stroke: (paint: rgb("#0277BD"), thickness: 0.9pt))
  content((0.25,7.8), text(size: 28pt, fill: rgb("#0277BD"), weight: "bold")[N#sub[2]], anchor: "east")
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
  content((2.0, 11.1), text(size: 25pt, weight: "bold")[1. Stack], anchor: "center")
  rect((0.2, 6.5), (3.8, 7.4), fill: si_col,    stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 6.95), text(size: 25pt)[Si], anchor: "center")
  rect((0.2, 7.4), (3.8, 8.4), fill: copmma_c,  stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 7.9),  text(size: 25pt)[co-PMMA], anchor: "center")
  rect((0.2, 8.4), (3.8, 9.4), fill: pmma_c,    stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 8.9),  text(size: 25pt)[PMMA], anchor: "center")

  // ─ arrow 1 →(right)→ 2 ─
  set-style(stroke: (paint: dark, thickness: 1.2pt))
  line((4.0, 8.0), (4.9, 8.0), mark: (end: ">", size: .18))

  // ─ STEP 2: EBL exposure + development (top-right) ─
  content((7.0, 11.1), text(size: 25pt, weight: "bold")[2. EBL + develop], anchor: "center")
  set-style(stroke: (paint: blue, thickness: 1.3pt))
  line((7.0, 10.6), (7.0, 9.4), mark: (end: ">", size: .16))
  content((7.0, 10.72), text(size: 25pt, fill: blue)[$e^-$], anchor: "center")
  set-style(stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 6.5), (8.8, 7.4), fill: si_col,   stroke: (paint: dark, thickness: 0.8pt))
  content((7.0, 6.95), text(size: 25pt)[Si], anchor: "center")
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
  content((7.0, 4.6), text(size: 25pt, weight: "bold")[3. NbN dep.], anchor: "center")
  set-style(stroke: (paint: grey, thickness: 0.8pt))
  for xd in (5.7, 6.3, 6.8, 7.3, 7.8, 8.3) {
    line((xd, 4.0), (xd, 3.3), mark: (end: ">", size: .12))
  }
  set-style(stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 0.0), (8.8, 0.9), fill: si_col,   stroke: (paint: dark, thickness: 0.8pt))
  content((7.0, 0.45), text(size: 25pt)[Si], anchor: "center")
  rect((5.2, 0.9), (6.3, 1.9), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  rect((7.7, 0.9), (8.8, 1.9), fill: copmma_c, stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 1.9), (6.5, 2.9), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  rect((7.5, 1.9), (8.8, 2.9), fill: pmma_c,   stroke: (paint: dark, thickness: 0.8pt))
  rect((5.2, 2.9), (6.5, 3.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  rect((7.5, 2.9), (8.8, 3.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  rect((6.3, 0.9), (7.7, 1.2), fill: nbn_c,    stroke: (paint: dark, thickness: 0.7pt))
  content((7.0, 1.05), text(size: 19pt, fill: white)[NbN], anchor: "center")

  // ─ arrow 3 →(left)→ 4 ─
  set-style(stroke: (paint: dark, thickness: 1.2pt))
  line((5.0, 1.5), (4.1, 1.5), mark: (end: ">", size: .18))

  // ─ STEP 4: lift-off result (bottom-left) ─
  content((2.0, 4.6), text(size: 25pt, weight: "bold")[4. Lift-off], anchor: "center")
  rect((0.2, 0.0), (3.8, 0.9), fill: si_col,  stroke: (paint: dark, thickness: 0.8pt))
  content((2.0, 0.45), text(size: 25pt)[Si], anchor: "center")
  rect((1.3, 0.9), (2.7, 1.2), fill: nbn_c,   stroke: (paint: dark, thickness: 1.0pt))
  content((2.0, 1.05), text(size: 19pt, fill: white)[NbN], anchor: "center")
  set-style(stroke: (paint: nbn_c, thickness: 0.7pt))
  line((2.0, 1.2), (2.0, 1.7), mark: (end: ">", size: .12))
  content((2.0, 1.95), text(size: 25pt, fill: nbn_c)[bridge], anchor: "center")
  content((3.5, 3.5), text(size: 25pt, fill: pink)[resist removed], anchor: "east")

})

// ─── Poster layout ────────────────────────────────────────────────────────────

// ── Header ──
#grid(
  columns: (1.2fr, 5.7fr, 1.2fr),
  gutter: 9mm,
  align(left + horizon)[#image("../researchproposal/ulgfsa_en.svg", width: 160mm)],
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

#v(3mm)

// ── Abstract ──
#block(
  width: 100%,
  fill: blue.lighten(88%),
  stroke: (paint: blue, thickness: 1.5pt),
  radius: 6pt,
  inset: (x: 75pt, top: 12pt, bottom: 20pt),
)[
  #align(center)[
    #text(size: 38pt, weight: "bold", fill: blue)[Abstract]
  ]
  #v(6pt)
  #text(size: 28pt, fill: dark)[
    NbN thin films are a key material for superconducting nanowire single-photon detectors (SNSPDs) and quantum circuits, with $T_c$ up to 17.3~K [1]. In reactive RF magnetron sputtering, the N#sub[2] partial pressure $P_(N_2)$ governs stoichiometry across three structural zones (Kalal et al. 2021). Here, 50 nm NbN films are deposited on Si substrates at varied $P_(N_2)$ (2.5–15 %) and their resistive transitions measured by 4-point transport. This work identifies the optimal $P_(N_2)$ for maximum reproducible $T_c$ and characterises the effect of EBL micro-patterning on finite-width NbN bridges.
  ]
]

#v(3mm)

// ══════════════════════════════════════════════════════════════════════════════
// 2-COLUMN LAYOUT
// Left = Introduction, Methods, RF process & growth  |  Right = SC physics + bridges
// ══════════════════════════════════════════════════════════════════════════════
#grid(
  columns: (1fr, 1fr),
  gutter: 14mm,

  // ══ LEFT ══════════════════════════════════════════════════════════════════
  [
    #panel([1. Introduction])[
      #set par(leading: 0.85em)
      #v(4pt)
      - NbN: *Type II superconductor*, $T_c$ up to 17.3~K (Keskar 1971).
      #v(4pt)
      - $T_c$ tuned by the nitrogen gas fraction: #text(size: 24pt, fill: dark)[$P_(N_2)$ [%] = 100 × N#sub[2] / total gas flow]
      #v(6pt)
      - Three crystalline structure R#sub[I/II/III] give distinct $T_c$ (Kalal et al. 2021)
      #v(6pt)
      - *Goal 1:* find optimal $P_(N_2)$ for highest reproducible $T_c$
      #v(6pt)
      - *Goal 2:* verify EBL-patterned bridges remain superconducting after micro-patterning
      #v(4pt)
    ]
    #v(3mm)
    #panel([2. Methods])[
      #v(4pt)
      #tag(blue)[Deposition] 50 nm NbN deposited by reactive RF magnetron sputtering (210 W, $10^(-8)$ Torr, 20 sccm), $P_(N_2)$ varied 2.5–15 %
      #v(7pt)
      #tag(violet)[Transport] 4-point $R(T)$ in cryostat, $T_c$ = midpoint of resistive transition (max $|"dR"/"dT"|$), onset (90 %) and offset (10 %) are two alternative thresholds
      #v(7pt)
      #tag(pink)[EBL] PMMA/co-PMMA bilayer patterned by e-beam lithography (Raith Pioneer Two), NbN deposited and lifted off → bridges 10 and 20 µm.
      #v(4pt)
    ]
    #v(3mm)
    // ── RF Sputtering ──
    #panel([3. Reactive RF Sputtering])[
      #align(center)[#draw_sputtering]
    ]
    #v(3mm)
    // ── Row 3: Deposition Rate — text left, plot right ──
    #panel([4. Deposition Rate vs $P_(N_2)$])[
      #grid(
        columns: (1fr, 2fr),
        gutter: 6mm,
        align(horizon)[
          #text(size: 25pt, fill: muted)[
            - Higher $P_(N_2)$ dilutes Ar in the plasma.
            #v(8mm)
            - Lower Ar#super[+] density reduces target bombardment.
            #v(8mm)
            - Fewer sputtering events decrease the deposition rate.
          ]
        ],
        align(center + horizon)[#image("../plot/deposition_rate_n2_fraction.pdf", width: 100%)],
      )
    ]
    #v(3mm)
    // ── Row 4: Tc vs PN2 — plot left, text right ──
    #panel([5. $T_c$ vs $P_(N_2)$: Growth results])[
      #grid(
        columns: (1.6fr, 1fr),
        gutter: 6mm,
        // Left: Tc vs PN2 plot only
        align(center + horizon)[#image("../plot/tc_vs_n2_fraction.pdf", width: 100%)],
        // Right: bullets, then 2×2 crystal images below
        [
          #text(size: 25pt, fill: muted)[
            - Peak at $P_(N_2)=10%$ in zone *R#sub[II]* (δ-NbN, cubic rock-salt).
            #v(3mm)
            - Zone R#sub[I] is nitrogen-poor, zone R#sub[III] is over-nitrided, both lowering $T_c$.
            #v(3mm)
            - Error bars span 90 % to 10 % thresholds. Trend agrees with Kalal et al. 2021.
          ]
          #v(3mm)
          #grid(
            columns: (1fr, 1fr, 1fr, 1fr),
            gutter: (2mm, 3pt),
            align(center)[#image("../molecule3d_split_pure_nb_4x.png", height: 37mm)],
            align(center)[#image("../molecule3d_split_r1_4x.png",      height: 37mm)],
            align(center)[#image("../molecule3d_split_r2_4x.png",      height: 37mm)],
            align(center)[#image("../molecule3d_split_r3_4x.png",      height: 37mm)],
            align(center)[#caption([Nb])],
            align(center)[#caption([β-Nb#sub[2]N])],
            align(center)[#caption([δ-NbN])],
            align(center)[#caption([ε-NbN])],
          )
          #v(2mm)
          #align(center)[#image("../molecule3d_split_legend_nb_n_4x.png", width: 40%)]
          #v(3mm)
          #caption([Crystal structures from Kalal et al. *[3]* (rendered and upscaled).])
        ],
      )
    ]
  ],

  // ══ RIGHT — SC physics, bridge fabrication, results ═══════════════════════
  [
    // ── Row 1: SC field diagram ──
    #panel([6. Superconducting Transition: Type I vs Type II])[
      #align(center)[#image("../plot/sc_field_diagram.pdf", width: 90%)]
      #caption([
        *Type I* (Pb): Meissner, $B=0$ inside. \
        *Type II* (NbN): vortex lattice above $H_(c 1)$, $R=0$ until $H_(c 2)$. \
        *Normal* ($T>T_c$): B passes through. 
      ])
    ]
    #v(3mm)
    // ── Row 2: R(T) plot | EBL diagram in one shared block ──
    #panel([7. R(T): Plain Film \& Bridges])[
      #grid(
        columns: (1fr, 1fr),
        gutter: 7mm,
        [
          #align(center)[#image("../plot/transition_and_bridge.pdf", width: 98%)]
          #v(4pt)
          #set list(indent: 4pt, body-indent: 6pt)
          - 4-point geometry: current injected at outer contacts, voltage sensed at inner contacts (contact resistance eliminated)
        ],
        [
          #align(center)[#draw_ebl]
          #v(4pt)
          #set list(indent: 4pt, body-indent: 6pt)
          - PMMA/co-PMMA bilayer deposited by *spin coating* prior to e-beam exposure
        ],
      )
    ]
    #v(3mm)
    // ── Row 3: Finite-Width Benchmark — plot aside, table + schematics in main column ──
    #panel([8. Finite-Width Benchmark])[
      #grid(
        columns: (1.5fr, 1fr),
        gutter: 7mm,
        align(horizon)[
          #align(center)[#image("../plot/bridge_tc_reference.pdf", width: 100%)]
        ],
        [
          #align(center)[
            #table(
              columns: (auto, auto),
              stroke: (paint: border, thickness: 0.6pt),
              inset: 4pt,
              align: center,
              table.header[*W*][$T_c$],
              [10 µm], [~8.1 K],
              [20 µm], [~8.0 K],
              [∞ (plain film)], [10.99 K],
            )
          ]
          #v(3mm)
          #grid(
            columns: (1fr, 1fr),
            gutter: 7mm,
            [
              #align(center)[#image("images/gds_C1.png", height: 75mm)]
              #align(center)[#caption([W = 10 µm])]
            ],
            [
              #align(center)[#image("images/gds_D1.png", height: 75mm)]
              #align(center)[#caption([W = 20 µm])]
            ],
          )
          #align(center)[#caption([Bridge schematic])]
        ],
      )
    ]
    #v(3mm)
    // ── Row 4: Conclusions (full width) ──
    #panel([Conclusions])[
      #set par(leading: 0.72em)
      #text(size: 25pt)[$P_(N_2) approx 10%$ yields optimal $T_c = 10.99$ K (zone R#sub[II], δ-NbN).]
      #v(6pt)
      #text(size: 25pt)[EBL micro-patterning preserves superconductivity: both bridges remain superconducting with a width-independent $Delta T_c approx 3$ K. The coherence length of NbN is a few nm, so a 10 µm bridge introduces no geometric confinement: the $Delta T_c$ is instead attributed to resist outgassing during NbN deposition.]
    ]
    #v(3mm)
    // ── Row 5: Ack, Data, References stacked ──
    #block(
      width: 100%,
      fill: amber.lighten(88%),
      stroke: (paint: amber.lighten(55%), thickness: 0.7pt),
      radius: 4pt,
      inset: (x: 11pt, y: 10pt),
    )[
      #text(size: 25pt, fill: dark)[
        *Acknowledgements:* *Cyril Delforge* and *Abhishek Naik* provided daily supervision and prepared several NbN samples. *Julia Baumgarten* contributed the bridge transport measurements and $T_c$ vs $P_(N_2)$ data points. *Nicolas Lejeune* retrieved additional $T_c$ measurements.
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
      #text(size: 25pt, fill: muted)[Data \& code: #text(fill: blue)[*github.com/Aerozine/ning*]]
    ]
    #v(2mm)
    #panel([References])[
      #text(size: 25pt, fill: muted)[
        *[1]* Keskar et al., _Jpn. J. Appl. Phys._ *10* (1971) #linebreak()
        *[2]* Sugimoto & Motohiro, _Vacuum_ *93* (2013) #linebreak()
        *[3]* Kalal et al., _J. Alloys Compd._ *851* (2021) #linebreak()
        *[4]* Glowacka et al., _arXiv:1401.2276_ (2014) #linebreak()
        *[5]* Gavaler et al., _Physica_ *55* (1971)
      ]
      #v(-4pt)
    ]
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
