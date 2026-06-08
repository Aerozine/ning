#!/usr/bin/env python3
"""Post-process NbN transport data and regenerate project figures."""

from __future__ import annotations

import csv
import math
import multiprocessing as mp
import re
import struct
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from utilsStyle import PALETTE, add_hline, finalize, style_ax, style_legend
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "postpro" / "data"
PLAIN_FILM_DIR = DATA_ROOT / "plain_films"
DISCORD_DIR = DATA_ROOT / "discord"
METADATA_DIR = DATA_ROOT / "metadata"
MICROSCOPY_DIR = DATA_ROOT / "microscopy"
PROCESSED_DIR = ROOT / "postpro" / "processed"
PLOT_DIR = ROOT / "plot"
POSTER_IMAGE_DIR = ROOT / "poster" / "images"
GDS_LAYOUT = DISCORD_DIR / "Transport_BridgesV3.gds"

TC_LEVELS = (0.10, 0.50, 0.90)
DEVICE_WIDTH_UM = {"C1": 10.0, "D1": 20.0}
MICROSCOPY_ROTATION_DEG = 90
MICROSCOPY_TRANSFORMS = {
    "2838_20x_2": {
        "rotation_deg": -90,
        "mirror_horizontal": True,
        "deskew_deg": 0.8,
    },
    "2838_50x_3": {
        "rotation_deg": 90,
        "deskew_deg": -1.0,
    },
    "2838_5x_5": {
        "rotation_deg": -90,
        "mirror_horizontal": True,
        "deskew_deg": -2.7,
    },
    "2838_5x_7": {
        "rotation_deg": -90,
        "mirror_horizontal": True,
        "deskew_deg": -2.7,
    },
}
DEFAULT_FILM_THICKNESS_NM = 50.0

# Gavaler et al. report ~15.2 K for thick NbN films and ~6.5 K at 25 Å.
# Combined with the Simonin thin-film form, this gives a simple thickness-only
# reference curve; it is not a fit to the present process.
GAVALER_TC_INF_K = 15.2
GAVALER_THIN_THICKNESS_NM = 2.5
GAVALER_THIN_TC_K = 6.5
GAVALER_DC_NM = GAVALER_THIN_THICKNESS_NM * (
    1.0 - GAVALER_THIN_TC_K / GAVALER_TC_INF_K
)

METADATA_CORRECTIONS = {
    9: {
        "ar_sccm": 17.25,
        "n2_sccm": 2.75,
        "pn_percent": 13.75,
        "metadata_note": (
            "P_N2 corrected to 13.75% from the refined plot; copied metadata "
            "previously duplicated NING-6 at 12.5%."
        ),
    },
}

LITERATURE_TC = {
    "Kalal et al.": {
        "pn": np.array([0.5, 4.0, 8.0, 16.0, 20.0]),
        "tc": np.array([2.55, 9.39, 12.24, 12.83, 7.91]),
        "color": PALETTE["orange"],
    },
    "Sugimoto et al.": {
        "pn": np.array([4.0, 6.0, 8.0, 10.0, 12.0, 14.0]),
        "tc": np.array([6.1, 10.2, 12.4, 13.6, 13.6, 13.2]),
        "color": PALETTE["green"],
    },
}


@dataclass
class Measurement:
    path: Path
    label: str
    kind: str
    current_a: float | None
    data: np.ndarray

    @property
    def temperature(self) -> np.ndarray:
        return self.data[:, 3]

    @property
    def voltage(self) -> np.ndarray:
        return self.data[:, 4]


def ensure_directories() -> None:
    for directory in (PROCESSED_DIR, PLOT_DIR, POSTER_IMAGE_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def decode_header(path: Path) -> str:
    header = []
    with path.open("rb") as handle:
        for raw_line in handle:
            if not raw_line.startswith(b"#"):
                break
            header.append(raw_line.decode("latin1", errors="replace"))
    return "".join(header)


def parse_current(header: str) -> float | None:
    match = re.search(r"sourcing\s+([0-9.]+)\s*([^\s]+)", header, flags=re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).replace("\xb5", "u").replace("\ufffd", "u").lower()
    if unit.startswith("ma"):
        return value * 1e-3
    if unit.startswith("ua"):
        return value * 1e-6
    if unit.startswith("a"):
        return value
    return None


def parse_kind(header: str) -> str:
    match = re.search(r"#\s*([24]pts)", header, flags=re.IGNORECASE)
    return match.group(1).lower() if match else "unknown"


def load_measurement(path: Path) -> Measurement:
    header = decode_header(path)
    data = np.genfromtxt(path, comments="#", encoding="latin1")
    if data.ndim != 2 or data.shape[1] < 5:
        raise ValueError(f"Unexpected measurement format in {path}")
    return Measurement(
        path=path,
        label=path.stem,
        kind=parse_kind(header),
        current_a=parse_current(header),
        data=data[:, :5],
    )


def sample_number(path: Path) -> int | None:
    match = re.search(r"NING[-_]?0*([0-9]+)", path.stem, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def device_label(path: Path) -> str | None:
    match = re.match(r"([A-Z][0-9]+)", path.stem)
    return match.group(1) if match else None


def clean_float(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text or text.lower() in {"none", "nan"}:
        return None
    match = re.match(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", text)
    if not match:
        return None
    return float(match.group(0))


def load_deposition_metadata() -> dict[int, dict[str, float | str]]:
    metadata: dict[int, dict[str, float | str]] = {}

    sample_csv = PLAIN_FILM_DIR / "sample.csv"
    if sample_csv.exists():
        rows = np.genfromtxt(sample_csv, comments="#", delimiter=";")
        if rows.ndim == 1:
            rows = rows.reshape(1, -1)
        for row in rows:
            ar_flow = float(row[1])
            n2_flow = float(row[2])
            total_flow = ar_flow + n2_flow
            number = int(row[6])
            metadata[number] = {
                "sample": number,
                "rate_angstrom_per_s": float(row[0]),
                "ar_sccm": ar_flow,
                "n2_sccm": n2_flow,
                "pn_percent": 100.0 * n2_flow / total_flow if total_flow else math.nan,
                "base_pressure_torr": float(row[4]),
                "power_percent": float(row[5]),
                "thickness_nm": float(row[7]),
                "mask": "None",
                "source": "sample.csv",
            }

    metadata_tsv = METADATA_DIR / "list2.txt"
    if metadata_tsv.exists():
        with metadata_tsv.open(newline="", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                sid = row.get("SampleID", "")
                match = re.search(r"NING-?([0-9]+)", sid)
                if not match:
                    continue
                number = int(match.group(1))
                ar_flow = clean_float(row.get("Flow_1"))
                n2_flow = clean_float(row.get("Flow_2"))
                rate = clean_float(row.get("Rate"))
                base_pressure = clean_float(row.get("Base_Pressure"))
                power = clean_float(row.get("Power"))
                thickness = clean_float(row.get("Thickness"))
                plasma = clean_float(row.get("Plasma_Pressure"))
                total_flow = (ar_flow or 0.0) + (n2_flow or 0.0)
                current = metadata.get(number, {})
                if base_pressure is None or base_pressure > 1e-3:
                    base_pressure = clean_float(current.get("base_pressure_torr"))

                current.update({
                    "sample": number,
                    "sample_id": sid,
                    "start": row.get("Start", ""),
                    "rate_angstrom_per_s": (rate * 10.0 if rate is not None and rate < 0.2 else rate),
                    "rate_raw": rate,
                    "ar_sccm": ar_flow,
                    "n2_sccm": n2_flow,
                    "pn_percent": 100.0 * n2_flow / total_flow if total_flow and n2_flow is not None else math.nan,
                    "base_pressure_torr": base_pressure,
                    "power_percent": power,
                    "thickness_nm": thickness,
                    "plasma_pressure_mTorr": plasma,
                    "mask": row.get("Mask", ""),
                    "source": "list2.txt",
                })
                metadata[number] = current

    for number, correction in METADATA_CORRECTIONS.items():
        metadata.setdefault(number, {"sample": number})
        metadata[number].update(correction)

    return metadata


def load_deposition_tests() -> tuple[np.ndarray, np.ndarray]:
    points = []
    nconc_csv = PLAIN_FILM_DIR / "Nconcentration.csv"
    if nconc_csv.exists():
        rows = np.genfromtxt(nconc_csv, comments="#", delimiter=";")
        if rows.ndim == 1:
            rows = rows.reshape(1, -1)
        for row in rows:
            ar_flow = float(row[1])
            n2_flow = float(row[2])
            total_flow = ar_flow + n2_flow
            points.append((100.0 * n2_flow / total_flow, float(row[0])))
    if not points:
        return np.array([]), np.array([])
    arr = np.array(points)
    return arr[:, 0], arr[:, 1]


def normalized_resistance(voltage: np.ndarray) -> np.ndarray:
    values = np.abs(np.asarray(voltage, dtype=float))
    low = np.nanpercentile(values, 2)
    high = np.nanpercentile(values, 98)
    if not np.isfinite(high - low) or abs(high - low) < 1e-18:
        return np.full_like(values, np.nan)
    return np.clip((values - low) / (high - low), 0.0, 1.0)


def smooth(values: np.ndarray, window: int = 5) -> np.ndarray:
    if len(values) < window:
        return values
    if window % 2 == 0:
        window += 1
    kernel = np.ones(window) / window
    padded = np.pad(values, (window // 2, window // 2), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def low_pass_window(length: int, requested: int) -> int:
    window = min(requested, length if length % 2 else length - 1)
    return max(3, window)


def low_pass_trace(values: np.ndarray, requested_window: int = 17) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) < 3:
        return values
    return smooth(values, low_pass_window(len(values), requested_window))


def branch_slices(temperature: np.ndarray) -> dict[str, slice]:
    max_index = int(np.nanargmax(temperature))
    branches: dict[str, slice] = {}
    if max_index > 8:
        branches["warming"] = slice(0, max_index + 1)
    if len(temperature) - max_index > 8:
        branches["cooling"] = slice(max_index, len(temperature))
    if not branches:
        branches["all"] = slice(0, len(temperature))
    return branches


def average_duplicate_temperatures(
    temperature: np.ndarray,
    resistance_norm: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(temperature)
    temperature = temperature[order]
    resistance_norm = resistance_norm[order]

    unique_t = []
    unique_r = []
    start = 0
    for index in range(1, len(temperature) + 1):
        if index == len(temperature) or temperature[index] != temperature[start]:
            unique_t.append(float(np.mean(temperature[start:index])))
            unique_r.append(float(np.mean(resistance_norm[start:index])))
            start = index
    return np.array(unique_t), np.array(unique_r)


def merged_low_pass_trace(
    temperature: np.ndarray,
    resistance_norm: np.ndarray,
    requested_window: int = 17,
) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(temperature) & np.isfinite(resistance_norm)
    if np.count_nonzero(mask) < 3:
        return np.asarray(temperature, dtype=float), np.asarray(resistance_norm, dtype=float)

    t, r = average_duplicate_temperatures(temperature[mask], resistance_norm[mask])
    return t, low_pass_trace(r, requested_window=requested_window)


def crossing_temperature(
    temperature: np.ndarray,
    resistance_norm: np.ndarray,
    level: float,
) -> float:
    mask = np.isfinite(temperature) & np.isfinite(resistance_norm)
    if np.count_nonzero(mask) < 3:
        return math.nan

    t, r = average_duplicate_temperatures(temperature[mask], resistance_norm[mask])
    r = smooth(r)

    crossings = []
    delta = r - level
    for index in range(1, len(t)):
        if delta[index - 1] == 0:
            crossings.append(t[index - 1])
        if delta[index - 1] * delta[index] <= 0 and r[index] != r[index - 1]:
            fraction = (level - r[index - 1]) / (r[index] - r[index - 1])
            crossings.append(t[index - 1] + fraction * (t[index] - t[index - 1]))
    if not crossings:
        return math.nan
    return float(np.median(crossings))


def max_gradient_temperature(
    temperature: np.ndarray,
    resistance_norm: np.ndarray,
) -> float:
    mask = np.isfinite(temperature) & np.isfinite(resistance_norm)
    if np.count_nonzero(mask) < 5:
        return crossing_temperature(temperature, resistance_norm, 0.50)

    t, r = average_duplicate_temperatures(temperature[mask], resistance_norm[mask])
    if len(t) < 5:
        return crossing_temperature(temperature, resistance_norm, 0.50)

    r_low_pass = low_pass_trace(r, requested_window=17)
    gradient = np.gradient(r_low_pass, t)
    candidate = np.isfinite(gradient) & (r_low_pass > 0.05) & (r_low_pass < 0.95)
    if np.count_nonzero(candidate) == 0:
        candidate = np.isfinite(gradient)
    if np.count_nonzero(candidate) == 0:
        return crossing_temperature(temperature, resistance_norm, 0.50)

    candidate_indices = np.flatnonzero(candidate)
    candidate_gradient = gradient[candidate]
    if np.nanmax(candidate_gradient) <= 0:
        selected = candidate_indices[int(np.nanargmax(np.abs(candidate_gradient)))]
    else:
        selected = candidate_indices[int(np.nanargmax(candidate_gradient))]
    return float(t[selected])


def transition_temperatures(
    measurement: Measurement,
    midpoint_method: str = "level",
) -> dict[str, float | str]:
    t = measurement.temperature
    r_norm = normalized_resistance(measurement.voltage)
    branch_results = {level: [] for level in TC_LEVELS}
    branch_names = []

    if midpoint_method == "max_gradient":
        result = {}
        for level in TC_LEVELS:
            if level == 0.50:
                value = max_gradient_temperature(t, r_norm)
            else:
                value = crossing_temperature(t, r_norm, level)
            result[f"tc_{int(level * 100):02d}_K"] = value
        result["transition_width_10_90_K"] = result["tc_90_K"] - result["tc_10_K"]
        result["branches"] = "+".join(branch_slices(t).keys())
        result["tc_midpoint_method"] = midpoint_method
        return result

    for name, branch_slice in branch_slices(t).items():
        branch_names.append(name)
        for level in TC_LEVELS:
            if level == 0.50 and midpoint_method == "max_gradient":
                value = max_gradient_temperature(t[branch_slice], r_norm[branch_slice])
            else:
                value = crossing_temperature(t[branch_slice], r_norm[branch_slice], level)
            if np.isfinite(value):
                branch_results[level].append(value)

    result = {
        f"tc_{int(level * 100):02d}_K": (
            float(np.mean(values)) if values else math.nan
        )
        for level, values in branch_results.items()
    }
    result["transition_width_10_90_K"] = result["tc_90_K"] - result["tc_10_K"]
    result["branches"] = "+".join(branch_names)
    result["tc_midpoint_method"] = midpoint_method
    return result


def status_for_sample(number: int | None) -> tuple[str, str]:
    if number == 16:
        return "excluded", "Connector Y short reported; measurement kept for traceability only."
    return "included", ""


def build_plain_film_summary(metadata: dict[int, dict[str, float | str]]) -> list[dict[str, object]]:
    files = sorted(PLAIN_FILM_DIR.glob("*/*.dat")) + sorted(DISCORD_DIR.glob("NING-*_Tc.dat"))
    rows: list[dict[str, object]] = []
    for path in files:
        measurement = load_measurement(path)
        number = sample_number(path)
        tc = transition_temperatures(measurement)
        meta = metadata.get(number or -1, {})
        status, notes = status_for_sample(number)
        note_parts = [notes] if notes else []
        metadata_note = str(meta.get("metadata_note", "")).strip()
        if metadata_note:
            note_parts.append(metadata_note)
        row = {
            "sample": number,
            "file": str(path.relative_to(ROOT)),
            "source_folder": path.parent.name,
            "measurement_kind": measurement.kind,
            "current_uA": measurement.current_a * 1e6 if measurement.current_a else math.nan,
            "status": status,
            "notes": "; ".join(note_parts),
        }
        row.update(meta)
        row.update(tc)
        rows.append(row)
    return rows


def build_device_summary() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(DISCORD_DIR.glob("[CD]1*.dat")):
        measurement = load_measurement(path)
        label = device_label(path) or path.stem
        width = DEVICE_WIDTH_UM.get(label, math.nan)
        current_uA = measurement.current_a * 1e6 if measurement.current_a else math.nan
        current_density = current_uA / width if np.isfinite(width) and current_uA else math.nan
        row = {
            "device": label,
            "width_um": width,
            "file": str(path.relative_to(ROOT)),
            "measurement_kind": measurement.kind,
            "current_uA": current_uA,
            "current_density_uA_per_um": current_density,
            "notes": "Width from Discord discussion.",
        }
        row.update(transition_temperatures(measurement, midpoint_method="max_gradient"))
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved: {path.relative_to(ROOT)}")


def finite(value: object) -> bool:
    try:
        return np.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def simonin_tc(thickness_nm: np.ndarray | float) -> np.ndarray:
    thickness = np.asarray(thickness_nm, dtype=float)
    tc = GAVALER_TC_INF_K * (1.0 - GAVALER_DC_NM / thickness)
    return np.where(thickness > GAVALER_DC_NM, tc, np.nan)


def plot_deposition(metadata: dict[int, dict[str, float | str]]) -> None:
    sample_points = [
        (float(meta["pn_percent"]), float(meta["rate_angstrom_per_s"]), int(number))
        for number, meta in metadata.items()
        if finite(meta.get("pn_percent")) and finite(meta.get("rate_angstrom_per_s")) and number <= 13
    ]
    test_pn, test_rate = load_deposition_tests()

    fig, ax = plt.subplots()
    if sample_points:
        pn = np.array([point[0] for point in sample_points])
        rate = np.array([point[1] for point in sample_points])
        ax.scatter(pn, rate, s=58, marker="o", color=PALETTE["blue"], label="NbN samples")

        all_pn = pn
        all_rate = rate
        if len(test_pn):
            all_pn = np.concatenate([all_pn, test_pn])
            all_rate = np.concatenate([all_rate, test_rate])
        if len(all_pn) >= 2:
            slope, intercept = np.polyfit(all_pn, all_rate, 1)
            xfit = np.linspace(max(0.0, all_pn.min() - 1.0), all_pn.max() + 1.0, 100)
            ax.plot(xfit, slope * xfit + intercept, color=PALETTE["grey"], label="Linear fit")

    if len(test_pn):
        ax.scatter(
            test_pn,
            test_rate,
            s=54,
            marker="s",
            color=PALETTE["orange"],
            label="Rate calibration",
        )

    style_ax(
        ax,
        xlabel=r"$P_{N_2}$ [%]",
        ylabel=r"Deposition rate [$\mathrm{\AA}/s$]",
    )
    style_legend(ax)
    finalize(fig, PLOT_DIR / "deposition_rate_n2_fraction", show=False)
    plt.close(fig)


def plot_tc_vs_pn(rows: list[dict[str, object]]) -> None:
    included = [
        row for row in rows
        if row.get("status") == "included"
        and finite(row.get("pn_percent"))
        and finite(row.get("tc_50_K"))
    ]
    excluded = [
        row for row in rows
        if row.get("status") != "included"
        and finite(row.get("pn_percent"))
        and finite(row.get("tc_50_K"))
    ]

    # Single-panel figure: crystal structures shown directly in the poster
    fig, ax = plt.subplots(figsize=(9.5, 7.8))

    # --- 3 zones ---
    zone_bounds = [(0.0, 6.5, "R$_I$", "#3D7FD8"), (6.5, 14.0, "R$_{II}$", "#8B63D9"), (14.0, 22.0, "R$_{III}$", "#E84D8A")]
    for x0, x1, label, color in zone_bounds:
        ax.axvspan(x0, x1, alpha=0.06, color=color, zorder=0)
        if x1 < 22.0:
            ax.axvline(x1, color="0.75", linestyle="--", linewidth=0.9, zorder=1)
        ax.text((x0 + x1) / 2.0, 14.7, label, ha="center", va="center",
                fontsize=22, fontweight="bold", color=color, alpha=0.7)

    for label, data in LITERATURE_TC.items():
        ax.plot(data["pn"], data["tc"], color=data["color"], alpha=0.9, label=label)
        ax.scatter(data["pn"], data["tc"], color=data["color"], s=36)

    if included:
        pn = np.array([float(row["pn_percent"]) for row in included])
        tc_mid = np.array([float(row["tc_50_K"]) for row in included])
        tc_low = np.array([float(row["tc_10_K"]) for row in included])
        tc_high = np.array([float(row["tc_90_K"]) for row in included])
        order = np.argsort(pn)
        ax.plot(pn[order], tc_mid[order], color=PALETTE["blue"], alpha=0.8)
        ax.errorbar(
            pn, tc_mid,
            yerr=[tc_mid - tc_low, tc_high - tc_mid],
            fmt="o", color=PALETTE["blue"], ecolor=PALETTE["blue"], capsize=4,
            label="This work",
        )

    style_ax(ax, xlabel=r"$P_{N_2}$ [%]", ylabel=r"$T_c$ [K]")
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15.5)
    style_legend(ax, many_threshold=2, max_columns=3)

    finalize(fig, PLOT_DIR / "tc_vs_n2_fraction", show=False)
    plt.close(fig)


def plot_plain_film_rt(rows: list[dict[str, object]]) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    files = sorted(PLAIN_FILM_DIR.glob("*/*.dat")) + sorted(DISCORD_DIR.glob("NING-*_Tc.dat"))
    for path in files:
        measurement = load_measurement(path)
        number = sample_number(path)
        r_norm = normalized_resistance(measurement.voltage)
        color = PALETTE["purple"] if number == 16 else None
        alpha = 0.45 if number == 16 else 0.85
        linestyle = "--" if number == 16 else "-"
        ax.plot(
            measurement.temperature,
            r_norm,
            linestyle=linestyle,
            color=color,
            alpha=alpha,
            label=f"NING-{number:02d}" if number is not None else measurement.label,
        )

    style_ax(
        ax,
        xlabel="Sample temperature [K]",
        ylabel=r"$R/R_n$",
    )
    ax.set_xlim(3, 15)
    ax.set_ylim(-0.05, 1.08)
    style_legend(ax, many_threshold=3, max_columns=5)
    finalize(fig, PLOT_DIR / "plain_film_resistance_temperature", show=False)
    plt.close(fig)


def plot_best_transition() -> None:
    """Separate heating/cooling as scatter + two low-pass guide lines."""
    path = PLAIN_FILM_DIR / "031125" / "NING-11.dat"
    measurement = load_measurement(path)
    r_norm = normalized_resistance(measurement.voltage)
    tc = transition_temperatures(measurement)

    branch_style = {
        "warming": (PALETTE["blue"], "o", "Heating"),
        "cooling": (PALETTE["green"], "s", "Cooling"),
    }

    fig, ax = plt.subplots()
    for name, sl in branch_slices(measurement.temperature).items():
        color, marker, label = branch_style.get(name, (PALETTE["grey"], "o", name))
        t_b = measurement.temperature[sl]
        r_b = r_norm[sl]
        ax.scatter(t_b, r_b, s=10, marker=marker, color=color, alpha=0.30, zorder=2, label=f"{label}")
        gt, gr = merged_low_pass_trace(t_b, r_b, requested_window=7)
        ax.plot(gt, gr, color=color, linewidth=2.0, zorder=3, label=f"{label} guide")

    level_colors = (
        (0.10, PALETTE["grey"]),
        (0.50, PALETTE["blue"]),
        (0.90, PALETTE["green"]),
    )
    for level, color in level_colors:
        key = f"tc_{int(level * 100):02d}_K"
        add_hline(ax, level, color=color, linestyle=":")
        ax.axvline(float(tc[key]), color=color, linestyle="--", linewidth=1.4, label=f"{int(level * 100)}%")

    style_ax(ax, xlabel="Sample temperature [K]", ylabel=r"$R/R_n$")
    ax.set_xlim(10.2, 11.8)
    ax.set_ylim(-0.04, 1.05)
    style_legend(ax, many_threshold=3, max_columns=4)
    finalize(fig, PLOT_DIR / "best_transition_ning11", show=False)
    plt.close(fig)


def plot_device_comparison() -> None:
    """Bridge devices only: scatter + low-pass guide per measurement file."""
    files = sorted(DISCORD_DIR.glob("[CD]1*.dat"))
    fig, ax = plt.subplots()
    for path in files:
        measurement = load_measurement(path)
        r_norm = normalized_resistance(measurement.voltage)
        label = device_label(path) or path.stem
        width = DEVICE_WIDTH_UM.get(label)
        current_uA = measurement.current_a * 1e6 if measurement.current_a else math.nan
        current_density = current_uA / width if width and current_uA else math.nan
        if "25" in path.stem:
            color = PALETTE["orange"]
        elif label == "C1":
            color = PALETTE["green"]
        else:
            color = PALETTE["blue"]
        legend = f"{label}: {width:g} $\\mu$m, {current_uA:g} $\\mu$A"
        if np.isfinite(current_density):
            legend += f" ({current_density:.1f} $\\mu$A/$\\mu$m)"
        ax.scatter(
            measurement.temperature,
            r_norm,
            s=6,
            color=color,
            alpha=0.20,
            label="_nolegend_",
        )
        guide_temperature, guide_resistance = merged_low_pass_trace(
            measurement.temperature,
            r_norm,
            requested_window=17,
        )
        ax.plot(guide_temperature, guide_resistance, color=color, linewidth=2.4, label=legend)

    style_ax(ax, xlabel="Sample temperature [K]", ylabel=r"$R/R_n$")
    ax.set_xlim(6.8, 9.4)
    ax.set_ylim(-0.05, 1.08)
    style_legend(ax, many_threshold=2, max_columns=2)
    finalize(fig, PLOT_DIR / "device_width_comparison", show=False)
    plt.close(fig)


def plot_transition_and_bridge() -> None:
    """Merged: NING-11 plain film + bridge devices on the same R/Rn vs T axes."""
    fig, ax = plt.subplots(figsize=(11.0, 7.5))

    # --- Plain film NING-11 (heating + cooling as scatter + guide) ---
    path_11 = PLAIN_FILM_DIR / "031125" / "NING-11.dat"
    m11 = load_measurement(path_11)
    r11 = normalized_resistance(m11.voltage)
    tc11 = transition_temperatures(m11, midpoint_method="max_gradient")
    branch_style = {
        "warming": (PALETTE["blue"], "o", "Plain film"),
        "cooling": (PALETTE["blue"], "s", "_nolegend_"),
    }
    for name, sl in branch_slices(m11.temperature).items():
        color, marker, lbl = branch_style.get(name, (PALETTE["grey"], "o", name))
        t_b = m11.temperature[sl]
        r_b = r11[sl]
        ax.scatter(t_b, r_b, s=8, marker=marker, color=color, alpha=0.25, zorder=2)
        gt, gr = merged_low_pass_trace(t_b, r_b, requested_window=7)
        ax.plot(gt, gr, color=color, linewidth=2.0, zorder=3, label=lbl)

    # --- Transition markers: onset (10%), midpoint (50%), offset (90%) ---
    marker_styles = [
        (0.10, "tc_10_K", "#888888", "Offset (10 %)"),
        (0.50, "tc_50_K", PALETTE["blue"],  r"$T_c$ (max.$|$d$R$/d$T|$)"),
        (0.90, "tc_90_K", "#888888", "Onset (90 %)"),
    ]
    for level, key, color, label in marker_styles:
        add_hline(ax, level, color=color, linestyle=":", linewidth=1.2, label=label)
        if key in tc11 and np.isfinite(float(tc11[key])):
            ax.axvline(float(tc11[key]), color=color, linestyle="--",
                       linewidth=1.2, zorder=1)

    # --- Bridge devices at matched current density (5.0 µA/µm each) ---
    # C1 @ 50 µA = 5.0 µA/µm; D1 @ 100 µA = 5.0 µA/µm. Skip C1 @ 25 µA.
    for path in sorted(DISCORD_DIR.glob("[CD]1*.dat")):
        if "25" in path.stem:        # skip C1 @ 25 µA — different current density
            continue
        m = load_measurement(path)
        r_norm = normalized_resistance(m.voltage)
        lbl = device_label(path) or path.stem
        width = DEVICE_WIDTH_UM.get(lbl)
        color = "#D62728" if lbl == "C1" else "#2CA02C"
        legend = f"Bridge (W = {width:g} $\\mu$m)"
        ax.scatter(m.temperature, r_norm, s=6, color=color, alpha=0.18, zorder=2)
        gt, gr = merged_low_pass_trace(m.temperature, r_norm, requested_window=17)
        ax.plot(gt, gr, color=color, linewidth=2.2, label=legend)

    style_ax(ax, xlabel="Sample temperature [K]", ylabel=r"$R/R_n$")
    ax.set_xlim(6.5, 12.5)
    ax.set_ylim(-0.05, 1.10)
    style_legend(ax, many_threshold=2, max_columns=2)
    finalize(fig, PLOT_DIR / "transition_and_bridge", show=False)
    plt.close(fig)


def selected_plain_film_tc(plain_rows: list[dict[str, object]]) -> float:
    for row in plain_rows:
        if row.get("sample") == 11 and finite(row.get("tc_50_K")):
            return float(row["tc_50_K"])
    return 10.99


def plot_bridge_tc_reference(
    device_rows: list[dict[str, object]],
    plain_rows: list[dict[str, object]],
) -> None:
    # Keep only measurements at the matched current density (5.0 µA/µm ±0.3)
    device_rows = [
        row for row in device_rows
        if finite(row.get("width_um")) and finite(row.get("tc_50_K"))
        and abs(float(row.get("current_density_uA_per_um", math.nan)) - 5.0) < 0.3
    ]
    plain_film_tc = selected_plain_film_tc(plain_rows)

    fig, ax_width = plt.subplots(1, 1, figsize=(9.5, 6.0))

    seen_labels: set[str] = set()
    width_offsets: dict[float, int] = {}
    for row in sorted(
        device_rows,
        key=lambda item: (
            float(item["width_um"]),
            float(item.get("current_density_uA_per_um", math.nan)),
            str(item.get("file", "")),
        ),
    ):
        width = float(row["width_um"])
        offset_index = width_offsets.get(width, 0)
        width_offsets[width] = offset_index + 1
        x = width + (offset_index - 0.5) * 0.55
        tc = float(row["tc_50_K"])
        tc_low = float(row["tc_10_K"]) if finite(row.get("tc_10_K")) else tc
        tc_high = float(row["tc_90_K"]) if finite(row.get("tc_90_K")) else tc
        current_density = float(row.get("current_density_uA_per_um", math.nan))
        color = PALETTE["blue"] if abs(current_density - 5.0) < 0.2 else PALETTE["orange"]
        label = f"4-point bridge, {current_density:g} $\\mu$A/$\\mu$m"
        legend_label = label if label not in seen_labels else "_nolegend_"
        seen_labels.add(label)
        ax_width.errorbar(
            x,
            tc,
            yerr=[[tc - tc_low], [tc_high - tc]],
            fmt="o",
            markersize=7,
            capsize=4,
            color=color,
            ecolor=color,
            label=legend_label,
        )

    ax_width.axhline(
        plain_film_tc,
        color=PALETTE["purple"],
        linestyle="--",
        linewidth=1.8,
        label=r"RF plain-film baseline, 10% $N_2$",
    )
    style_ax(
        ax_width,
        xlabel=r"Bridge width [$\mu$m]",
        ylabel=r"$T_c$ [K]",
        title=r"Bridge measurements",
    )
    ax_width.set_xticks([10, 20])
    ax_width.set_xlim(7.5, 22.5)
    ax_width.set_ylim(6.5, 11.8)
    ax_width.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1, 1, 0),
        mode="expand",
        ncol=1,
        borderaxespad=0.0,
        frameon=True,
        framealpha=1.0,
        edgecolor="black",
    )

    finalize(fig, PLOT_DIR / "bridge_tc_reference", show=False)
    plt.close(fig)


def run_parallel_tasks(tasks: list[tuple[str, object, tuple[object, ...]]]) -> None:
    workers = min(4, len(tasks))
    context = mp.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        futures = {
            executor.submit(func, *args): name
            for name, func, args in tasks
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
            except Exception as exc:
                raise RuntimeError(f"Parallel task failed: {name}") from exc


def convert_microscopy() -> None:
    try:
        from PIL import Image, ImageEnhance, ImageFilter
    except ImportError:
        print("  Skipped microscopy conversion: Pillow is not installed")
        return

    def enhance(image: "Image.Image") -> "Image.Image":
        rgb = image.convert("RGB")
        adjusted = ImageEnhance.Contrast(rgb).enhance(1.18)
        adjusted = ImageEnhance.Color(adjusted).enhance(1.04)
        adjusted = ImageEnhance.Sharpness(adjusted).enhance(1.12)
        return ImageEnhance.Brightness(adjusted).enhance(1.02)

    def soft_step(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
        scaled = np.clip((values - edge0) / (edge1 - edge0), 0.0, 1.0)
        return scaled * scaled * (3.0 - 2.0 * scaled)

    def neutralize_background(image: "Image.Image") -> "Image.Image":
        arr = np.asarray(image.convert("RGB")).astype(np.float32)
        flat = arr.reshape(-1, 3)
        brightness = flat.mean(axis=1)
        valid = (
            (brightness > np.percentile(brightness, 10))
            & (brightness < np.percentile(brightness, 98))
        )
        background = np.median(flat[valid], axis=0)

        color_distance = np.linalg.norm(arr - background, axis=2)
        blue_feature_score = (
            background[0] - arr[:, :, 0]
            + 0.65 * (arr[:, :, 2] - background[2])
        )
        dark_feature_score = background.mean() - arr.mean(axis=2)

        foreground = np.maximum(
            soft_step(30.0, 80.0, color_distance),
            soft_step(22.0, 65.0, blue_feature_score),
        )
        foreground = np.maximum(
            foreground,
            0.7 * soft_step(55.0, 105.0, dark_feature_score),
        )
        foreground_mask = Image.fromarray(
            np.uint8(np.clip(foreground * 255.0, 0, 255))
        ).filter(ImageFilter.GaussianBlur(radius=1.2))
        foreground = np.asarray(foreground_mask).astype(np.float32) / 255.0

        neutral_background = np.array([246.0, 248.0, 250.0], dtype=np.float32)
        corrected = (
            neutral_background * (1.0 - foreground[:, :, None])
            + arr * foreground[:, :, None]
        )
        return Image.fromarray(np.uint8(np.clip(corrected, 0, 255)))

    def align_image(source: Path, image: "Image.Image") -> "Image.Image":
        transform = MICROSCOPY_TRANSFORMS.get(source.stem, {})
        aligned = enhance(image).rotate(
            float(transform.get("rotation_deg", MICROSCOPY_ROTATION_DEG)),
            expand=True,
        )
        if transform.get("mirror_horizontal"):
            aligned = aligned.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        deskew = float(transform.get("deskew_deg", 0.0))
        if deskew:
            aligned = aligned.rotate(
                deskew,
                expand=True,
                fillcolor=tuple(int(value) for value in np.asarray(aligned).mean(axis=(0, 1))),
            )
        return neutralize_background(aligned)

    for source in sorted(MICROSCOPY_DIR.glob("*.tif")):
        target = POSTER_IMAGE_DIR / (source.stem + ".png")
        aligned_target = POSTER_IMAGE_DIR / f"{source.stem}_aligned.png"
        with Image.open(source) as image:
            original = image.convert("RGB")
            original.thumbnail((1600, 1200))
            original.save(target)
            aligned = align_image(source, image)
            aligned.thumbnail((1350, 1800))
            aligned.save(aligned_target)
        print(f"  Saved: {target.relative_to(ROOT)}")
        print(f"  Saved: {aligned_target.relative_to(ROOT)}")


def parse_gds_real8(data: bytes) -> list[float]:
    values = []
    for index in range(0, len(data), 8):
        raw = data[index:index + 8]
        if raw == b"\0" * 8:
            values.append(0.0)
            continue
        sign = -1 if raw[0] & 0x80 else 1
        exponent = (raw[0] & 0x7F) - 64
        mantissa = int.from_bytes(raw[1:], "big") / (1 << 56)
        values.append(sign * mantissa * (16 ** exponent))
    return values


def parse_gds_data(data_type: int, payload: bytes):
    if data_type == 2:
        return [item[0] for item in struct.iter_unpack(">h", payload)]
    if data_type == 3:
        return [item[0] for item in struct.iter_unpack(">i", payload)]
    if data_type == 5:
        return parse_gds_real8(payload)
    if data_type == 6:
        return payload.rstrip(b"\0").decode("ascii", errors="replace")
    return None


def load_gds_boundaries(path: Path) -> list[tuple[int, list[tuple[float, float]]]]:
    stream = path.read_bytes()
    position = 0
    in_boundary = False
    layer = 0
    polygons: list[tuple[int, list[tuple[float, float]]]] = []

    while position < len(stream):
        record_length, record_type, data_type = struct.unpack(">HBB", stream[position:position + 4])
        payload = stream[position + 4:position + record_length]
        position += record_length
        value = parse_gds_data(data_type, payload)

        if record_type == 0x08:
            in_boundary = True
            layer = 0
        elif record_type == 0x0D and value is not None:
            layer = int(value[0])
        elif record_type == 0x10 and in_boundary and value is not None:
            points = [
                (float(value[index]) * 1e-3, float(value[index + 1]) * 1e-3)
                for index in range(0, len(value), 2)
            ]
            polygons.append((layer, points))
        elif record_type == 0x11:
            in_boundary = False

    return polygons


GDS_DEVICE_CROPS: dict[str, tuple[float, float, float, float]] = {
    # (x0, x1, y0, y1) in µm — tuned to include device + label, exclude adjacent rows
    "C1": (-15.0, 355.0, 785.0, 1240.0),
    "D1": (-15.0, 355.0, 1295.0, 1735.0),
}


def render_gds_device_crops() -> None:
    if not GDS_LAYOUT.exists():
        print(f"  Skipped GDS device crop rendering: missing {GDS_LAYOUT.relative_to(ROOT)}")
        return

    polygons = load_gds_boundaries(GDS_LAYOUT)

    for device_name, (x0, x1, y0, y1) in GDS_DEVICE_CROPS.items():
        cropped_patches = []
        cropped_colors = []
        for layer, points in polygons:
            pts = np.array(points)
            cx = pts[:, 0].mean()
            cy = pts[:, 1].mean()
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                cropped_patches.append(Polygon(points, closed=True))
                cropped_colors.append(PALETTE["blue"] if layer == 1 else PALETTE["grey"])

        if not cropped_patches:
            print(f"  Skipped {device_name}: no polygons in crop region")
            continue

        width = x1 - x0
        height = y1 - y0
        scale = 4.0 / max(width, height)
        fig, ax = plt.subplots(figsize=(width * scale, height * scale))
        collection = PatchCollection(
            cropped_patches, facecolor=cropped_colors, edgecolor="none", alpha=0.92
        )
        ax.add_collection(collection)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        fig.tight_layout(pad=0.0)

        image_path = POSTER_IMAGE_DIR / f"gds_{device_name}"
        plot_path = PLOT_DIR / f"gds_{device_name}"
        fig.savefig(image_path.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.02)
        fig.savefig(plot_path.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(plot_path.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        print(f"  Saved: {image_path.relative_to(ROOT)}.png")
        print(f"  Saved: {plot_path.relative_to(ROOT)}.pdf / .png")


def render_gds_layout() -> None:
    if not GDS_LAYOUT.exists():
        print(f"  Skipped GDS rendering: missing {GDS_LAYOUT.relative_to(ROOT)}")
        return

    polygons = load_gds_boundaries(GDS_LAYOUT)
    patches = []
    colors = []
    for layer, points in polygons:
        patches.append(Polygon(points, closed=True))
        colors.append(PALETTE["blue"] if layer == 1 else PALETTE["orange"])

    fig, ax = plt.subplots(figsize=(10.5, 8.6))
    collection = PatchCollection(patches, facecolor=colors, edgecolor="none", alpha=0.92)
    ax.add_collection(collection)
    ax.autoscale()
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.05)

    image_base = POSTER_IMAGE_DIR / "gds_transport_bridges_v3"
    plot_base = PLOT_DIR / "gds_transport_bridges_v3"
    fig.savefig(image_base.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(plot_base.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(plot_base.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"  Saved: {image_base.relative_to(ROOT)}.png")
    print(f"  Saved: {plot_base.relative_to(ROOT)}.pdf / .png")


def plot_sc_field_diagram() -> None:
    """SC field diagram: box CENTRED, R(T) schematic on top, order [TypeI|TypeII|Normal]."""
    import matplotlib.gridspec as mgridspec
    from matplotlib.patches import Wedge

    BOX_W  = 1.2
    BOX_H  = 0.35
    BOX_Y  = 0.0           # centred
    BOX_TOP = BOX_H        #  0.35
    BOX_BOT = -BOX_H       # -0.35
    R_PSI  = 1.28
    TRANS_H = 0.65
    YMAX   = 2.5           # reduced vertical extent
    # Dummy keep-compat (not actually used with centred box)
    _BOX_Y_UNUSED = 0
    SC_FC = "#B8D0E8"; SC_EC = "#4A7AA0"
    PINK  = "#E84D8A"; DGRN  = "#1B7A3B"

    # ── helpers ───────────────────────────────────────────────────────────────
    def ss(t: float | np.ndarray) -> float | np.ndarray:
        t = np.clip(t, 0.0, 1.0); return t*t*(3-2*t)

    def iso_x(C: float, y: float, R: float = R_PSI) -> float | None:
        if abs(C) < 1e-9: return None
        coeffs = [1.0, -C, y**2 - R**2, -C*y**2]
        roots = np.roots(coeffs)
        sgn = 1 if C > 0 else -1
        valid = [r.real for r in roots
                 if abs(r.imag) < 1e-5 and sgn*r.real > 0 and r.real**2+y**2 >= R**2*0.97]
        return min(valid, key=lambda x: abs(x-C)) if valid else None

    # Full symmetric y array (box is at origin, visible above AND below)
    Y = np.linspace(-YMAX+0.05, YMAX-0.05, 420)
    TT = BOX_TOP + TRANS_H   # y level where upper bowing starts
    TB = BOX_BOT - TRANS_H   # y level where lower bowing starts

    def hybrid(C: float, R: float = R_PSI):
        """Straight far from box, bow only near surface. No NaN — box drawn on top covers interior."""
        xs = []
        for y in Y:
            if y > TT or y < TB:
                xs.append(C)                  # straight (far from box)
            elif y > BOX_TOP:
                t = ss((TT - y) / TRANS_H)
                xi = iso_x(C, y, R)
                xs.append(C if xi is None else C + t*(xi - C))
            elif y < BOX_BOT:               # lower transition
                t = ss((y - TB) / TRANS_H)
                xi = iso_x(C, y, R)
                xs.append(C if xi is None else C + t*(xi - C))
            else:                           # |y| ≤ BOX_H: inside box height — use full iso_x
                xi = iso_x(C, y, R)         # for Meissner, xi > BOX_W (line clears box)
                xs.append(C if xi is None else xi)
        return np.array(xs, dtype=float), Y.copy()

    def vtube(sx: float, vx: float):
        """Straight → converge to vx near box surface → x=vx through box → diverge below."""
        xs = []
        for y in Y:
            if y > TT or y < TB:
                xs.append(sx)               # straight
            elif y > BOX_TOP:
                t = ss((TT - y) / TRANS_H)
                xs.append(sx + t*(vx - sx))
            elif y < BOX_BOT:
                t = ss((y - TB) / TRANS_H)
                xs.append(sx + t*(vx - sx))
            else:                           # inside box height range: at vortex
                xs.append(vx)
        return np.array(xs), Y.copy()

    def draw_box(ax):
        ax.add_patch(plt.Rectangle((-BOX_W, BOX_BOT), 2*BOX_W, 2*BOX_H,
                                    fc=SC_FC, ec=SC_EC, lw=1.4, zorder=10))

    def arw(ax, xs, ys, color, lw=1.4, ms=11):
        """Upward arrows at the TOP of the upper segment and BOTTOM of the lower segment."""
        mt = (~np.isnan(xs)) & (ys > 0.65*YMAX)
        if mt.sum() >= 5:
            i = np.flatnonzero(mt)
            ax.annotate("", xy=(xs[i[-1]], ys[i[-1]]), xytext=(xs[i[-5]], ys[i[-5]]),
                        arrowprops=dict(arrowstyle="->", color=color, lw=lw, mutation_scale=ms))
        mb = (~np.isnan(xs)) & (ys < -0.65*YMAX)
        if mb.sum() >= 5:
            i = np.flatnonzero(mb)
            # arrow from lower y to higher y → upward direction
            ax.annotate("", xy=(xs[i[4]], ys[i[4]]), xytext=(xs[i[0]], ys[i[0]]),
                        arrowprops=dict(arrowstyle="->", color=color, lw=lw, mutation_scale=ms))

    # ── field-line parameters ─────────────────────────────────────────────────
    C_half = np.array([0.30, 0.57, 0.85, 1.10])  # verified clear box with R=1.5
    C_all  = np.concatenate([-C_half[::-1], C_half])
    VORT   = [-0.85, 0.0, 0.85];  VOFF = 0.18
    C_vo   = np.array([1.5, 1.9]);  R_VO = 0.5
    ls_kw  = dict(ls="--", dashes=(6,4), lw=1.35, zorder=3)

    # Panel order: [Meissner/TypeI | Vortex/TypeII | Normal]
    panels = [
        ("meissner", "Meissner state (Type I)", PINK, r"$T < T_c,\ B < B_c$"),
        ("vortex",   "Vortex phase (Type II)",  DGRN, r"$T < T_c,\ B > B_{c1}$"),
        ("normal",   "Normal phase",             PINK, r"$T > T_c$"),
    ]

    # ── figure: R(T) top + 3 field panels ────────────────────────────────────
    fig = plt.figure(figsize=(11.0, 7.0), facecolor="white")
    gs  = fig.add_gridspec(2, 3, height_ratios=[0.28, 1.0], hspace=0.12,
                           left=0.05, right=0.97, top=0.97, bottom=0.03, wspace=0.04)

    # ── R(T) schematic ────────────────────────────────────────────────────────
    ax_rt = fig.add_subplot(gs[0, :])
    Tc = 0.52
    ax_rt.plot([0, Tc, Tc, 1.0], [0, 0, 1, 1], color="#222", lw=2.4)
    ax_rt.axvspan(0,   Tc,  alpha=0.10, color="#3D7FD8")   # SC region
    ax_rt.axvspan(Tc, 1.0,  alpha=0.07, color="#888")       # Normal region
    ax_rt.axvline(Tc, color="#666", ls="--", lw=1.1)
    import matplotlib.transforms as mtransforms
    _blended = mtransforms.blended_transform_factory(ax_rt.transData, ax_rt.transAxes)
    ax_rt.text(Tc, 1.03, r"$T_c$", ha="center", va="bottom", fontsize=12, color="#444",
               transform=_blended, clip_on=False)
    ax_rt.text(Tc*0.38, 0.5, "Superconducting", ha="center", va="center",
               fontsize=19, color="#3D7FD8", style="italic")
    ax_rt.text((Tc+1)/2, 0.5, "Normal", ha="center", va="center",
               fontsize=19, color="#777", style="italic")
    # Column markers
    # Column markers removed — no specification of where Type I/II are on the curve
    ax_rt.set_xlim(0, 1);  ax_rt.set_ylim(-0.08, 1.28)
    ax_rt.set_xlabel("Temperature →", fontsize=11, labelpad=8)
    ax_rt.set_ylabel(r"$R$ →", fontsize=11)
    # Clean axes — no tick marks (they cause corner bracket artifacts)
    ax_rt.spines[["top", "right"]].set_visible(False)
    ax_rt.set_xticks([]);  ax_rt.set_yticks([])
    # Manual axis labels via text (avoids tick-mark artifacts at edges)
    ax_rt.text(0, -0.16, "0", ha="center", va="top", fontsize=9, color="#444", clip_on=False)
    ax_rt.text(-0.03, 0, "0", ha="right", va="center", fontsize=9, color="#444", clip_on=False)
    ax_rt.text(-0.03, 1, r"$R_n$", ha="right", va="center", fontsize=9, color="#444", clip_on=False)

    # ── field panels ──────────────────────────────────────────────────────────
    for col_i, (ax, (mode, title, color, label)) in \
            enumerate(zip([fig.add_subplot(gs[1, i]) for i in range(3)], panels)):
        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-YMAX, YMAX)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=5)

        if mode == "normal":
            for x0 in np.linspace(-2.0, 2.0, 9):
                ax.plot([x0]*2, [-YMAX+0.05, YMAX-0.05], color=color, **ls_kw)
                arw(ax, np.full_like(Y, x0), Y, color)
        elif mode == "meissner":
            for C in C_all:
                xs, ys = hybrid(C)
                ax.plot(xs, ys, color=color, **ls_kw)
                arw(ax, xs, ys, color)
        else:
            for C in np.concatenate([-C_vo[::-1], C_vo]):
                xs, ys = hybrid(C, R_VO)
                ax.plot(xs, ys, color=color, **ls_kw)
                arw(ax, xs, ys, color)
            for vx in VORT:
                for off in (-VOFF, VOFF):
                    xv, yv = vtube(vx+off, vx)
                    ax.plot(xv, yv, color=color, **ls_kw)
                    arw(ax, xv, yv, color)
                # Vortex line penetrating through the solid (field line passes through Type II SC)
                ax.plot([vx, vx], [-YMAX+0.05, YMAX-0.05], color=color,
                        ls="--", dashes=(6, 4), lw=1.35, zorder=11)

        # B arrow
        ax.annotate("", xy=(-2.4, YMAX*0.75), xytext=(-2.4, YMAX*0.50),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.9, mutation_scale=15))
        ax.text(-2.4, YMAX*0.88, r"$\vec{B}$", fontsize=15, color=color,
                ha="center", va="bottom")
        # Condition label placed BELOW the axes (outside the field line area)
        ax.text(0.5, -0.07, label, ha="center", va="top", fontsize=11.5, color="#333",
                transform=ax.transAxes, clip_on=False)
        draw_box(ax)

    base = PLOT_DIR / "sc_field_diagram"
    fig.savefig(str(base)+".pdf", dpi=300)
    fig.savefig(str(base)+".png", dpi=300)
    plt.close(fig)
    print(f"  Saved: {base.relative_to(ROOT)}.pdf / .png")


def plot_sputtering_diagram() -> None:
    """RF magnetron sputtering — large plasma cone, dashed circular B-arches, poster fonts."""

    FS = 14   # base font size for poster readability

    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    fig.patch.set_facecolor("white")
    ax.set_xlim(-1.0, 11.5); ax.set_ylim(0, 12)
    ax.set_aspect("equal"); ax.axis("off")

    def rot(pts, deg, cx=0.0, cy=0.0):
        th = math.radians(deg); c, s = math.cos(th), math.sin(th)
        return np.array([(c*x - s*y + cx, s*x + c*y + cy) for x, y in pts])

    def poly(pts, fc, ec="#333", lw=1.1, zo=5, alpha=1.0):
        ax.add_patch(plt.Polygon(pts, fc=fc, ec=ec, lw=lw, zorder=zo, alpha=alpha))

    # ── Chamber, with small inlet openings for Ar and N2 ────────────────
    chamber_x0, chamber_x1 = 0.3, 9.7
    chamber_y0, chamber_y1 = 0.3, 11.7
    chamber_style = dict(color="#555", lw=1.5, ls="--", zorder=1)
    ax.plot([chamber_x0, chamber_x1], [chamber_y1, chamber_y1], **chamber_style)
    ax.plot([chamber_x0, chamber_x1], [chamber_y0, chamber_y0], **chamber_style)
    ax.plot([chamber_x1, chamber_x1], [chamber_y0, chamber_y1], **chamber_style)
    for y_start, y_end in ((chamber_y0, 7.58), (8.02, 8.78), (9.22, chamber_y1)):
        ax.plot([chamber_x0, chamber_x0], [y_start, y_end], **chamber_style)
    ax.text(5.0, 11.88, "Vacuum chamber", ha="center",
            fontsize=FS-2, color="#555")

    # ── Substrate (green, rotating) — ↻ embedded in label ───────────────
    ax.add_patch(plt.Rectangle((1.2, 10.5), 7.6, 0.55,
                                fc="#4CAF50", ec="#1B5E20", lw=1.5, zorder=6))
    ax.text(5.0, 10.78, "Substrate (anode)  ↻", ha="center",
            fontsize=FS, fontweight="bold", color="white", zorder=7)
    # NbN thin film deposited on the bottom face of the substrate
    ax.add_patch(plt.Rectangle((1.2, 10.28), 7.6, 0.22,
                                fc="#90A4AE", ec="#455A64", lw=0.8, zorder=6))
    ax.text(5.0, 10.25, "NbN thin film", ha="center", va="top",
            fontsize=FS-5, color="#37474F", zorder=7)

    ANGLE = 0.0
    CX, CY = 5.0, 3.6

    # ── Large plasma cone (triangle from target face → substrate) ─────────
    face_left  = rot([(-2.2, 0)], ANGLE, CX, CY)[0]
    face_right = rot([(2.2,  0)], ANGLE, CX, CY)[0]
    sub_left  = (1.2,  10.5)
    sub_right = (8.8,  10.5)
    cone_pts = np.array([face_left, face_right, sub_right, sub_left])
    poly(cone_pts, fc="#CE93D8", ec="#CE93D8", lw=1.0, zo=2, alpha=0.16)

    # ── Target (grey cathode) — face at y=0, body extends at y<0 (away from plasma) ──
    tgt = rot([(-2.2,0),(2.2,0),(2.2,-0.6),(-2.2,-0.6)], ANGLE, CX, CY)
    poly(tgt, fc="#B0BEC5", ec="#37474F", lw=1.4, zo=8)
    tmid = tgt.mean(axis=0)
    ax.text(tmid[0], tmid[1], "Nb target (cathode)", ha="center", va="center",
            fontsize=FS-1, fontweight="bold", color="#1A2A2A",
            rotation=ANGLE, zorder=9)

    # ── Magnets (N-S-N) — behind target ──────────────────────────────────
    NSEG = 3
    seg_w = 4.4 / NSEG
    mcols = ["#E53935", "#9E9E9E", "#E53935"]   # N – S – N
    mlbls = ["N", "S", "N"]
    for i in range(NSEG):
        x0 = -2.2 + i*seg_w; x1 = x0 + seg_w
        pts = rot([(x0,-0.6),(x1,-0.6),(x1,-1.25),(x0,-1.25)], ANGLE, CX, CY)
        poly(pts, fc=mcols[i], ec="#333", lw=0.7, zo=7)
        mid = pts.mean(axis=0)
        ax.text(mid[0], mid[1], mlbls[i], ha="center", va="center",
                fontsize=FS-4, fontweight="bold", color="white",
                rotation=ANGLE, zorder=10)

    # ── Water cooling — behind magnets ────────────────────────────────────
    cool = rot([(-2.2,-1.25),(2.2,-1.25),(2.2,-2.0),(-2.2,-2.0)], ANGLE, CX, CY)
    poly(cool, fc="#90CAF9", ec="#1565C0", lw=0.9, zo=6)
    cmid = cool.mean(axis=0)
    ax.text(cmid[0], cmid[1], "Water cooling", ha="center", va="center",
            fontsize=FS-4, color="#0D47A1", rotation=ANGLE, zorder=9)

    # ── Ground shield (grey plates on both sides of magnetron assembly) ──
    shield_L = rot([(-3.0, 0.4), (-2.2, 0.4), (-2.2, -2.0), (-3.0, -2.0)], ANGLE, CX, CY)
    shield_R = rot([(2.2, 0.4), (3.0, 0.4), (3.0, -2.0), (2.2, -2.0)], ANGLE, CX, CY)
    poly(shield_L, fc="#78909C", ec="#37474F", lw=1.1, zo=7)
    poly(shield_R, fc="#78909C", ec="#37474F", lw=1.1, zo=7)
    gs_pt = rot([(3.2, -0.8)], ANGLE, CX, CY)[0]
    ax.text(gs_pt[0] + 0.15, gs_pt[1], "Ground\nshield", fontsize=FS-4, color="#37474F",
            ha="left", va="center", zorder=6)

    # ── B-field arches: N→S arches from each outer N pole to the centre S pole ──
    # With N-S-N arrangement: outer N poles at ±(3/4)*seg_w from centre, centre S at 0.
    # Each arch is a semicircle centred midway between its N pole and the S centre.
    # Traversal θ: 0→π sweeps right→left, so left arches (cx<0) go S→N and need
    # a reversed arrow; right arches (cx>0) go N→S and are drawn correctly.
    ARCH_CLR = "#1A237E"
    half = seg_w / 2   # half-distance between adjacent pole centres ≈ 0.733
    arch_groups = [
        (-half, [half * 0.52, half * 0.90]),   # left: between left-N and centre-S
        (+half, [half * 0.52, half * 0.90]),   # right: mirror
    ]
    for cx_loc, radii in arch_groups:
        for r_loc in radii:
            theta = np.linspace(0, np.pi, 100)
            xloc = cx_loc + r_loc * np.cos(theta)
            yloc = r_loc * np.sin(theta)   # upper half = toward plasma
            pts_w = rot(list(zip(xloc, yloc)), ANGLE, CX, CY)
            ax.plot(pts_w[:, 0], pts_w[:, 1],
                    color=ARCH_CLR, lw=2.8, ls="--", dashes=(5.5, 3), zorder=15)
            # Arrow at arch peak — B goes from N pole to S pole above the surface.
            # Right arch (cx_loc>0): θ traversal goes N→S, so increasing-θ direction is correct.
            # Left arch (cx_loc<0): θ traversal goes S→N, so reverse the arrow.
            mid = len(theta) // 2
            dx = pts_w[mid+2, 0] - pts_w[mid-2, 0]
            dy = pts_w[mid+2, 1] - pts_w[mid-2, 1]
            s = 1 if cx_loc > 0 else -1
            ax.annotate("", xy=(pts_w[mid, 0]+s*dx*0.5, pts_w[mid, 1]+s*dy*0.5),
                        xytext=(pts_w[mid, 0]-s*dx*0.5, pts_w[mid, 1]-s*dy*0.5),
                        arrowprops=dict(arrowstyle="-|>", color=ARCH_CLR,
                                       lw=1.9, mutation_scale=12))

    arch_lbl = rot([(2.55, 1.35)], ANGLE, CX, CY)[0]
    ax.text(
        arch_lbl[0] + 0.08,
        arch_lbl[1],
        "B-field\ntrap",
        fontsize=FS - 3,
        color=ARCH_CLR,
        ha="left",
        va="center",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
        zorder=20,
    )

    # ── Plasma and sputtered atom dots — schematic, deterministic, non-symmetric ──
    # Purple dots represent the ionised Ar-rich plasma; blue dots represent
    # sputtered Nb/NbN species travelling from the target toward the substrate.
    arrow_col = "#7B1FA2"
    purple_points = np.array([
        (3.02, 9.62), (4.18, 10.08), (6.04, 9.70), (7.55, 9.28),
        (2.45, 8.72), (3.50, 8.55), (4.95, 8.92), (6.70, 8.52),
        (2.70, 7.83), (4.58, 7.58), (5.72, 7.92), (7.18, 7.44),
        (3.30, 6.82), (4.25, 6.35), (5.48, 6.62), (6.34, 6.08),
        (3.76, 5.68), (5.05, 5.33), (6.78, 5.14), (4.58, 4.82),
        (5.70, 4.54),
    ])
    purple_sizes = [4.1, 4.8, 3.8, 4.3, 4.6, 3.5, 4.0, 4.7, 3.7, 4.2, 3.5,
                    4.3, 4.5, 3.7, 4.0, 4.8, 3.8, 4.4, 4.1, 3.6, 4.2]
    for (px, py), size in zip(purple_points, purple_sizes):
        ax.plot(px, py, "o", ms=size, color="#9C27B0", alpha=0.66, zorder=4)

    blue_points = np.array([
        (3.55, 9.12), (5.30, 9.42), (6.96, 9.05),
        (2.90, 8.28), (4.15, 8.04), (6.10, 8.12),
        (3.48, 7.16), (5.05, 7.02), (6.58, 6.82),
        (4.06, 6.05), (5.82, 5.72), (6.92, 5.62),
    ])
    blue_sizes = [3.4, 3.0, 3.6, 3.2, 3.4, 3.1, 3.5, 3.0, 3.4, 3.2, 3.5, 3.1]
    for (px, py), size in zip(blue_points, blue_sizes):
        ax.plot(px, py, "o", ms=size, color="#1565C0", alpha=0.72, zorder=5)

    label_box = {
        "boxstyle": "round,pad=0.18",
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.76,
    }
    ax.text(
        0.78,
        5.68,
        "Ar⁺ plasma",
        fontsize=FS - 5,
        color="#8E24AA",
        ha="left",
        va="center",
        bbox=label_box,
        zorder=20,
    )
    ax.text(
        0.78,
        4.98,
        "Nb/NbN atoms",
        fontsize=FS - 5,
        color="#1565C0",
        ha="left",
        va="center",
        bbox=label_box,
        zorder=20,
    )
    ax.annotate(
        "",
        xy=(2.55, 6.65),
        xytext=(1.96, 5.78),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#8E24AA",
            lw=1.25,
            mutation_scale=10,
            alpha=0.78,
        ),
        zorder=19,
    )
    ax.annotate(
        "",
        xy=(4.06, 6.05),
        xytext=(1.96, 4.98),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#1565C0",
            lw=1.25,
            mutation_scale=10,
            alpha=0.78,
        ),
        zorder=19,
    )

    # ── RF power supply: outside chamber, cables from anode and cathode ──
    RF_CX, RF_TOP, RF_BOT = 10.55, 7.0, 5.0
    RF_CY = (RF_TOP + RF_BOT) / 2
    # Anode cable: from substrate top-right corner → right → down to RF box top
    ax.plot([8.8, RF_CX, RF_CX], [10.83, 10.83, RF_TOP],
            color="#555", lw=1.3, zorder=4)
    # Cathode cable: from target face right tip → right → up to RF box bottom
    cath_pt = rot([(2.2, 0)], ANGLE, CX, CY)[0]
    ax.plot([cath_pt[0], RF_CX, RF_CX], [cath_pt[1], cath_pt[1], RF_BOT],
            color="#555", lw=1.3, zorder=4)
    # RF box (outside chamber right wall at x=9.7)
    ax.add_patch(plt.Rectangle((9.9, RF_BOT), 1.3, RF_TOP - RF_BOT,
                                fc="#FFF9C4", ec="#555", lw=1.2, zorder=5))
    ax.text(RF_CX, RF_CY, "RF", ha="center", va="center",
            fontsize=FS + 2, fontweight="bold", color="#333", zorder=6)

    # ── Gas inlets — species labels, no partial-pressure annotation ──────
    ax.annotate("", xy=(1.8, 9.0), xytext=(0.3, 9.0),
                arrowprops=dict(arrowstyle="-|>", color="#E65100", lw=1.8,
                               mutation_scale=14))
    ax.text(0.1, 9.0, "Ar", ha="right", va="center",
            fontsize=FS, fontweight="bold", color="#E65100")
    ax.annotate("", xy=(1.8, 7.8), xytext=(0.3, 7.8),
                arrowprops=dict(arrowstyle="-|>", color="#0277BD", lw=0.9,
                               mutation_scale=9))
    ax.text(0.1, 7.8, r"N$_2$", ha="right", va="center",
            fontsize=FS, fontweight="bold", color="#0277BD")

    fig.tight_layout(pad=0.3)
    base = PLOT_DIR / "sputtering_diagram"
    fig.savefig(str(base) + ".pdf", dpi=300)
    fig.savefig(str(base) + ".png", dpi=300)
    plt.close(fig)
    print(f"  Saved: {base.relative_to(ROOT)}.pdf / .png")


def main() -> None:
    ensure_directories()
    metadata = load_deposition_metadata()
    plain_rows = build_plain_film_summary(metadata)
    device_rows = build_device_summary()

    write_csv(PROCESSED_DIR / "plain_film_tc_summary.csv", plain_rows)
    write_csv(PROCESSED_DIR / "device_tc_summary.csv", device_rows)
    run_parallel_tasks([
        ("deposition trend", plot_deposition, (metadata,)),
        ("Tc versus nitrogen", plot_tc_vs_pn, (plain_rows,)),
        ("plain-film R(T)", plot_plain_film_rt, (plain_rows,)),
        ("best transition", plot_best_transition, ()),
        ("device comparison", plot_device_comparison, ()),
        ("transition and bridge", plot_transition_and_bridge, ()),
        ("bridge Tc reference", plot_bridge_tc_reference, (device_rows, plain_rows)),
        ("GDS rendering", render_gds_layout, ()),
        ("GDS device crops", render_gds_device_crops, ()),
        ("SC field diagram", plot_sc_field_diagram, ()),
        ("sputtering diagram", plot_sputtering_diagram, ()),
    ])
    convert_microscopy()


if __name__ == "__main__":
    main()
