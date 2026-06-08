"""Plot style helpers for the NbN project."""

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / f"matplotlib-{os.getuid()}"))

import matplotlib.pyplot as plt
from cycler import cycler

PALETTE = {
    "blue": "#3D7FD8",
    "green": "#8B63D9",
    "purple": "#E84D8A",
    "orange": "#737985",
    "grey": "#737985",
    "pink": "#F5A9C9",
}

COLORS = [
    PALETTE["blue"],
    PALETTE["green"],
    PALETTE["purple"],
    PALETTE["grey"],
]


def apply_style():
    plt.rcParams.update({
        "mathtext.fontset": "cm",
        "figure.figsize": (9.5, 6.0),
        "figure.dpi": 130,
        "savefig.dpi": 400,
        "savefig.bbox": "tight",
        "font.size": 18,
        "axes.labelsize": 24,
        "axes.titlesize": 25,
        "legend.fontsize": 20,
        "xtick.labelsize": 19,
        "ytick.labelsize": 19,
        "axes.linewidth": 1.5,
        "lines.linewidth": 2.8,
        "lines.markersize": 6.0,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.major.size": 6,
        "ytick.major.size": 6,
        "xtick.minor.size": 3,
        "ytick.minor.size": 3,
        "xtick.major.width": 1.1,
        "ytick.major.width": 1.1,
        "xtick.minor.width": 0.9,
        "ytick.minor.width": 0.9,
        "legend.frameon": True,
        "legend.framealpha": 1.0,
        "legend.edgecolor": "black",
        "axes.prop_cycle": cycler(color=COLORS),
    })


apply_style()


def style_ax(ax, xlabel="", ylabel="", title="", grid=False, minorticks=True):
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if grid:
        ax.grid(True, which="major", linestyle="--", linewidth=0.8, alpha=0.55)
        ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.35)
    if minorticks:
        ax.minorticks_on()


def add_hline(ax, y, label=None, color="black", linestyle="--", linewidth=1.5):
    ax.axhline(
        y,
        linestyle=linestyle,
        linewidth=linewidth,
        color=color,
        label="_nolegend_" if label is None else label,
        zorder=1,
    )


def style_legend(ax, title=None, loc="best", many_threshold=3, max_columns=3, **kwargs):
    handles, labels = ax.get_legend_handles_labels()
    visible_labels = [
        label for label in labels
        if label and not str(label).startswith("_")
    ]
    if not visible_labels:
        return None

    if len(visible_labels) >= many_threshold:
        ncol = min(max_columns, len(visible_labels))
        return ax.legend(
            title=title,
            loc="lower left",
            bbox_to_anchor=(0, 1, 1, 0),
            mode="expand",
            ncol=ncol,
            borderaxespad=0.0,
            **kwargs,
        )

    return ax.legend(title=title, loc=loc, **kwargs)


def finalize(fig, save_path=None, show=True):
    fig.tight_layout()
    if save_path:
        base = str(save_path).replace(".pdf", "").replace(".png", "")
        fig.savefig(base + ".pdf")
        fig.savefig(base + ".png")
        print(f"  Saved: {base}.pdf / .png")
    if show and "agg" not in plt.get_backend().lower():
        plt.show()
