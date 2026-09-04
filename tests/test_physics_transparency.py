# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — spherical cathode grid transparency tests

"""Tests of the published transparency metrics."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    RADEL_CATHODE_DIAMETER_M,
    RADEL_CATHODE_WIRE_DIAMETER_M,
    SYNTHETIC_GRID_TRANSPARENCY,
    circular_half_angles,
    equal_aperture_areas,
)
from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.physics.grid_geometry import bridge_half_angle_rad
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

GRID_RADIUS_M = RADEL_CATHODE_DIAMETER_M / 2.0
BRIDGE_RAD = bridge_half_angle_rad(
    RADEL_CATHODE_WIRE_DIAMETER_M, RADEL_CATHODE_DIAMETER_M
)
# Measured, not chosen: over 899 aperture angles spanning the admissible
# range, 282 disagree between the composed equations 7 and 8 and the
# single-step form, the worst by 8.4e-15 relative. The arcsine and the
# sine do not round-trip through every double.
COMPOSITION_TOLERANCE = 1.0e-13
# Measured: the equal-area construction is bit-exact for most aperture
# counts and one unit in the last place away for others, because
# eta * 4 pi R^2 / N does not always divide back to eta.
RECOVERY_TOLERANCE = 1.0e-15
# Measured over 499 radii: the closed hemisphere and equation 8 differ at
# every one of them by exactly one unit in the last place, at most
# 2.22e-16 relative.
HEMISPHERE_TOLERANCE = 1.0e-15


def test_sphere_area_is_the_closed_form() -> None:
    """The grid sphere's area is four pi r squared."""
    assert sphere_area_m2(2.0) == 4.0 * math.pi * 4.0


@pytest.mark.parametrize("apertures", [8, 24, 48, 50, 120, 640])
def test_a_declared_transparency_is_recovered_from_its_apertures(
    apertures: int,
) -> None:
    """Equation 6 returns the transparency the apertures were built for."""
    areas = equal_aperture_areas(apertures, GRID_RADIUS_M, SYNTHETIC_GRID_TRANSPARENCY)
    recovered = geometric_transparency(areas, GRID_RADIUS_M)
    assert math.isclose(
        recovered, SYNTHETIC_GRID_TRANSPARENCY, rel_tol=RECOVERY_TOLERANCE
    )


def test_the_transparency_does_not_depend_on_aperture_order() -> None:
    """Summing with fsum makes the result independent of the listing order.

    Several hundred unequal areas summed in the ordinary way do depend on
    their order. This is why equation 6 is evaluated with a compensated
    sum rather than the obvious one.
    """
    areas = tuple(1.0e-6 * (1.0 + index) for index in range(200))
    assert geometric_transparency(areas, GRID_RADIUS_M) == geometric_transparency(
        tuple(reversed(areas)), GRID_RADIUS_M
    )


def test_apertures_may_fill_the_whole_sphere() -> None:
    """A transparency of exactly one is the boundary, not a violation."""
    areas = equal_aperture_areas(4, GRID_RADIUS_M, 1.0)
    assert geometric_transparency(areas, GRID_RADIUS_M) == 1.0


def test_apertures_exceeding_their_sphere_are_refused() -> None:
    """A transparency above one measures something other than this sphere."""
    areas = equal_aperture_areas(4, GRID_RADIUS_M, 1.0)
    too_wide = (*areas, areas[0])
    with pytest.raises(DeviceConfigurationError, match="cannot exceed the sphere"):
        geometric_transparency(too_wide, GRID_RADIUS_M)


def test_a_grid_with_no_apertures_is_refused() -> None:
    """An empty aperture list describes a solid shell, not a grid."""
    with pytest.raises(DeviceConfigurationError, match="at least one aperture"):
        geometric_transparency((), GRID_RADIUS_M)


def test_a_negative_aperture_area_is_refused_by_index() -> None:
    """The rejection names which aperture is wrong."""
    with pytest.raises(DeviceConfigurationError, match=r"\[1\]: must not be negative"):
        require_aperture_areas("areas", (1.0e-4, -1.0e-4), GRID_RADIUS_M)


def test_a_non_finite_aperture_area_is_refused_by_index() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match=r"\[0\]: must be finite"):
        require_aperture_areas("areas", (math.inf,), GRID_RADIUS_M)


def test_a_zero_area_aperture_is_admitted() -> None:
    """An aperture a bridge has closed has zero area, which is not an error."""
    assert require_aperture_areas("areas", (0.0, 1.0e-4), GRID_RADIUS_M) == (
        0.0,
        1.0e-4,
    )


def test_the_bridge_may_not_consume_the_aperture() -> None:
    """An aperture no wider than its own bridge admits no circle."""
    with pytest.raises(DeviceConfigurationError, match="no circle fits"):
        circular_aperture_radius_m(GRID_RADIUS_M, BRIDGE_RAD, BRIDGE_RAD)


def test_an_aperture_beyond_a_quarter_turn_is_refused() -> None:
    """Past a quarter turn the cap base stops growing with the angle."""
    with pytest.raises(DeviceConfigurationError, match="beyond the quarter turn"):
        circular_aperture_radius_m(
            GRID_RADIUS_M, QUARTER_TURN_RAD + 2.0 * BRIDGE_RAD, BRIDGE_RAD
        )


def test_an_aperture_of_exactly_a_quarter_turn_is_admitted() -> None:
    """The quarter turn itself is the boundary and gives the full radius."""
    radius = circular_aperture_radius_m(
        GRID_RADIUS_M, QUARTER_TURN_RAD + BRIDGE_RAD, BRIDGE_RAD
    )
    assert math.isclose(radius, GRID_RADIUS_M, rel_tol=1.0e-15)


def test_a_non_finite_half_angle_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        circular_aperture_radius_m(GRID_RADIUS_M, math.nan, BRIDGE_RAD)


def test_a_non_finite_bridge_angle_is_refused() -> None:
    """The bridge half-angle is validated as well as the aperture's."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        circular_aperture_radius_m(GRID_RADIUS_M, 0.5, math.nan)


def test_a_cap_base_wider_than_its_sphere_is_refused() -> None:
    """Beyond the sphere radius the arcsine of equation 8 has no real value."""
    with pytest.raises(DeviceConfigurationError, match="exceeds the sphere radius"):
        spherical_cap_area_m2(GRID_RADIUS_M, GRID_RADIUS_M * 1.5)


def test_a_negative_cap_base_is_refused() -> None:
    """A cap base radius is a length."""
    with pytest.raises(DeviceConfigurationError, match="must not be negative"):
        spherical_cap_area_m2(GRID_RADIUS_M, -1.0e-3)


def test_a_hemisphere_cap_is_half_the_sphere() -> None:
    """A cap whose base is the sphere radius is a hemisphere, to one ulp.

    Not exactly. ``cos(asin(1))`` is 6.12e-17 rather than zero, so the
    bracket of equation 8 evaluates to 0.9999999999999999 and the cap
    lands one unit in the last place below half the sphere. Measured over
    499 radii the two disagree at every one of them, always by that same
    single place. An equality here would be a claim about the arithmetic
    that the arithmetic does not support.
    """
    for step in range(1, 20):
        radius = step / 20.0
        assert math.isclose(
            spherical_cap_area_m2(radius, radius),
            sphere_area_m2(radius) / 2.0,
            rel_tol=HEMISPHERE_TOLERANCE,
        )


def test_a_cap_of_zero_base_has_no_area() -> None:
    """A closed aperture contributes nothing."""
    assert spherical_cap_area_m2(GRID_RADIUS_M, 0.0) == 0.0


@pytest.mark.parametrize("steps", [7, 31, 101])
def test_equations_seven_and_eight_compose_to_the_single_step_form(steps: int) -> None:
    """Composing the two equations agrees with the angle they encode.

    Equation 8 recovers the polar angle from the base radius equation 7
    built out of it, so the pair reduces to one cosine of the same angle.
    They agree within a measured tolerance rather than exactly: the
    arcsine and the sine do not round-trip through every double.
    """
    for index in range(1, steps):
        angle = index * (QUARTER_TURN_RAD - BRIDGE_RAD) / steps
        composed = spherical_cap_area_m2(
            GRID_RADIUS_M,
            circular_aperture_radius_m(GRID_RADIUS_M, angle + BRIDGE_RAD, BRIDGE_RAD),
        )
        single = 2.0 * math.pi * GRID_RADIUS_M * GRID_RADIUS_M * (1.0 - math.cos(angle))
        assert math.isclose(composed, single, rel_tol=COMPOSITION_TOLERANCE)


def test_circular_apertures_normalise_to_exactly_one() -> None:
    """The identity the filed source states for circular apertures.

    A grid whose apertures already are the circles inscribed in them has
    a normalised circular transparency of one. Here that is exact rather
    than close: the same value is divided by itself.
    """
    half_angles = circular_half_angles(48, BRIDGE_RAD, 0.1)
    circular = circular_transparency(GRID_RADIUS_M, half_angles, BRIDGE_RAD)
    assert normalised_circular_transparency(circular, circular) == 1.0


def test_polygonal_apertures_normalise_below_one() -> None:
    """An inscribed circle covers less than the aperture around it."""
    half_angles = circular_half_angles(48, BRIDGE_RAD, 0.1)
    circular = circular_transparency(GRID_RADIUS_M, half_angles, BRIDGE_RAD)
    assert 0.0 < normalised_circular_transparency(circular * 1.2, circular * 1.2) <= 1.0
    assert normalised_circular_transparency(circular, circular * 1.2) < 1.0


def test_a_grid_with_no_half_angles_is_refused() -> None:
    """The circular transparency needs at least one aperture to sum."""
    with pytest.raises(DeviceConfigurationError, match="at least one aperture"):
        circular_transparency(GRID_RADIUS_M, (), BRIDGE_RAD)


def test_circular_transparency_grows_with_the_apertures() -> None:
    """Wider apertures leave more of the sphere open."""
    narrow = circular_transparency(
        GRID_RADIUS_M, circular_half_angles(48, BRIDGE_RAD, 0.05), BRIDGE_RAD
    )
    wide = circular_transparency(
        GRID_RADIUS_M, circular_half_angles(48, BRIDGE_RAD, 0.10), BRIDGE_RAD
    )
    assert narrow < wide


def test_an_inscribed_circle_cannot_exceed_its_aperture() -> None:
    """A circular transparency above the geometric one is refused."""
    with pytest.raises(DeviceConfigurationError, match="cannot exceed its aperture"):
        normalised_circular_transparency(0.9, 0.5)


def test_a_grid_that_leaves_nothing_open_has_no_ratio() -> None:
    """Dividing by a zero geometric transparency is refused, not returned."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        normalised_circular_transparency(0.0, 0.0)


def test_a_non_finite_circular_transparency_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        normalised_circular_transparency(math.nan, 0.5)
