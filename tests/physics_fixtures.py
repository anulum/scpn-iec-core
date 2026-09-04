# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — level-0 physics anchors and builders

"""Anchors and builders shared by the level-0 physics tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

Two filed sources are used and they carry different kinds of value.

**Wulfkühler et al., Scientific Reports 14:2261 (2024)** — open access,
CC BY 4.0 — prints the closed-form grid geometry. Every constant below
whose name begins ``PRINTED_`` is read from that paper and is reproduced
by the code under test rather than stored for comparison alone.

**Radel, UWFDM-1325 (2007)** — the University of Wisconsin–Madison IEC
device — prints absolute dimensions. It does not print a transparency,
so wherever a transparency is needed the fixture declares a synthetic
one and says so; no transparency here is attributed to that device.

**Reading note.** The equations were read off rendered page images, not
off the PDF text layer. `pdftotext` drops the tangent from equation 5
and renders it as a bare fraction, and Table 2's four angles agree to
every digit it prints under both readings, so the table cannot correct
the mistake. The internal papers ledger records this at length.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_iec_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_iec_core.parameters import ConfinementStructure, ElectrostaticDrive
from scpn_iec_core.physics.level0 import CathodeGridDeclaration
from scpn_iec_core.physics.transparency import sphere_area_m2

# --- Wulfkühler et al. 2024, Table 2: bridge ratio and its printed angle ---
# The paper prints each angle to three decimals in degrees.
PRINTED_BRIDGE_ANGLES_DEG: Final = (
    (1.0, 50.0, 1.146),
    (1.0, 100.0, 0.573),
    (1.0, 150.0, 0.382),
    (0.8, 200.0, 0.229),
)
PRINTED_BRIDGE_ANGLE_DECIMALS: Final = 3

# --- Wulfkühler et al. 2024, equation 12 and the text around it ---
# Figure 11's caption states the aperture count of the grid it draws.
PRINTED_FIGURE11_RINGS: Final = (4, 5)
PRINTED_FIGURE11_APERTURES: Final = 50
# "only globe grids with n_lat = n_long and n_lat = n_long - 1 in the range
# of n_long 2 to 10 will be considered. This provides grids with 8 to 220
# apertures" — the two endpoints of that stated range.
PRINTED_GLOBE_FAMILY_RANGE: Final = ((1, 2, 8), (10, 10, 220))
# Fancher's cathode, cited in the paper's review of experimental grids.
PRINTED_FANCHER_RINGS: Final = (9, 32)
PRINTED_FANCHER_APERTURES: Final = 640

# --- Wulfkühler et al. 2024, Table 3: the four symmetric grids ---
PRINTED_SYMMETRIC_GRIDS: Final = (
    (3, 8, 2, 90.0),
    (6, 24, 3, 60.0),
    (9, 48, 4, 45.0),
    (15, 120, 5, 36.0),
)
# The same paper's review of experiments states two of those counts a
# second time, from two different laboratories, which is why the table is
# read as corroborated rather than merely transcribed.
PRINTED_CORROBORATED_SYMMETRIC: Final = ((6, 24), (9, 48))

# --- Radel, UWFDM-1325: the University of Wisconsin-Madison IEC device ---
# Section 4.1.2, pages 69 to 72.
RADEL_CATHODE_DIAMETER_M: Final = 0.20
RADEL_CATHODE_WIRE_DIAMETER_M: Final = 0.00075
RADEL_ANODE_DIAMETER_M: Final = 0.40
RADEL_SYMMETRIC_CATHODE_RINGS: Final = 9
# Section 4.1, page 66: the cylindrical aluminium vacuum chamber.
RADEL_CHAMBER_DIAMETER_M: Final = 0.91
RADEL_CHAMBER_HEIGHT_M: Final = 0.65

# --- Synthetic, and not attributed to any device ---
# Radel prints no transparency for the UW grids. This value is declared so
# that the relations have an input, and it sits inside the range the other
# source calls readily achievable for globe grids.
SYNTHETIC_GRID_TRANSPARENCY: Final = 0.95
SYNTHETIC_WELL_VOLTAGE_KV: Final = 100.0
SYNTHETIC_POLYWELL_COILS: Final = 6
SYNTHETIC_REGISTRY_VERSION: Final = "1.0.0"
SYNTHETIC_REGISTRY_DIGEST: Final = "0" * 64


def registry_binding() -> RegistryBinding:
    """Build the synthetic registry pin the fixtures share.

    Returns
    -------
    RegistryBinding
        A well-formed pin; its digest is synthetic and pins nothing.
    """
    return RegistryBinding(
        version=SYNTHETIC_REGISTRY_VERSION,
        digest_sha256=SYNTHETIC_REGISTRY_DIGEST,
    )


def anchor_configuration() -> DeviceConfiguration:
    """Build the gridded configuration the anchors are evaluated on.

    Returns
    -------
    DeviceConfiguration
        A ``gridded_iec`` configuration carrying the synthetic
        transparency and well voltage.
    """
    return DeviceConfiguration(
        identifier="gridded_iec",
        confinement=ConfinementStructure(
            kind="gridded",
            cathode_grid_transparency=SYNTHETIC_GRID_TRANSPARENCY,
            polyhedral_coil_count=0,
        ),
        drive=ElectrostaticDrive(well_voltage_kv=SYNTHETIC_WELL_VOLTAGE_KV),
        registry=registry_binding(),
    )


def polywell_configuration() -> DeviceConfiguration:
    """Build the virtual-cathode configuration of the same family.

    Returns
    -------
    DeviceConfiguration
        A ``polywell`` configuration; its class invariant fixes the
        transparency at exactly one.
    """
    return DeviceConfiguration(
        identifier="polywell",
        confinement=ConfinementStructure(
            kind="polywell",
            cathode_grid_transparency=1.0,
            polyhedral_coil_count=SYNTHETIC_POLYWELL_COILS,
        ),
        drive=ElectrostaticDrive(well_voltage_kv=SYNTHETIC_WELL_VOLTAGE_KV),
        registry=registry_binding(),
    )


def equal_aperture_areas(
    aperture_count: int, grid_radius_m: float, transparency: float
) -> tuple[float, ...]:
    """Build aperture areas that realise a transparency exactly.

    Parameters
    ----------
    aperture_count
        Number of apertures to divide the open area between.
    grid_radius_m
        Grid radius in metres.
    transparency
        Geometric transparency the apertures should realise.

    Returns
    -------
    tuple of float
        One area per aperture, all equal.
    """
    open_area = transparency * sphere_area_m2(grid_radius_m)
    return (open_area / aperture_count,) * aperture_count


def anchor_grid(*, with_areas: bool = True) -> CathodeGridDeclaration:
    """Build the symmetric cathode grid the anchors are evaluated on.

    The ring count and both lengths come from Radel: the UW device was
    operated with a nine-ring symmetric cathode of 20 cm diameter wound
    from 0.75 mm wire. Treating that wire as the bridge element is the
    fixture's own reading, not something the report prints.

    Parameters
    ----------
    with_areas
        Whether to attach the synthetic per-aperture areas.

    Returns
    -------
    CathodeGridDeclaration
        The declared grid.
    """
    rings = RADEL_SYMMETRIC_CATHODE_RINGS
    apertures = {count: cells for count, cells, _, _ in PRINTED_SYMMETRIC_GRIDS}[rings]
    areas = (
        equal_aperture_areas(
            apertures, RADEL_CATHODE_DIAMETER_M / 2.0, SYNTHETIC_GRID_TRANSPARENCY
        )
        if with_areas
        else None
    )
    return CathodeGridDeclaration(
        kind="symmetric",
        grid_diameter_m=RADEL_CATHODE_DIAMETER_M,
        bridge_thickness_m=RADEL_CATHODE_WIRE_DIAMETER_M,
        symmetric_rings=rings,
        aperture_areas_m2=areas,
    )


def circular_half_angles(
    aperture_count: int, bridge_half_angle_rad: float, angular_radius_rad: float
) -> tuple[float, ...]:
    """Build neighbour half-angles that leave a given circular aperture.

    Equation 7 subtracts the bridge half-angle from the neighbour
    half-angle, so a grid whose apertures should each subtend
    ``angular_radius_rad`` is declared by adding the bridge back on.

    Parameters
    ----------
    aperture_count
        Number of apertures.
    bridge_half_angle_rad
        Half-angle the bridge element subtends.
    angular_radius_rad
        Angular radius each circular aperture should have.

    Returns
    -------
    tuple of float
        One neighbour half-angle per aperture.
    """
    return (bridge_half_angle_rad + angular_radius_rad,) * aperture_count


def degrees_rounded(radians: float) -> float:
    """Convert to degrees and round to the precision Table 2 prints.

    Parameters
    ----------
    radians
        Angle in radians.

    Returns
    -------
    float
        The angle in degrees, rounded to three decimals.
    """
    return round(math.degrees(radians), PRINTED_BRIDGE_ANGLE_DECIMALS)
