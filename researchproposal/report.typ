//#import "@preview/red-agora:0.1.2": project
#import "@preview/subpar:0.2.2"
#import "lib.typ": project
#import "@preview/dashy-todo:0.1.3": todo
#import "@preview/wrap-it:0.1.1": *
#import "@preview/gantty:0.5.1": gantt
#set text(font: "xits")
#set cite(style: "ieee")
#show: project.with(
  title: "Growth Optimization of Superconducting NbN for Hybrid Thin Film Structures",
  subtitle: "APRI0006 - Experimental project",
  authors: (
    "Loïc Delbarre",
    "S215072"
  ),
  school-logo: image("ulgfsa.svg"), // Replace with [] to remove the school logo
  company-logo: image("epnm.png"),
  mentors: (
    "Cyril Delforge",
    "Abhishek Naik"
  ),
  mentorname:"Daily supervisors",
  jury: (
    "Alejandro V. Silhanek",
  ),
  juryname:"Advisor",
  branch: "Engineering physics",
  academic-year: "2025-2026",
  tof: false,
  tot: false,
  toc:false,
  footer-text: "Research proposal" // Text used in left side of the footer
)

#set par(justify: true)
#set page(paper: "a4")

#let tc = $T_c$
#let pn = $P_N_2$

#set text(size: 12pt)
//TODO 
/*
*include all paper value inside the same graph for Tc  
* explain Tc definition according differents authors 
* cite more 
* reread all tomorow
*
* 
*
*/
//
#v(-.5em)
=== State of the art
 Niobium Nitride (NbN) thin films have been extensively studied due to their inherent superconducting properties (type II) and high transition temperature (#tc) for for example superconducting resonators. NbN thin films prepared via reactive sputtering have demonstrated a higher bound for #tc of 17.3 K, as reported by Keskar et al. @KESKAR71. Notably, the #tc of NbN exceeds that of pure niobium, which has a #tc of approximately 8 K @SUGIMOTO .
//The superconducting properties of NbN are strongly influenced by the nitridation process.
As shown by Kalal et al. @KALAL, the nitrogen partial pressure (#pn) relative to the total pressure of nitrogen and argon during deposition plays a crucial role in determining the material's properties. Their work identifies an optimal nitrogen partial pressure of around 8%, which results in the best superconducting performance.
#v(-.5em)
=== Goals
Develop a reliable NbN thin-film deposition process for the ULiège Nanofabrication Platform, targeting the highest achievable #tc within the practical limits set by Nb’s intrinsic #tc. . The growth parameters to be examined include film thickness, the base pressure of the deposition chamber, the nitrogen gas fraction, the plasma pressure, and the deposition rate.The quality of the fabricated films will be evaluated using electrical 2-point cryogenic transport measurements
/*=== Methodology
The initial experiments were performed using a radio-frequency (RF) magnetron sputtering system (@rfms). A 13.56 MHz RF signal generates a plasma, which is confined near the target by concentric magnets. Ionized Ar particles bombard the Nb target, sputtering Nb clusters that disperse toward the substrate. Because the sputtering head is tilted, the substrate is rotated during deposition to ensure uniform film thickness and reduce anisotropic growth.

In this configuration, the deposition rate is monitored using a quartz crystal microbalance placed in the vicinity of the sputtering head.
This device uses a piezoelectric crystal whose resonance frequency decreases proportionally to the mass deposited on its surface, allowing the deposition rate to be inferred from the time-dependent frequency shift.
*/
#v(-.5em)
=== Preliminary Results
A 50 nm NbN film was deposited under high vacuum ($10^(–8)$ Torr) at 210 W RF power with a fixed total gas flow of 20 standard cubic centimeter per minute (sccm) with the setup described at @rfms. The deposition rate and #tc are reported as functions of the N₂ partial pressure (cf @deposition and @pn). #tc is extracted from $R(T)$ curves as show in @onset using the 10% onset criterion, with uncertainties defined by the 10–90% transition width.
The data show two distinct trends. First, the deposition rate monotonically decreases with increasing $N_2$ fraction, consistent with target poisoning that lowers the sputtering yield. Second, the superconducting transition temperature #tc exhibits a maximum at an intermediate $N_2$ level. This peak arises from a balance between introducing sufficient nitrogen to form the desired Nb–N phase and avoiding over-nitridation, which degrades film quality.
//As expected, the deposition rate decreases with increasing N₂ fraction due to target poisoning, which reduces the sputtering yield. In contrast, #tc peaks at an intermediate N₂ level, reflecting the trade-off between adequate nitrogen incorporation and degradation caused by over-nitridation.
These results underscore the importance of precise nitrogen-flow optimization for maximizing #tc, and the observed trends agree qualitatively with previous reports on NbN stoichiometry effects @GLOWACKA.
//These results confirm the reliability of our setup and highlight the need for precise nitrogen flow optimization to maximize #tc. The observed trends agree qualitatively with previous reports on NbN stoichiometry effects @GLOWACKA.
Although the deposition conditions used by Kalal et al. differ mostly in film thickness and the use of a higher-power DC sputtering system, their data also show an optimal N₂ partial pressure and then a decrease. Despite our system’s limitations, we therefore expect a similar peak of performance.

/*Using RF magnetron sputtering under high vacuum (~$10^(–8)$  Torr), we grew 50 nm NbN films at 210 W RF power
with a constant total gas flow of 20 sccm (standard cubic centimeter per minute). 
The measured deposition rate and #tc for these films are presented as functions of the N₂ partial pressure @deposition,@pn .
#tc is defined from the $R(T)$ curves @onset as the 10% onset of the superconducting transition, with the uncertainty taken as the difference between the 10% and 90% criteria.

The data reveal a clear trend: the deposition rate decreases with increasing $N_2$ fraction. This behavior arises from target poisoning, which lowers the sputtering yield as more nitrogen reacts with the target surface. In contrast, the #tc reaches a maximum at an intermediate $N_2$ level, reflecting the balance between sufficient nitrogen incorporation and the onset of over-nitridation, which degrades film quality.

These preliminary findings validate our experimental setup and indicate the importance of fine-tuning
nitrogen content to maximize #tc. Such behavior is qualitatively consistent with prior reports on nitrogen concentration effects in NbN films, 
supporting the planned optimization strategy @GLOWACKA .

Although the deposition conditions reported by Kalal et al. differ from ours particularly regarding film thickness and the use of a more powerful DC magnetron sputtering system their results similarly indicate the presence of an optimal $N_2$ partial pressure. Despite the limitations of our setup, a comparable peak in performance is therefore expected.
*/

#v(-.5em)
=== Research Plan
The plan is shown in the Gantt diagram @gantt.
- Fabrication of additional NbN films under optimal #pn conditions to evaluate reproducibility. The highest #tc recipe will be selected for next steps.
- Spin-coat the pristine substrate with PMMA (Poly(methyl methacrylate)) and co-PMMA resist layers, and pattern nanowires stripes of various widths using the Raith Pioneer Two electron-beam lithography system.
- NbN Deposition and Lift‑Off: Deposit NbN onto the patterned substrate. Carry out lift‑off to form nanowires stripes with controlled geometries.
- Structural and Electrical Characterization: Assess the impact of progressive lateral size reduction by measuring #tc for nanowires stripes of different widths, thereby quantifying geometric effects on superconductivity. Complement these measurements with SEM imaging to evaluate the morphology and grain structure of the patterned stripes.

#pagebreak()
=== Figures

#subpar.grid(
//DCBA 
  //

figure(
  image("rf",width:60%),
  caption:[Radio-Frequency (RF) (13.56MHz) magnetron sputtering taken from @RATZ:
  Because the sputtering head is tilted, the substrate is rotated during deposition to ensure uniform film thickness and reduce anisotropic growth.
The deposition rate is monitored using a quartz crystal microbalance placed in the vicinity of the sputtering head.
This device uses a piezoelectric crystal whose resonance frequency decreases proportionally to the mass deposited on its surface, allowing the deposition rate to be inferred from the time-dependent frequency shift.
],
),<rfms> ,


figure(
  image("../plot/deposition_rate_n2_fraction.pdf",width:100%),
  caption:[Deposition rate as a function of partial pressure of $N_2$ for a total 
flow rate of 20 sccm, power at 210 W and 50 nm thickness ]
),<deposition>,

figure(
  image("../plot/tc_vs_n2_fraction.pdf",width:110%),
  caption:[#tc as a function of partial pressure of N for a total 
flow rate of 20 sccm , power at 210 W and 50 nm  
thickness.]
),<pn>,

figure(
  image("../plot/best_transition_ning11.pdf",width:120%),
  caption:[ Method used for computing #tc with 10% onset and the associated error for the actual highest #tc sample. ]
),<onset>,

columns: (1fr, 1fr)
)
#pagebreak()
#figure(
  caption: [Gantt chart describing the estimated time required for each step.],
  gantt(yaml("gantt.yaml"))
)<gantt>
#bibliography("bib.bib",style:	"ieee")
