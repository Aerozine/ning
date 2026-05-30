#!/usr/bin/env python3
"""Split-panel 3D Matplotlib render for the Nb/N/Ni molecule views.

The nitride panels use explicit 3D coordinates: a square front lattice in x/z,
a shallow y-depth layer, and half-colored cylindrical bonds.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.patches import FancyArrowPatch


ROOT = Path(__file__).resolve().parent
NITRIDE_BACK_Y = 0.42
NITRIDE_MID_Y = NITRIDE_BACK_Y * 0.5

COLORS = {
    "blue": "#3D7FD8",
    "violet": "#8B63D9",
    "pink": "#E84D8A",
    "grey": "#737985",
    "dark": "#27323C",
    "muted": "#59616F",
    "light": "#FFFFFF",
    "border": "#E1DFE8",
    "amber": "#E8830A",
}

ELEMENT = {
    "Nb": COLORS["blue"],
    "N": COLORS["violet"],
    "Ni": COLORS["pink"],
}

RADII = {
    "Nb": 0.135,
    "N": 0.056,
    "Ni": 0.073,
}


def rgb(color: str | tuple[float, float, float] | np.ndarray) -> np.ndarray:
    return np.array(mcolors.to_rgb(color), dtype=float)


def mix(c1: str | tuple[float, float, float] | np.ndarray, c2: str | tuple[float, float, float], t: float) -> tuple[float, float, float]:
    a = rgb(c1)
    b = rgb(c2)
    return tuple(a * (1 - t) + b * t)


def fade(color: str | tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    return mix(color, COLORS["light"], amount)


def darken(color: str | tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    return mix(color, "#000000", amount)


def normalize(v: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(v))
    if norm == 0:
        return v
    return v / norm


LIGHT = normalize(np.array([-0.55, -0.38, 0.92]))
VIEW_LIGHT = normalize(np.array([-0.45, -0.30, 1.0]))


def shaded(base_color: str | tuple[float, float, float], normals: np.ndarray) -> np.ndarray:
    base = rgb(base_color)
    diffuse = np.clip(normals @ LIGHT, 0, 1)
    spec = np.clip(normals @ VIEW_LIGHT, 0, 1) ** 28
    colors = base * (0.48 + 0.48 * diffuse[..., None]) + spec[..., None] * 0.10
    colors = np.clip(colors, 0, 1)
    return np.dstack((colors, np.ones(diffuse.shape)))


def sphere(ax, center, radius: float, color, resolution: int = 44) -> None:
    center = np.array(center, dtype=float)
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution // 2)
    uu, vv = np.meshgrid(u, v)
    nx = np.cos(uu) * np.sin(vv)
    ny = np.sin(uu) * np.sin(vv)
    nz = np.cos(vv)
    normals = np.dstack((nx, ny, nz))
    x = center[0] + radius * nx
    y = center[1] + radius * ny
    z = center[2] + radius * nz
    ax.plot_surface(
        x,
        y,
        z,
        facecolors=shaded(color, normals),
        linewidth=0,
        antialiased=True,
        shade=False,
        rcount=resolution // 2,
        ccount=resolution,
    )


def cylinder_mesh(p0, p1, radius: float, resolution: int = 40, segments: int = 10):
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    axis = p1 - p0
    length = float(np.linalg.norm(axis))
    if length <= 1e-9:
        return None
    w = axis / length
    helper = np.array([0.0, 0.0, 1.0])
    if abs(float(np.dot(w, helper))) > 0.92:
        helper = np.array([0.0, 1.0, 0.0])
    u = normalize(np.cross(w, helper))
    v = normalize(np.cross(w, u))
    theta = np.linspace(0, 2 * np.pi, resolution)
    t = np.linspace(0, length, segments + 1)
    tt, th = np.meshgrid(t, theta)
    normals = np.cos(th)[..., None] * u + np.sin(th)[..., None] * v
    pts = p0 + tt[..., None] * w + radius * normals
    return pts, normals, tt, length


def cylinder(ax, p0, p1, radius: float, color, resolution: int = 40) -> None:
    mesh = cylinder_mesh(p0, p1, radius, resolution)
    if mesh is None:
        return
    pts, normals, _tt, _length = mesh
    ax.plot_surface(
        pts[..., 0],
        pts[..., 1],
        pts[..., 2],
        facecolors=shaded(color, normals),
        linewidth=0,
        edgecolor="none",
        antialiased=True,
        shade=False,
        rstride=1,
        cstride=1,
    )


def bicolor_cylinder(ax, p0, p1, radius: float, color_a, color_b, resolution: int = 40) -> None:
    mesh = cylinder_mesh(p0, p1, radius, resolution)
    if mesh is None:
        return
    pts, normals, tt, length = mesh
    colors_a = shaded(color_a, normals)
    colors_b = shaded(color_b, normals)
    first_half = (tt <= length * 0.5)[..., None]
    facecolors = np.where(first_half, colors_a, colors_b)
    ax.plot_surface(
        pts[..., 0],
        pts[..., 1],
        pts[..., 2],
        facecolors=facecolors,
        linewidth=0,
        edgecolor="none",
        antialiased=True,
        shade=False,
        rstride=1,
        cstride=1,
    )


def trimmed(a, b, trim_a: float, trim_b: float) -> tuple[np.ndarray, np.ndarray]:
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    axis = b - a
    length = float(np.linalg.norm(axis))
    if length <= trim_a + trim_b:
        return a, b
    u = axis / length
    return a + u * trim_a, b - u * trim_b


def half_bond(
    ax,
    a,
    b,
    elem_a: str,
    elem_b: str,
    radius: float = 0.025,
    color_a=None,
    color_b=None,
    fade_amount: float = 0.0,
) -> None:
    ca = color_a if color_a is not None else ELEMENT[elem_a]
    cb = color_b if color_b is not None else ELEMENT[elem_b]
    ca = fade(ca, fade_amount) if fade_amount else ca
    cb = fade(cb, fade_amount) if fade_amount else cb
    p0, p1 = trimmed(a, b, RADII[elem_a] * 0.52, RADII[elem_b] * 0.52)
    bicolor_cylinder(ax, p0, p1, radius, ca, cb)


def mono_bond(ax, a, b, elem_a: str, elem_b: str, color, radius: float = 0.021, fade_amount: float = 0.0) -> None:
    c = fade(color, fade_amount) if fade_amount else color
    p0, p1 = trimmed(a, b, RADII[elem_a] * 0.52, RADII[elem_b] * 0.52)
    cylinder(ax, p0, p1, radius, c)


def unit_cell(ax, y_back: float = 0.28) -> None:
    corners = [
        (0, 0, 0),
        (1, 0, 0),
        (0, y_back, 0),
        (1, y_back, 0),
        (0, 0, 1),
        (1, 0, 1),
        (0, y_back, 1),
        (1, y_back, 1),
    ]
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7), (0, 2), (1, 3), (4, 6), (5, 7)]
    for i, j in edges:
        p, q = np.array(corners[i]), np.array(corners[j])
        ax.plot([p[0], q[0]], [p[1], q[1]], [p[2], q[2]], color=fade(COLORS["dark"], 0.35), lw=1.1)


def setup_ax(ax, azim: float = -78, elev: float = 0.0) -> None:
    ax.set_axis_off()
    ax.set_facecolor(COLORS["light"])
    ax.set_xlim(-0.16, 1.16)
    ax.set_ylim(-0.07, 0.52)
    ax.set_zlim(-0.14, 1.14)
    ax.set_box_aspect((1.0, 0.44, 1.0))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("ortho")


def draw_nb_lattice(ax, center: bool = True) -> None:
    yb = 0.28
    unit_cell(ax, yb)
    for p in [(0, yb, 0), (1, yb, 0), (0, yb, 1), (1, yb, 1)]:
        sphere(ax, p, RADII["Nb"], fade(ELEMENT["Nb"], 0.52), 40)
    if center:
        sphere(ax, (0.50, 0.14, 0.50), RADII["Nb"], ELEMENT["Nb"], 42)
    for p in [(0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1)]:
        sphere(ax, p, RADII["Nb"], ELEMENT["Nb"], 44)


def draw_pure(ax) -> None:
    draw_nb_lattice(ax, center=True)


def draw_r1(ax) -> None:
    draw_nb_lattice(ax, center=True)
    ni_atoms = [
        (0.18, -0.02, 0.28),
        (0.34, -0.01, 0.31),
        (0.84, -0.02, 0.33),
        (0.28, -0.03, 0.18),
    ]
    bonds = [
        ((0, 0, 0), ni_atoms[0], "Nb", "Ni"),
        ((0, 0, 0), ni_atoms[3], "Nb", "Ni"),
        ((0, 0, 1), ni_atoms[0], "Nb", "Ni"),
        ((0, 0.28, 1), ni_atoms[1], "Nb", "Ni"),
        ((1, 0, 0), ni_atoms[2], "Nb", "Ni"),
        ((1, 0.28, 1), ni_atoms[2], "Nb", "Ni"),
        (ni_atoms[0], ni_atoms[1], "Ni", "Ni"),
        (ni_atoms[3], ni_atoms[0], "Ni", "Ni"),
        (ni_atoms[3], ni_atoms[1], "Ni", "Ni"),
        (ni_atoms[1], (0.50, 0.14, 0.50), "Ni", "Nb"),
        (ni_atoms[2], (0.50, 0.14, 0.50), "Ni", "Nb"),
        (ni_atoms[1], (1, 0, 0), "Ni", "Nb"),
        (ni_atoms[0], ni_atoms[2], "Ni", "Ni"),
    ]
    for a, b, ea, eb in bonds:
        half_bond(ax, a, b, ea, eb, radius=0.023)
    for p in ni_atoms:
        sphere(ax, p, RADII["Ni"], ELEMENT["Ni"], 40)


def nitride_atoms(y: float) -> dict[str, tuple[float, float, float]]:
    return {
        "N_tl": (0.0, y, 1.0),
        "Nb_t": (0.5, y, 1.0),
        "N_tr": (1.0, y, 1.0),
        "Nb_l": (0.0, y, 0.5),
        "N_c": (0.5, y, 0.5),
        "Nb_r": (1.0, y, 0.5),
        "N_bl": (0.0, y, 0.0),
        "Nb_b": (0.5, y, 0.0),
        "N_br": (1.0, y, 0.0),
    }


NITRIDE_EDGES = [
    ("N_tl", "Nb_t"),
    ("Nb_t", "N_tr"),
    ("Nb_l", "N_c"),
    ("N_c", "Nb_r"),
    ("N_bl", "Nb_b"),
    ("Nb_b", "N_br"),
    ("N_tl", "Nb_l"),
    ("Nb_l", "N_bl"),
    ("Nb_t", "N_c"),
    ("N_c", "Nb_b"),
    ("N_tr", "Nb_r"),
    ("Nb_r", "N_br"),
]


def elem_for(name: str) -> str:
    return "N" if name.startswith("N_") else "Nb"


GRID_INDEX = {
    "N_tl": (0, 2),
    "Nb_t": (1, 2),
    "N_tr": (2, 2),
    "Nb_l": (0, 1),
    "N_c": (1, 1),
    "Nb_r": (2, 1),
    "N_bl": (0, 0),
    "Nb_b": (1, 0),
    "N_br": (2, 0),
}


def elem_at_grid(xi: int, yi: int, zi: int) -> str:
    return "N" if (xi + yi + zi) % 2 == 0 else "Nb"


def draw_nitride_layer(ax, atoms: dict[str, tuple[float, float, float]], *, back: bool = False) -> None:
    f = 0.46 if back else 0.0
    bond_r = 0.014 if back else 0.027
    for a, b in NITRIDE_EDGES:
        half_bond(ax, atoms[a], atoms[b], elem_for(a), elem_for(b), radius=bond_r, fade_amount=f)
    for name, p in atoms.items():
        elem = elem_for(name)
        amount = 0.46 if back else 0.0
        sphere(ax, p, RADII[elem], fade(ELEMENT[elem], amount), 36 if back else 44)


def draw_mid_layer(ax) -> None:
    mid = mid_sites()
    for a, b in NITRIDE_EDGES:
        pa, ea = mid[a]
        pb, eb = mid[b]
        half_bond(ax, pa, pb, ea, eb, radius=0.014, fade_amount=0.34)
    for name, (p, elem) in mid_sites().items():
        # N sites directly behind foreground Nb sites are part of the depth
        # chain, but they are occluded in the reference projection.
        if elem == "N" and elem_for(name) == "Nb":
            continue
        sphere(ax, p, RADII[elem], fade(ELEMENT[elem], 0.34), 40)


def mid_sites() -> dict[str, tuple[tuple[float, float, float], str]]:
    return {
        name: ((xi / 2, NITRIDE_MID_Y, zi / 2), elem_at_grid(xi, 1, zi))
        for name, (xi, zi) in GRID_INDEX.items()
    }


def draw_depth_bonds(ax, front: dict[str, tuple[float, float, float]], back: dict[str, tuple[float, float, float]]) -> None:
    mid = mid_sites()
    for name, (mid_pos, mid_elem) in mid.items():
        if name == "N_c":
            continue
        elem = elem_for(name)
        half_bond(ax, front[name], mid_pos, elem, mid_elem, radius=0.013, fade_amount=0.42)
        half_bond(ax, mid_pos, back[name], mid_elem, elem, radius=0.013, fade_amount=0.42)


def draw_nitride(ax, defect: bool = False) -> None:
    front = nitride_atoms(0.0)
    back = nitride_atoms(NITRIDE_BACK_Y)

    draw_nitride_layer(ax, back, back=True)
    draw_depth_bonds(ax, front, back)
    draw_mid_layer(ax)
    draw_nitride_layer(ax, front, back=False)

    if defect:
        ni = (0.38, -0.035, 0.30)
        defect_targets = ["Nb_l", "N_bl", "N_c", "Nb_b"]
        for target in defect_targets:
            half_bond(ax, ni, front[target], "Ni", elem_for(target), radius=0.025)
        sphere(ax, ni, RADII["Ni"], ELEMENT["Ni"], 44)


def title_r(fig, roman: str) -> None:
    fig.text(0.50, 0.995, "R", fontsize=46, ha="center", va="top", color=COLORS["dark"], family="DejaVu Sans")
    fig.text(0.62, 0.850, roman, fontsize=30, ha="left", va="top", color=COLORS["dark"], family="DejaVu Sans")
    for x1, x2, style in [(0.10, 0.38, "<-"), (0.62, 0.90, "->")]:
        fig.patches.append(
            FancyArrowPatch(
                (x1, 0.905),
                (x2, 0.905),
                transform=fig.transFigure,
                arrowstyle=style,
                mutation_scale=18,
                linewidth=2.5,
                color=COLORS["dark"],
            )
        )


def title_pure(fig) -> None:
    fig.text(0.50, 0.970, "Pure Nb", fontsize=30, ha="center", va="top", color=COLORS["dark"], family="DejaVu Sans")


def save_3d_panel(name: str, title: str, draw_fn, *, width_px: int = 245) -> None:
    fig = plt.figure(figsize=(width_px / 100, 2.39), dpi=100)
    fig.patch.set_facecolor(COLORS["light"])
    if title == "Pure Nb":
        title_pure(fig)
    else:
        title_r(fig, title)

    ax = fig.add_axes([-0.02, -0.015, 1.04, 0.815], projection="3d")
    setup_ax(ax)
    draw_fn(ax)

    stem = ROOT / f"molecule3d_split_{name}"
    fig.savefig(f"{stem}.png", dpi=100, facecolor=COLORS["light"])
    fig.savefig(f"{stem}_4x.png", dpi=400, facecolor=COLORS["light"])
    fig.savefig(f"{stem}.pdf", facecolor=COLORS["light"])
    plt.close(fig)


def legend_sphere(ax, x: float, y: float, r: float, color: str) -> None:
    ax.add_patch(patches.Circle((x + r * 0.10, y + r * 0.10), r * 1.03, facecolor=fade(COLORS["dark"], 0.82), edgecolor="none"))
    ax.add_patch(patches.Circle((x, y), r, facecolor=darken(color, 0.36), edgecolor=darken(color, 0.60), linewidth=2))
    for i in range(18, 0, -1):
        frac = i / 18
        rr = r * 0.92 * frac
        t = 1 - frac
        cx = x - r * 0.15 * t
        cy = y - r * 0.18 * t
        ax.add_patch(patches.Circle((cx, cy), rr, facecolor=mix(darken(color, 0.18), fade(color, 0.18), t), edgecolor="none"))


def save_legend() -> None:
    fig = plt.figure(figsize=(1.45, 1.10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 145)
    ax.set_ylim(110, 0)
    ax.set_axis_off()
    fig.patch.set_facecolor(COLORS["light"])
    ax.set_facecolor(COLORS["light"])
    legend_sphere(ax, 25, 24, 14, ELEMENT["Nb"])
    ax.text(51, 30, "Nb", fontsize=20, va="center", color=COLORS["dark"], family="DejaVu Sans")
    legend_sphere(ax, 25, 60, 11, ELEMENT["N"])
    ax.text(51, 66, "N", fontsize=20, va="center", color=COLORS["dark"], family="DejaVu Sans")
    legend_sphere(ax, 25, 92, 12, ELEMENT["Ni"])
    ax.text(51, 98, "N", fontsize=20, va="center", color=COLORS["dark"], family="DejaVu Sans")
    stem = ROOT / "molecule3d_split_legend_nb_n"
    fig.savefig(f"{stem}.png", dpi=100, facecolor=COLORS["light"])
    fig.savefig(f"{stem}_4x.png", dpi=400, facecolor=COLORS["light"])
    fig.savefig(f"{stem}.pdf", facecolor=COLORS["light"])
    plt.close(fig)


def build() -> None:
    save_3d_panel("pure_nb", "Pure Nb", draw_pure, width_px=210)
    save_3d_panel("r1", "I", draw_r1, width_px=225)
    save_3d_panel("r2", "II", lambda ax: draw_nitride(ax, defect=False), width_px=245)
    save_3d_panel("r3", "III", lambda ax: draw_nitride(ax, defect=True), width_px=245)
    save_legend()


if __name__ == "__main__":
    build()
    print("Wrote molecule3d_split_pure_nb/r1/r2/r3 and molecule3d_split_legend_nb_n as PNG, 4x PNG, and PDF.")
