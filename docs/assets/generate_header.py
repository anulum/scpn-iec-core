# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the electrostatic potential well with converging
ions, the gridded-versus-polywell class split drawn at the repository's
own minimum coil count, and the documented well-voltage range. The
right-hand text panel states only facts backed by the repository
itself.

Outputs (written next to this script):

- ``repo_header.png`` — the potential well with inbound ions and the
  converged core (used by ``README.md``).
- ``repo_header_class_split.png`` — the physical grid cathode beside
  the polywell virtual cathode.
- ``repo_header_voltage_range.png`` — well depth against voltage with
  the documented operating floor.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

POLYWELL_MIN_COILS = 6

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configurations", "gridded_iec · polywell"),
    ("Class Invariants", "grid vs virtual cathode, hard"),
    ("Polywell Rule", "at least six confinement coils"),
    ("Voltage Gate", "below documented range flagged"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.74,
        "IEC CORE",
        color="white",
        fontsize=34,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.66,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.615, 0.615], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.55
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _core_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw the glowing converged core."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 150)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 150)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=28,
        cmap=_glow_cmap(),
        alpha=0.92,
    )


def generate_potential_well() -> None:
    """Generate ``repo_header.png``: the electrostatic potential well."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    radius = np.linspace(-1.0, 1.0, 400)
    well = 7.6 - 5.6 * np.exp(-((radius / 0.30) ** 2))
    profile_x = 5.0 + 3.9 * radius
    ax.plot(profile_x, well, color=CYAN, lw=2.6, alpha=0.95)
    ax.fill_between(profile_x, well, 7.6, color=CYAN, alpha=0.06)

    ax.plot(
        [1.0, 9.0],
        [7.6, 7.6],
        color=STEEL,
        lw=1.0,
        alpha=0.6,
        ls=(0, (4, 3)),
    )
    ax.text(
        1.1,
        7.85,
        "grid / wall potential",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        alpha=0.9,
    )
    ax.text(
        5.0,
        1.45,
        "radius",
        color="#8899bb",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        1.28,
        8.9,
        "electrostatic potential",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    for start_x, direction in ((1.9, +1), (8.1, -1)):
        for offset in (0.0, 0.55, -0.55):
            ax.annotate(
                "",
                xy=(start_x + direction * 1.35, 6.6 + offset * 0.28),
                xytext=(start_x, 7.15 + offset * 0.28),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": MAGENTA,
                    "lw": 1.3,
                    "alpha": 0.85,
                    "mutation_scale": 9,
                },
            )
    ax.text(
        2.35,
        6.35,
        "ions accelerate inward",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        alpha=0.95,
    )

    _core_glow(ax, 5.0, 2.35, 0.55, 1.7)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    ax.plot(
        5.0 + 0.42 * np.cos(theta),
        2.35 + 0.42 * np.sin(theta),
        color=CYAN,
        lw=1.6,
        alpha=0.95,
    )
    ax.text(
        5.0,
        3.35,
        "converged core",
        color="#99bbdd",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.text(
        5.0,
        0.75,
        "the field does the confining · no closed magnetic surface required",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "A Well Deep Enough To Fuse")
    _save(fig, plt, "repo_header.png")


def generate_class_split() -> None:
    """Generate ``repo_header_class_split.png``: grid versus polywell."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 300)

    centre = 2.6
    _core_glow(ax, centre, 0.15, 0.26, 0.85)
    ax.plot(
        centre + 0.24 * np.cos(theta),
        0.15 + 0.24 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    for tilt in np.linspace(0, np.pi, 7, endpoint=False):
        ax.plot(
            centre + 0.86 * np.cos(theta) * np.cos(tilt),
            0.15 + 0.86 * np.sin(theta),
            color=STEEL,
            lw=1.3,
            alpha=0.8,
        )
    ax.plot(
        centre + 1.02 * np.cos(theta),
        0.15 + 1.02 * np.sin(theta),
        color=PROBE,
        lw=1.4,
        alpha=0.6,
    )
    for index in range(10):
        angle = 2.0 * np.pi * index / 10
        ax.annotate(
            "",
            xy=(centre + 0.42 * np.cos(angle), 0.15 + 0.42 * np.sin(angle)),
            xytext=(centre + 0.98 * np.cos(angle), 0.15 + 0.98 * np.sin(angle)),
            arrowprops={
                "arrowstyle": "-|>",
                "color": MAGENTA,
                "lw": 1.0,
                "alpha": 0.75,
                "mutation_scale": 8,
            },
        )
    ax.text(
        centre,
        2.05,
        "gridded_iec",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        1.7,
        "physical grid cathode",
        color="#667799",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        centre,
        -2.2,
        "Hirsch, JAP 38 (1967) 4522",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    centre = 7.4
    _core_glow(ax, centre, 0.15, 0.26, 0.85)
    ax.plot(
        centre + 0.24 * np.cos(theta),
        0.15 + 0.24 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    ring = np.linspace(0.0, 2.0 * np.pi, 60)
    for index in range(POLYWELL_MIN_COILS):
        angle = 2.0 * np.pi * index / POLYWELL_MIN_COILS + np.pi / 6
        coil_x = centre + 0.92 * np.cos(angle)
        coil_z = 0.15 + 0.92 * np.sin(angle)
        ax.plot(
            coil_x
            + 0.26 * np.cos(ring) * np.cos(angle)
            - 0.10 * np.sin(ring) * np.sin(angle),
            coil_z
            + 0.26 * np.cos(ring) * np.sin(angle)
            + 0.10 * np.sin(ring) * np.cos(angle),
            color=MAGENTA,
            lw=1.5,
            alpha=0.9,
        )
    ax.text(
        centre,
        2.05,
        "polywell",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        1.7,
        f"virtual cathode · {POLYWELL_MIN_COILS}+ coils",
        color="#667799",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        centre,
        -2.2,
        "no material grid in the ion path",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot([5.0, 5.0], [-1.9, 1.9], color=STEEL, lw=0.8, alpha=0.4)
    ax.text(
        5.0,
        -2.8,
        "a configuration contradicting its class is rejected",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )
    _text_panel(fig, "Real Grid Or Virtual Cathode")
    _save(fig, plt, "repo_header_class_split.png")


def generate_voltage_range() -> None:
    """Generate ``repo_header_voltage_range.png``: the voltage gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "well voltage",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.85,
        "well depth",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    voltage = np.linspace(0.0, 1.0, 200)
    px = 1.0 + 8.0 * voltage
    py = 1.7 + 6.6 * voltage
    ax.plot(px, py, color=CYAN, lw=2.6, alpha=0.95)
    ax.fill_between(px, py, 1.7, color=CYAN, alpha=0.05)

    floor_x = 1.0 + 8.0 * 0.30
    ax.plot(
        [floor_x, floor_x],
        [1.7, 9.0],
        color=MAGENTA,
        lw=1.6,
        alpha=0.9,
        ls=(0, (5, 3)),
    )
    ax.text(
        floor_x,
        9.25,
        "documented IEC operating range starts here",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.fill_between([1.0, floor_x], 1.7, 9.0, color=RED, alpha=0.06)
    ax.fill_between([floor_x, 9.0], 1.7, 9.0, color=GREEN, alpha=0.05)
    ax.text(
        (1.0 + floor_x) / 2,
        5.4,
        "below range\n· FLAGGED",
        color="#ff8899",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        va="center",
        alpha=0.95,
    )
    ax.text(
        6.6,
        3.3,
        "documented range",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    for fraction, inside in ((0.18, False), (0.48, True), (0.78, True)):
        mark_x, mark_y = 1.0 + 8.0 * fraction, 1.7 + 6.6 * fraction
        if inside:
            ax.plot(mark_x, mark_y, "o", color=CYAN, ms=7, alpha=0.95)
        else:
            ax.plot(
                mark_x,
                mark_y,
                "x",
                color=RED,
                ms=9,
                mew=2.2,
                alpha=0.95,
            )

    ax.text(
        5.0,
        0.75,
        "a declared well voltage below the documented range is "
        "flagged, never silently accepted",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Depth With A Documented Floor")
    _save(fig, plt, "repo_header_voltage_range.png")


if __name__ == "__main__":
    generate_potential_well()
    generate_class_split()
    generate_voltage_range()
