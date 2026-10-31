# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — level-0 physics benchmark

"""Benchmark the level-0 physics of this package on the Python floor.

Follows the ecosystem benchmark standard: warm-up, repeated samples,
percentiles, one row per (operation, backend), unavailable backends marked
explicitly, full provenance in the artefact. Two operations are timed:

- ``closed_forms``: the bridge half-angle, the circular aperture radius,
  the spherical-cap area and the maximum ion-pass bound over a
  deterministic grid of synthetic transparencies and aperture half-angles;
  each sample times one full grid pass;
- ``level0_record``: the composed level-0 record with its canonical bytes
  on a synthetic nine-ring symmetric grid over a grid of well voltages;
  each sample times one full grid pass.

This package has no native crate. The ``rust_native`` row records that
explicitly instead of omitting it. Nothing measured here is a physics
claim, and a run on a loaded host is a smoke timing, not a performance
measurement.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scpn_iec_core.configuration import (  # noqa: E402
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_iec_core.parameters import (  # noqa: E402
    ConfinementStructure,
    ElectrostaticDrive,
)
from scpn_iec_core.physics import (  # noqa: E402
    CathodeGridDeclaration,
    bridge_half_angle_rad,
    circular_aperture_radius_m,
    level0_physics,
    maximum_ion_passes,
    sphere_area_m2,
    spherical_cap_area_m2,
    symmetric_grid,
)

SCHEMA: Final = "scpn-iec-core.level0-physics-benchmark.v1"
NATIVE_STATUS: Final = (
    "unavailable: this package has no native crate; the level-0 kernels use "
    "+ - * /, math.fsum and the platform atan, sin, asin and cos, and the "
    "decision on a native backend is open with the project owner"
)
SYNTHETIC_TRANSPARENCY: Final = 0.95
SYNTHETIC_GRID_DIAMETER_M: Final = 0.20
SYNTHETIC_BRIDGE_THICKNESS_M: Final = 0.00075
SYNTHETIC_RINGS: Final = 9


def grid(points: int) -> list[tuple[float, float]]:
    """Build a deterministic synthetic grid of transparencies and angles.

    Parameters
    ----------
    points
        Number of grid points.

    Returns
    -------
    list of (float, float)
        ``(transparency, minimum_half_angle_rad)`` pairs, the transparency
        in the open unit interval and the half-angle between 0.05 and
        0.75 rad.
    """
    return [
        (
            0.5 + 0.49 * (index % 97) / 96.0,
            0.05 + 0.7 * (index % 89) / 88.0,
        )
        for index in range(points)
    ]


def reference_grid() -> CathodeGridDeclaration:
    """Return the synthetic nine-ring symmetric grid; it describes nothing.

    Returns
    -------
    CathodeGridDeclaration
        A symmetric grid with equal aperture areas realising the synthetic
        transparency and equal neighbour half-angles.
    """
    apertures = symmetric_grid(SYNTHETIC_RINGS).apertures
    radius = SYNTHETIC_GRID_DIAMETER_M / 2.0
    area = SYNTHETIC_TRANSPARENCY * sphere_area_m2(radius) / apertures
    bridge = bridge_half_angle_rad(
        SYNTHETIC_BRIDGE_THICKNESS_M, SYNTHETIC_GRID_DIAMETER_M
    )
    return CathodeGridDeclaration(
        kind="symmetric",
        grid_diameter_m=SYNTHETIC_GRID_DIAMETER_M,
        bridge_thickness_m=SYNTHETIC_BRIDGE_THICKNESS_M,
        symmetric_rings=SYNTHETIC_RINGS,
        aperture_areas_m2=(area,) * apertures,
        minimum_half_angles_rad=(bridge + 0.2,) * apertures,
    )


def configuration(well_voltage_kv: float) -> DeviceConfiguration:
    """Return a synthetic gridded configuration; it describes nothing.

    Parameters
    ----------
    well_voltage_kv
        Well voltage of the configuration.

    Returns
    -------
    DeviceConfiguration
        A ``gridded_iec`` configuration with the synthetic transparency.
    """
    return DeviceConfiguration(
        identifier="gridded_iec",
        confinement=ConfinementStructure(
            kind="gridded",
            cathode_grid_transparency=SYNTHETIC_TRANSPARENCY,
            polyhedral_coil_count=0,
        ),
        drive=ElectrostaticDrive(well_voltage_kv=well_voltage_kv),
        registry=RegistryBinding(version="1.0.0", digest_sha256="0" * 64),
    )


def closed_forms_pass(sample_grid: list[tuple[float, float]]) -> float:
    """Evaluate the closed forms once over the grid.

    Parameters
    ----------
    sample_grid
        Transparency and half-angle pairs.

    Returns
    -------
    float
        Checksum of the results, so the work cannot be optimised away.
    """
    radius = SYNTHETIC_GRID_DIAMETER_M / 2.0
    total = 0.0
    for transparency, half_angle in sample_grid:
        bridge = bridge_half_angle_rad(
            SYNTHETIC_BRIDGE_THICKNESS_M, SYNTHETIC_GRID_DIAMETER_M
        )
        base = circular_aperture_radius_m(radius, half_angle, bridge)
        total += spherical_cap_area_m2(radius, base)
        total += maximum_ion_passes(transparency)
    return total


def record_pass_factory(
    declared_grid: CathodeGridDeclaration,
) -> Callable[[list[tuple[float, float]]], float]:
    """Return a grid pass that composes and serialises level-0 records.

    Parameters
    ----------
    declared_grid
        Validated grid declaration every record is built with.

    Returns
    -------
    callable
        The pass; the transparency of each grid point is ignored and its
        half-angle sets a well voltage between 30 and 170 kV.
    """

    def record_pass(sample_grid: list[tuple[float, float]]) -> float:
        total = 0
        for _transparency, half_angle in sample_grid:
            voltage = 20.0 + 200.0 * half_angle
            record = level0_physics(configuration(voltage), declared_grid)
            total += len(record.canonical_bytes())
        return float(total)

    return record_pass


def measure(
    run: Callable[[list[tuple[float, float]]], float],
    sample_grid: list[tuple[float, float]],
    warmup: int,
    repeats: int,
) -> dict[str, float]:
    """Time repeated grid passes and summarise them.

    Parameters
    ----------
    run
        Grid pass to time.
    sample_grid
        Parameter grid.
    warmup
        Discarded leading passes.
    repeats
        Timed passes.

    Returns
    -------
    dict[str, float]
        Percentiles, mean, min, max in microseconds per grid point and the
        throughput in points per second (P50-based).
    """
    for _ in range(warmup):
        run(sample_grid)
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        run(sample_grid)
        samples.append((time.perf_counter_ns() - start) / 1e3 / len(sample_grid))
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        return ordered[min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))]

    p50 = percentile(0.5)
    return {
        "p50_us_per_point": p50,
        "p95_us_per_point": percentile(0.95),
        "p99_us_per_point": percentile(0.99),
        "mean_us_per_point": statistics.fmean(samples),
        "min_us_per_point": ordered[0],
        "max_us_per_point": ordered[-1],
        "throughput_points_per_s": 1e6 / p50,
    }


def provenance() -> dict[str, Any]:
    """Collect the environment provenance of a run.

    Returns
    -------
    dict[str, Any]
        Interpreter, platform, CPU model, commit and host-load context.
    """
    cpu_model = "unknown"
    with contextlib.suppress(OSError):
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    load = "unavailable"
    with contextlib.suppress(OSError):
        load = Path("/proc/loadavg").read_text(encoding="utf-8").split()[0]
    commit = "unknown"
    git = shutil.which("git")
    if git is not None:
        with contextlib.suppress(OSError):
            # A fixed argument vector with the resolved executable; no shell.
            commit = subprocess.run(  # noqa: S603
                [git, "rev-parse", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "load_average_1min_at_start": load,
        "commit": commit,
        "isolated_cores": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command-line interface.

    Parameters
    ----------
    argv
        Argument vector; None reads sys.argv.

    Returns
    -------
    int
        0 on completion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=int, default=20_000)
    parser.add_argument("--record-points", type=int, default=2_000)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--label", default="local")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results")
    args = parser.parse_args(argv)
    sample_grid = grid(args.points)
    record_grid = grid(args.record_points)
    record_pass = record_pass_factory(reference_grid())
    results: list[dict[str, Any]] = [
        {
            "name": "closed_forms",
            "backend": "python_floor",
            "stats": measure(closed_forms_pass, sample_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "closed_forms",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
        {
            "name": "level0_record",
            "backend": "python_floor",
            "stats": measure(record_pass, record_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "level0_record",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
    ]
    artefact = {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "label": args.label,
        "platform": provenance(),
        "parameters": {
            "points": args.points,
            "record_points": args.record_points,
            "warmup": args.warmup,
            "repeats": args.repeats,
        },
        "results": results,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / f"level0_physics.{args.label}.json"
    target.write_text(
        json.dumps(artefact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"benchmark: wrote {target}")
    for row in results:
        print(f"  {row['name']} {row['backend']}: {row['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
