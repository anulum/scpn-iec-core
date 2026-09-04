# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — spherical cathode grid transparency metrics

"""Published transparency metrics of a spherical cathode grid.

Three of the four metrics Wulfkühler et al., *Scientific Reports*
**14**:2261 (2024) use to compare grid geometries, in the closed forms
that paper prints: the geometric transparency (equation 6), the circular
transparency (equations 7 to 9) and the normalised circular
transparency (equation 10).

The geometric transparency is the fraction of the sphere the apertures
leave open. The circular transparency is what that fraction would be if
every aperture were the largest circle that fits inside it, so their
ratio says how close the apertures are to circles — it is exactly one
for a grid whose apertures already are circles, and that identity is
what the tests anchor equations 9 and 10 on.

The fourth metric, the distribution's potential energy, is not
implemented: it is a sum over aperture centre points, which this package
does not carry, and computing it would require the mesh the filed source
builds and this repository does not.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Final

from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import require_finite, require_positive

QUARTER_TURN_RAD: Final = math.pi / 2.0


def sphere_area_m2(grid_radius_m: float) -> float:
    """Total surface area of the sphere a grid is built on.

    Parameters
    ----------
    grid_radius_m
        Grid radius ``R_grid`` in metres; strictly positive.

    Returns
    -------
    float
        ``4 pi R_grid**2`` in square metres.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """
    require_positive("grid_radius_m", grid_radius_m)
    return 4.0 * math.pi * grid_radius_m * grid_radius_m


def require_aperture_areas(
    name: str, areas_m2: Sequence[float], grid_radius_m: float
) -> tuple[float, ...]:
    """Return aperture areas that can lie on the given sphere.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    areas_m2
        Individual aperture areas in square metres.
    grid_radius_m
        Grid radius the areas are measured on, in metres.

    Returns
    -------
    tuple of float
        The validated areas.

    Raises
    ------
    DeviceConfigurationError
        If the sequence is empty, if any area is non-finite or negative,
        or if the areas together exceed the sphere they are said to lie
        on. The last is refused rather than clamped: a transparency above
        one is not a grid with wide apertures, it is a measurement of
        something other than this sphere.
    """
    if not areas_m2:
        raise DeviceConfigurationError(f"{name}: must carry at least one aperture")
    validated: list[float] = []
    for index, area in enumerate(areas_m2):
        require_finite(f"{name}[{index}]", area)
        if area < 0.0:
            raise DeviceConfigurationError(
                f"{name}[{index}]: must not be negative, got {area!r}"
            )
        validated.append(float(area))
    total = math.fsum(validated)
    available = sphere_area_m2(grid_radius_m)
    if total > available:
        raise DeviceConfigurationError(
            f"{name}: apertures total {total!r} m^2 on a sphere of "
            f"{available!r} m^2; the apertures cannot exceed the sphere"
        )
    return tuple(validated)


def geometric_transparency(
    aperture_areas_m2: Sequence[float], grid_radius_m: float
) -> float:
    """Fraction of the grid sphere the apertures leave open.

    Equation 6 of the filed source. The sum is taken with
    :func:`math.fsum` so that the result does not depend on the order the
    apertures happen to be listed in — an ordinary sum of several hundred
    unequal areas does.

    Parameters
    ----------
    aperture_areas_m2
        Individual spherical aperture areas in square metres.
    grid_radius_m
        Grid radius ``R_grid`` in metres; strictly positive.

    Returns
    -------
    float
        The geometric transparency ``eta``, in ``[0, 1]``.

    Raises
    ------
    DeviceConfigurationError
        If the radius or any area violates its bound, or if the apertures
        together exceed the sphere.
    """
    areas = require_aperture_areas(
        "aperture_areas_m2", aperture_areas_m2, grid_radius_m
    )
    return math.fsum(areas) / sphere_area_m2(grid_radius_m)


def circular_aperture_radius_m(
    grid_radius_m: float,
    minimum_half_angle_rad: float,
    bridge_half_angle_rad: float,
) -> float:
    """Return the base radius of the largest circular aperture that fits.

    Equation 7 of the filed source. The half-angle to the nearest
    neighbouring aperture, less the half-angle the bridge between them
    consumes, is the angular radius of the largest circle the aperture
    admits.

    Parameters
    ----------
    grid_radius_m
        Grid radius ``R_grid`` in metres; strictly positive.
    minimum_half_angle_rad
        Half the angular distance to the closest neighbouring aperture,
        ``theta_min``.
    bridge_half_angle_rad
        Half-angle the bridge element subtends, ``alpha_bridge``.

    Returns
    -------
    float
        The base radius ``r_circ`` of the spherical cap, in metres.

    Raises
    ------
    DeviceConfigurationError
        If the bridge consumes the aperture, so that the remaining angle
        is not strictly positive, or if that angle exceeds a quarter
        turn, beyond which the cap base stops growing with it and the
        equation no longer describes the largest circle that fits.
    """
    require_positive("grid_radius_m", grid_radius_m)
    require_finite("minimum_half_angle_rad", minimum_half_angle_rad)
    require_finite("bridge_half_angle_rad", bridge_half_angle_rad)
    angle = minimum_half_angle_rad - bridge_half_angle_rad
    if angle <= 0.0:
        raise DeviceConfigurationError(
            "minimum_half_angle_rad: the bridge half-angle "
            f"{bridge_half_angle_rad!r} rad consumes an aperture of "
            f"{minimum_half_angle_rad!r} rad; no circle fits inside it"
        )
    if angle > QUARTER_TURN_RAD:
        raise DeviceConfigurationError(
            f"minimum_half_angle_rad: {minimum_half_angle_rad!r} rad less the "
            f"bridge leaves {angle!r} rad, beyond the quarter turn where the "
            "cap base radius stops growing with the angle"
        )
    return grid_radius_m * math.sin(angle)


def spherical_cap_area_m2(grid_radius_m: float, cap_base_radius_m: float) -> float:
    """Surface area of a spherical cap of the given base radius.

    Equation 8 of the filed source, in the form it prints: the polar
    angle is recovered from the base radius with an arcsine and the cap
    area follows from its cosine.

    Parameters
    ----------
    grid_radius_m
        Sphere radius ``R_grid`` in metres; strictly positive.
    cap_base_radius_m
        Base radius of the cap in metres; not negative and not larger
        than the sphere radius.

    Returns
    -------
    float
        The cap area in square metres.

    Raises
    ------
    DeviceConfigurationError
        If the base radius is negative or exceeds the sphere radius, at
        which point the arcsine has no real value.
    """
    require_positive("grid_radius_m", grid_radius_m)
    require_finite("cap_base_radius_m", cap_base_radius_m)
    if cap_base_radius_m < 0.0:
        raise DeviceConfigurationError(
            f"cap_base_radius_m: must not be negative, got {cap_base_radius_m!r}"
        )
    if cap_base_radius_m > grid_radius_m:
        raise DeviceConfigurationError(
            f"cap_base_radius_m: {cap_base_radius_m!r} m exceeds the sphere "
            f"radius {grid_radius_m!r} m"
        )
    polar_angle = math.asin(cap_base_radius_m / grid_radius_m)
    return 2.0 * math.pi * grid_radius_m * grid_radius_m * (1.0 - math.cos(polar_angle))


def circular_transparency(
    grid_radius_m: float,
    minimum_half_angles_rad: Sequence[float],
    bridge_half_angle_rad: float,
) -> float:
    """Transparency the grid would have with circular apertures.

    Equation 9 of the filed source, composed from equations 7 and 8 for
    each aperture in turn.

    Parameters
    ----------
    grid_radius_m
        Grid radius ``R_grid`` in metres; strictly positive.
    minimum_half_angles_rad
        One ``theta_min`` per aperture.
    bridge_half_angle_rad
        Half-angle the bridge element subtends, shared by every aperture.

    Returns
    -------
    float
        The circular transparency ``eta_circ``.

    Raises
    ------
    DeviceConfigurationError
        If no aperture is given, or if any aperture violates the bounds
        of equation 7.
    """
    if not minimum_half_angles_rad:
        raise DeviceConfigurationError(
            "minimum_half_angles_rad: must carry at least one aperture"
        )
    areas = [
        spherical_cap_area_m2(
            grid_radius_m,
            circular_aperture_radius_m(
                grid_radius_m, half_angle, bridge_half_angle_rad
            ),
        )
        for half_angle in minimum_half_angles_rad
    ]
    return math.fsum(areas) / sphere_area_m2(grid_radius_m)


def normalised_circular_transparency(circular: float, geometric: float) -> float:
    """Fraction of the aperture area the inscribed circles cover.

    Equation 10 of the filed source. It is exactly one for a grid whose
    apertures are already circles, and below one for polygonal apertures.

    Parameters
    ----------
    circular
        Circular transparency ``eta_circ``.
    geometric
        Geometric transparency ``eta``; strictly positive, since a grid
        that leaves nothing open has no ratio to report.

    Returns
    -------
    float
        The normalised circular transparency.

    Raises
    ------
    DeviceConfigurationError
        If either transparency is non-finite, if the geometric
        transparency is not strictly positive, or if the inscribed
        circles are said to cover more than the apertures they are
        inscribed in.
    """
    require_finite("circular", circular)
    require_positive("geometric", geometric)
    if circular > geometric:
        raise DeviceConfigurationError(
            f"circular: {circular!r} exceeds the geometric transparency "
            f"{geometric!r}; an inscribed circle cannot exceed its aperture"
        )
    return circular / geometric
