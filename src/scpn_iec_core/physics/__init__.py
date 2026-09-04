# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — level-0 device physics package

"""Level-0 device physics of the IEC device family.

The published closed-form geometry of a spherical cathode grid — the
aperture count its ring structure implies, the half-angle its bridges
subtend, the three transparency metrics that compare one grid geometry
with another, and the geometric upper bound those place on how many
times an ion may pass through — composed with the electrostatic well the
configuration already carries.

The family's two configurations meet these relations differently and the
package keeps that difference visible rather than smoothing it: a
gridded device has apertures to count and a transparency below one, a
polywell has neither. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_iec_core.physics.grid_geometry import (
    FULL_TURN_DEG,
    GRID_KINDS,
    MIN_LATITUDE_RINGS,
    MIN_LONGITUDE_RINGS,
    SYMMETRIC_GRID_BY_RINGS,
    SYMMETRIC_GRIDS,
    SymmetricGrid,
    bridge_half_angle_rad,
    globe_aperture_count,
    require_ring_count,
    symmetric_grid,
    symmetric_grid_aperture_angle_deg,
)
from scpn_iec_core.physics.ion_transit import maximum_ion_passes
from scpn_iec_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CathodeGridDeclaration,
    Level0Physics,
    OperatingPoint,
    level0_physics,
    require_grid_for_class,
)
from scpn_iec_core.physics.transparency import (
    QUARTER_TURN_RAD,
    circular_aperture_radius_m,
    circular_transparency,
    geometric_transparency,
    normalised_circular_transparency,
    require_aperture_areas,
    sphere_area_m2,
    spherical_cap_area_m2,
)

__all__ = [
    "FULL_TURN_DEG",
    "GRID_KINDS",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MIN_LATITUDE_RINGS",
    "MIN_LONGITUDE_RINGS",
    "QUARTER_TURN_RAD",
    "SYMMETRIC_GRIDS",
    "SYMMETRIC_GRID_BY_RINGS",
    "CathodeGridDeclaration",
    "Level0Physics",
    "OperatingPoint",
    "SymmetricGrid",
    "bridge_half_angle_rad",
    "circular_aperture_radius_m",
    "circular_transparency",
    "geometric_transparency",
    "globe_aperture_count",
    "level0_physics",
    "maximum_ion_passes",
    "normalised_circular_transparency",
    "require_aperture_areas",
    "require_grid_for_class",
    "require_ring_count",
    "sphere_area_m2",
    "spherical_cap_area_m2",
    "symmetric_grid",
    "symmetric_grid_aperture_angle_deg",
]
