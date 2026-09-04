# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — spherical cathode grid geometry

"""Closed-form geometry of a spherical cathode grid.

Two grid families became standard for spherical gridded IEC devices and
both are described here: the **globe** grid, a latitude/longitude cage
whose aperture count follows from its two ring counts, and the
**symmetric** grid, of which only four configurations are permissible
because each is the spherical projection of one specific polyhedron.

Every relation is taken from Wulfkühler et al., *Scientific Reports*
**14**:2261 (2024) and nothing is inferred beyond what that paper
prints. The bridge half-angle is the one place where the printed
equation and the printed table disagree in what they can tell you: the
table's four angles are reproduced to every digit it prints by both
``arctan(t / D)`` and the small-angle ``t / D``, so the table alone
cannot settle the form. Equation 5 settles it, and it carries the
tangent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import require_positive

GRID_KINDS: Final = ("globe", "symmetric")
MIN_LONGITUDE_RINGS: Final = 1
MIN_LATITUDE_RINGS: Final = 0
FULL_TURN_DEG: Final = 360.0


@dataclass(frozen=True, slots=True)
class SymmetricGrid:
    """One permissible symmetric grid configuration.

    Parameters
    ----------
    rings
        Number of great-circle ring elements the grid is built from.
    apertures
        Number of spherical-triangle apertures the rings cut.
    max_rings_in_crossing
        Largest number of rings meeting at a single crossing point.
    spherical_polyhedron
        Name of the spherical polyhedron the grid projects.
    """

    rings: int
    apertures: int
    max_rings_in_crossing: int
    spherical_polyhedron: str


SYMMETRIC_GRIDS: Final = (
    SymmetricGrid(3, 8, 2, "spherical octahedron"),
    SymmetricGrid(6, 24, 3, "spherical tetrakis hexahedron"),
    SymmetricGrid(9, 48, 4, "spherical disdyakis dodecahedron"),
    SymmetricGrid(15, 120, 5, "spherical disdyakis triacontahedron"),
)
SYMMETRIC_GRID_BY_RINGS: Final = {grid.rings: grid for grid in SYMMETRIC_GRIDS}


def require_ring_count(name: str, value: int, minimum: int) -> int:
    """Return a ring count at or above its documented floor.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Ring count under validation.
    minimum
        Smallest admissible count for this field.

    Returns
    -------
    int
        The validated count.

    Raises
    ------
    DeviceConfigurationError
        If the count is below its floor. Booleans are rejected: ``True``
        is an ``int`` in Python and would otherwise pass as one ring.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise DeviceConfigurationError(f"{name}: must be an integer, got {value!r}")
    if value < minimum:
        raise DeviceConfigurationError(
            f"{name}: must be at least {minimum}, got {value!r}"
        )
    return value


def bridge_half_angle_rad(bridge_thickness_m: float, grid_diameter_m: float) -> float:
    """Half-angle subtended by one bridge element of a grid.

    A bridge element is the conductor between two neighbouring
    apertures. Its thickness projected onto the grid radius subtends
    ``arctan(t_bridge / D_grid)``, equation 5 of the filed source: the
    half-thickness over the radius is the thickness over the diameter.

    Parameters
    ----------
    bridge_thickness_m
        Bridge thickness ``t_bridge`` in metres; strictly positive.
    grid_diameter_m
        Grid diameter ``D_grid`` in metres; strictly positive.

    Returns
    -------
    float
        The half-angle ``alpha_bridge`` in radians.

    Raises
    ------
    DeviceConfigurationError
        If either length is non-finite or not strictly positive.
    """
    require_positive("bridge_thickness_m", bridge_thickness_m)
    require_positive("grid_diameter_m", grid_diameter_m)
    return math.atan(bridge_thickness_m / grid_diameter_m)


def globe_aperture_count(latitude_rings: int, longitude_rings: int) -> int:
    """Return the number of apertures of a globe grid.

    Equation 12 of the filed source, which assumes the apertures nearest
    each pole are triangular and the grid meets its conductor rod at the
    north pole. A longitude *ring* is a full great circle and therefore
    contributes two meridians, which is where the factor of two comes
    from.

    Parameters
    ----------
    latitude_rings
        Number of latitude rings ``n_lat``; not negative. Zero is
        admissible and describes a grid of bare meridians.
    longitude_rings
        Number of longitude rings ``n_long``; at least one.

    Returns
    -------
    int
        The aperture count ``N_globe``.

    Raises
    ------
    DeviceConfigurationError
        If either ring count is below its documented floor.
    """
    require_ring_count("latitude_rings", latitude_rings, MIN_LATITUDE_RINGS)
    require_ring_count("longitude_rings", longitude_rings, MIN_LONGITUDE_RINGS)
    return 2 * longitude_rings * (latitude_rings + 1)


def symmetric_grid_aperture_angle_deg(max_rings_in_crossing: int) -> float:
    """Varying aperture angle of a symmetric grid.

    Two of the three angles of a symmetric grid's spherical triangles are
    fixed at 90 and 60 degrees. The third follows from how many rings
    meet at the busiest crossing point, as ``360 / (2 n)``.

    Parameters
    ----------
    max_rings_in_crossing
        Largest number of rings meeting at one crossing point; at least
        two, since a single ring crosses nothing.

    Returns
    -------
    float
        The varying angle in degrees.

    Raises
    ------
    DeviceConfigurationError
        If fewer than two rings are said to cross.
    """
    require_ring_count("max_rings_in_crossing", max_rings_in_crossing, 2)
    return FULL_TURN_DEG / (2 * max_rings_in_crossing)


def symmetric_grid(rings: int) -> SymmetricGrid:
    """Return the permissible symmetric grid built from ``rings`` rings.

    Only four configurations exist. The filed source states that beyond
    fifteen rings the varying angle would fall to thirty degrees or less
    and violate the bound on the angle sum of a proper spherical
    triangle, while noting that no proof of exhaustiveness is offered.
    This function is therefore a lookup and refuses anything else rather
    than extrapolating the pattern.

    Parameters
    ----------
    rings
        Ring count; one of 3, 6, 9 or 15.

    Returns
    -------
    SymmetricGrid
        The tabulated configuration.

    Raises
    ------
    DeviceConfigurationError
        If no symmetric grid is tabulated for that ring count.
    """
    require_ring_count("rings", rings, 2)
    grid = SYMMETRIC_GRID_BY_RINGS.get(rings)
    if grid is None:
        admissible = sorted(SYMMETRIC_GRID_BY_RINGS)
        raise DeviceConfigurationError(
            f"rings: no symmetric grid is tabulated for {rings!r}; "
            f"tabulated ring counts: {admissible!r}"
        )
    return grid
