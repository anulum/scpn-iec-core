# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — inertial-electrostatic-confinement parameter model

"""Validated parameter objects of an IEC configuration.

The derived quantity implements one standard result and nothing more:
the maximum singly-charged ion energy ``E = e U`` of the electrostatic
well (R. L. Hirsch, J. Appl. Phys. 38 (1967) 4522). It is a rough
consistency instrument with documented applicability bounds; no claim
about any real machine follows from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_iec_core.errors import DeviceConfigurationError

CONFINEMENT_KINDS: Final = ("gridded", "polywell")
POLYWELL_MIN_COILS: Final = 6


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class ConfinementStructure:
    """Confinement structure of an IEC configuration.

    Parameters
    ----------
    kind
        Confinement class: ``gridded`` (physical cathode grid) or
        ``polywell`` (magnetically formed virtual cathode).
    cathode_grid_transparency
        Geometric transparency of the cathode grid; strictly inside
        ``(0, 1)`` for the gridded class and exactly one for the
        polywell class (no physical grid intercepts).
    polyhedral_coil_count
        Number of polyhedral field coils; zero for the gridded class
        and at least six for the polywell class.

    Raises
    ------
    DeviceConfigurationError
        If the kind is unknown or a class invariant is violated.
    """

    kind: str
    cathode_grid_transparency: float
    polyhedral_coil_count: int

    def __post_init__(self) -> None:
        """Validate the confinement-structure class invariants.

        Raises
        ------
        DeviceConfigurationError
            If the kind is unknown or a class invariant is violated.
        """
        if self.kind not in CONFINEMENT_KINDS:
            raise DeviceConfigurationError(
                f"kind: must be one of {CONFINEMENT_KINDS!r}, got {self.kind!r}"
            )
        require_finite("cathode_grid_transparency", self.cathode_grid_transparency)
        if self.kind == "gridded":
            if not 0.0 < self.cathode_grid_transparency < 1.0:
                raise DeviceConfigurationError(
                    "cathode_grid_transparency: gridded requires a physical "
                    "grid with transparency strictly inside (0, 1), "
                    f"got {self.cathode_grid_transparency!r}"
                )
            if self.polyhedral_coil_count != 0:
                raise DeviceConfigurationError(
                    "polyhedral_coil_count: gridded declares no magnetic "
                    f"coils, got {self.polyhedral_coil_count!r}"
                )
        else:
            if self.cathode_grid_transparency != 1.0:
                raise DeviceConfigurationError(
                    "cathode_grid_transparency: polywell has no physical "
                    "grid — transparency must be exactly 1, "
                    f"got {self.cathode_grid_transparency!r}"
                )
            if self.polyhedral_coil_count < POLYWELL_MIN_COILS:
                raise DeviceConfigurationError(
                    "polyhedral_coil_count: polywell requires at least "
                    f"{POLYWELL_MIN_COILS} coils, "
                    f"got {self.polyhedral_coil_count!r}"
                )


@dataclass(frozen=True, slots=True)
class ElectrostaticDrive:
    """Electrostatic drive of an IEC configuration.

    Parameters
    ----------
    well_voltage_kv
        Electrostatic well voltage ``U`` in kilovolts; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If the voltage is non-finite or not strictly positive.
    """

    well_voltage_kv: float

    def __post_init__(self) -> None:
        """Validate the drive invariants.

        Raises
        ------
        DeviceConfigurationError
            If the voltage is non-finite or not strictly positive.
        """
        require_positive("well_voltage_kv", self.well_voltage_kv)

    def max_ion_energy_kev(self) -> float:
        """Maximum singly-charged ion energy of the validated well.

        Returns
        -------
        float
            ``E = e U`` in kiloelectronvolts — numerically equal to the
            well voltage in kilovolts (Hirsch, JAP 38 (1967) 4522).
        """
        return self.well_voltage_kv
