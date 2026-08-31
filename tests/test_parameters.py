# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — parameter model tests

"""Every validation branch of the IEC parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import (
    ConfinementStructure,
    ElectrostaticDrive,
    require_finite,
    require_positive,
)


def synthetic_gridded(**overrides: Any) -> ConfinementStructure:
    """Build a valid synthetic gridded structure with optional overrides."""
    values: dict[str, Any] = {
        "kind": "gridded",
        "cathode_grid_transparency": 0.95,
        "polyhedral_coil_count": 0,
    }
    values.update(overrides)
    return ConfinementStructure(**values)


def synthetic_polywell(**overrides: Any) -> ConfinementStructure:
    """Build a valid synthetic polywell structure with optional overrides."""
    values: dict[str, Any] = {
        "kind": "polywell",
        "cathode_grid_transparency": 1.0,
        "polyhedral_coil_count": 6,
    }
    values.update(overrides)
    return ConfinementStructure(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_both_confinement_classes_construct() -> None:
    """Both documented confinement classes construct."""
    assert synthetic_gridded().kind == "gridded"
    assert synthetic_polywell().polyhedral_coil_count == 6


@pytest.mark.parametrize(
    ("builder", "overrides", "fragment"),
    [
        (synthetic_gridded, {"kind": "fusor"}, "kind"),
        (synthetic_gridded, {"cathode_grid_transparency": 0.0}, "transparency"),
        (synthetic_gridded, {"cathode_grid_transparency": 1.0}, "transparency"),
        (
            synthetic_gridded,
            {"cathode_grid_transparency": math.nan},
            "cathode_grid_transparency",
        ),
        (synthetic_gridded, {"polyhedral_coil_count": 2}, "no magnetic"),
        (synthetic_polywell, {"cathode_grid_transparency": 0.9}, "no physical"),
        (synthetic_polywell, {"polyhedral_coil_count": 4}, "at least"),
    ],
)
def test_invalid_structure_is_rejected(
    builder: Any, overrides: dict[str, Any], fragment: str
) -> None:
    """Each confinement-class violation is rejected precisely."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        builder(**overrides)


def test_drive_and_ion_energy() -> None:
    """The drive constructs and derives the ion energy ``E = e U``."""
    drive = ElectrostaticDrive(well_voltage_kv=80.0)
    assert drive.max_ion_energy_kev() == pytest.approx(80.0)


def test_invalid_drive_is_rejected() -> None:
    """Non-positive well voltages are rejected."""
    with pytest.raises(DeviceConfigurationError, match="well_voltage_kv"):
        ElectrostaticDrive(well_voltage_kv=0.0)
    with pytest.raises(DeviceConfigurationError, match="well_voltage_kv"):
        ElectrostaticDrive(well_voltage_kv=math.inf)
