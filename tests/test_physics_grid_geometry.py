# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — spherical cathode grid geometry tests

"""Tests of the closed-form spherical cathode grid geometry."""

from __future__ import annotations

import math
from typing import cast

import pytest

from physics_fixtures import (
    PRINTED_BRIDGE_ANGLES_DEG,
    PRINTED_CORROBORATED_SYMMETRIC,
    PRINTED_FANCHER_APERTURES,
    PRINTED_FANCHER_RINGS,
    PRINTED_FIGURE11_APERTURES,
    PRINTED_FIGURE11_RINGS,
    PRINTED_GLOBE_FAMILY_RANGE,
    PRINTED_SYMMETRIC_GRIDS,
    degrees_rounded,
)
from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.physics.grid_geometry import (
    SYMMETRIC_GRIDS,
    bridge_half_angle_rad,
    globe_aperture_count,
    require_ring_count,
    symmetric_grid,
    symmetric_grid_aperture_angle_deg,
)


@pytest.mark.parametrize(
    ("thickness", "diameter", "printed"), PRINTED_BRIDGE_ANGLES_DEG
)
def test_printed_bridge_angles_are_recovered(
    thickness: float, diameter: float, printed: float
) -> None:
    """Each angle Table 2 prints follows from the ratio beside it."""
    assert degrees_rounded(bridge_half_angle_rad(thickness, diameter)) == printed


@pytest.mark.parametrize(
    ("thickness", "diameter", "printed"), PRINTED_BRIDGE_ANGLES_DEG
)
def test_the_printed_table_cannot_settle_the_form_of_equation_five(
    thickness: float, diameter: float, printed: float
) -> None:
    """Table 2 agrees with both readings of equation 5, so it settles neither.

    The implementation takes the tangent because the printed equation
    carries one. This test exists to record that the table is no
    corroboration of that choice: dropping the arctangent, which is what
    the paper's own text layer invites, reproduces all four printed
    angles to the digit. Anyone who later "simplifies" the tangent away
    will not be caught by the anchor above, and should be caught here.
    """
    small_angle = round(math.degrees(thickness / diameter), 3)
    assert small_angle == printed
    assert bridge_half_angle_rad(thickness, diameter) != thickness / diameter


def test_figure_eleven_aperture_count_is_recovered() -> None:
    """The aperture count Figure 11's caption prints follows from its rings."""
    latitude, longitude = PRINTED_FIGURE11_RINGS
    assert globe_aperture_count(latitude, longitude) == PRINTED_FIGURE11_APERTURES


@pytest.mark.parametrize(
    ("latitude", "longitude", "printed"), PRINTED_GLOBE_FAMILY_RANGE
)
def test_stated_globe_family_range_endpoints_are_recovered(
    latitude: int, longitude: int, printed: int
) -> None:
    """The 8-to-220 range the paper states for its globe family is exact."""
    assert globe_aperture_count(latitude, longitude) == printed


def test_fancher_cathode_aperture_count_is_recovered() -> None:
    """The one experimental grid whose count follows from equation 12.

    The paper's review cites four experimental grids with their ring
    counts and aperture counts. Only this one is reproduced by equation
    12; the other three are not, because the laboratories that built them
    counted meridians rather than rings. That is a property of the
    citations, not of the equation, and it is why the equation is
    anchored on the paper's own figure and stated range as well.
    """
    latitude, longitude = PRINTED_FANCHER_RINGS
    assert globe_aperture_count(latitude, longitude) == PRINTED_FANCHER_APERTURES


def test_globe_count_scales_as_the_equation_says() -> None:
    """Doubling the meridians doubles the apertures; a latitude adds a row."""
    base = globe_aperture_count(4, 5)
    assert globe_aperture_count(4, 10) == 2 * base
    assert globe_aperture_count(5, 5) - base == 2 * 5


def test_a_grid_of_bare_meridians_is_admitted() -> None:
    """Zero latitude rings is a stated bound of equation 12, not an error."""
    assert globe_aperture_count(0, 3) == 6


@pytest.mark.parametrize(
    ("rings", "apertures", "crossings", "angle"), PRINTED_SYMMETRIC_GRIDS
)
def test_symmetric_grid_table_is_reproduced(
    rings: int, apertures: int, crossings: int, angle: float
) -> None:
    """Every row of Table 3 is carried, and its angle follows from its rule."""
    grid = symmetric_grid(rings)
    assert grid.apertures == apertures
    assert grid.max_rings_in_crossing == crossings
    assert symmetric_grid_aperture_angle_deg(crossings) == angle


@pytest.mark.parametrize(("rings", "apertures"), PRINTED_CORROBORATED_SYMMETRIC)
def test_two_table_three_rows_are_corroborated_by_experiment(
    rings: int, apertures: int
) -> None:
    """Two rows are stated a second time, from two other laboratories."""
    assert symmetric_grid(rings).apertures == apertures


def test_symmetric_grids_are_tabulated_in_ascending_ring_order() -> None:
    """The table is ordered, and its crossing count rises with each row."""
    rings = [grid.rings for grid in SYMMETRIC_GRIDS]
    crossings = [grid.max_rings_in_crossing for grid in SYMMETRIC_GRIDS]
    assert rings == sorted(rings)
    assert crossings == list(range(2, 2 + len(SYMMETRIC_GRIDS)))


def test_every_symmetric_grid_names_its_polyhedron() -> None:
    """Each row carries the spherical polyhedron it projects."""
    for grid in SYMMETRIC_GRIDS:
        assert grid.spherical_polyhedron.startswith("spherical ")


def test_an_untabulated_ring_count_is_refused_not_extrapolated() -> None:
    """The pattern is not continued past the four permissible grids."""
    with pytest.raises(DeviceConfigurationError, match="no symmetric grid"):
        symmetric_grid(12)


def test_a_single_ring_crosses_nothing() -> None:
    """A symmetric grid needs at least two rings to cut an aperture."""
    with pytest.raises(DeviceConfigurationError, match="at least 2"):
        symmetric_grid_aperture_angle_deg(1)


def test_a_boolean_is_not_a_ring_count() -> None:
    """``True`` is an ``int`` in Python and must not pass as one ring."""
    with pytest.raises(DeviceConfigurationError, match="must be an integer"):
        require_ring_count("rings", value=True, minimum=0)


def test_a_float_is_not_a_ring_count() -> None:
    """A ring count is counted, never measured.

    The cast is deliberate. This guard exists for callers the annotation
    does not reach — a decoded JSON record, an untyped consumer — so the
    test has to hand it a value the annotation forbids.
    """
    measured = cast("int", 3.0)
    with pytest.raises(DeviceConfigurationError, match="must be an integer"):
        require_ring_count("rings", measured, 0)


def test_a_ring_count_below_its_floor_is_refused() -> None:
    """The rejection names the field and the floor it violated."""
    with pytest.raises(
        DeviceConfigurationError, match="longitude_rings: must be at least 1"
    ):
        globe_aperture_count(0, 0)


def test_a_negative_latitude_count_is_refused() -> None:
    """Latitude rings may be absent but never negative."""
    with pytest.raises(DeviceConfigurationError, match="latitude_rings"):
        globe_aperture_count(-1, 2)


@pytest.mark.parametrize(
    ("thickness", "diameter"), [(0.0, 0.2), (-0.001, 0.2), (0.001, 0.0)]
)
def test_a_bridge_angle_needs_two_positive_lengths(
    thickness: float, diameter: float
) -> None:
    """Neither length may be zero or negative."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        bridge_half_angle_rad(thickness, diameter)


def test_a_non_finite_length_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        bridge_half_angle_rad(math.nan, 0.2)
