# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — level-0 physics record tests

"""Tests of the composed level-0 physics record."""

from __future__ import annotations

import json
import math

import pytest

from physics_fixtures import (
    RADEL_CATHODE_DIAMETER_M,
    RADEL_CATHODE_WIRE_DIAMETER_M,
    RADEL_SYMMETRIC_CATHODE_RINGS,
    SYNTHETIC_GRID_TRANSPARENCY,
    SYNTHETIC_WELL_VOLTAGE_KV,
    anchor_configuration,
    anchor_grid,
    circular_half_angles,
    equal_aperture_areas,
    polywell_configuration,
)
from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.physics.grid_geometry import bridge_half_angle_rad
from scpn_iec_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CathodeGridDeclaration,
    level0_physics,
    require_grid_for_class,
)

# The equal-area construction is bit-exact for most aperture counts and one
# unit in the last place away for others; 48 is one of the latter.
RECOVERY_TOLERANCE = 1.0e-15
WISCONSIN_SYMMETRIC_APERTURES = 48


def globe_grid(
    *,
    kind: str = "globe",
    grid_diameter_m: float = RADEL_CATHODE_DIAMETER_M,
    bridge_thickness_m: float = RADEL_CATHODE_WIRE_DIAMETER_M,
    latitude_rings: int = 4,
    longitude_rings: int = 5,
    aperture_areas_m2: tuple[float, ...] | None = None,
    minimum_half_angles_rad: tuple[float, ...] | None = None,
) -> CathodeGridDeclaration:
    """Build a globe grid declaration, overriding one field at a time.

    Every parameter is named and typed rather than collected into a
    mapping and splatted, so a test that passes the wrong kind of value
    is caught where it is written instead of at run time.

    Parameters
    ----------
    kind
        Grid family.
    grid_diameter_m
        Outer diameter of the grid in metres.
    bridge_thickness_m
        Bridge element thickness in metres.
    latitude_rings
        Latitude ring count.
    longitude_rings
        Longitude ring count.
    aperture_areas_m2
        Optional per-aperture areas.
    minimum_half_angles_rad
        Optional per-aperture neighbour half-angles.

    Returns
    -------
    CathodeGridDeclaration
        The declared grid.
    """
    return CathodeGridDeclaration(
        kind=kind,
        grid_diameter_m=grid_diameter_m,
        bridge_thickness_m=bridge_thickness_m,
        latitude_rings=latitude_rings,
        longitude_rings=longitude_rings,
        aperture_areas_m2=aperture_areas_m2,
        minimum_half_angles_rad=minimum_half_angles_rad,
    )


def test_the_wisconsin_cathode_aperture_count_crosses_two_sources() -> None:
    """A nine-ring symmetric cathode reports the count the table prints.

    One filed source states that the University of Wisconsin device was
    operated with a nine-ring symmetric cathode. A second, independent
    source tabulates a nine-ring symmetric grid as carrying 48 apertures,
    and states the same figure again where it reviews another
    laboratory's grid. The record built from the first source's device
    reports the second source's number, which is what makes it an anchor
    rather than a value stored beside one.
    """
    record = level0_physics(anchor_configuration(), anchor_grid())
    assert record.grid is not None
    assert record.grid.symmetric_rings == RADEL_SYMMETRIC_CATHODE_RINGS
    assert record.operating_point.aperture_count == WISCONSIN_SYMMETRIC_APERTURES


def test_the_declared_transparency_is_recoverable_from_the_apertures() -> None:
    """The record recomputes the transparency instead of echoing it.

    Both numbers are reported and neither is derived from the other; the
    test is what says they agree.
    """
    point = level0_physics(anchor_configuration(), anchor_grid()).operating_point
    assert point.declared_grid_transparency == SYNTHETIC_GRID_TRANSPARENCY
    assert point.recovered_geometric_transparency is not None
    assert math.isclose(
        point.recovered_geometric_transparency,
        point.declared_grid_transparency,
        rel_tol=RECOVERY_TOLERANCE,
    )


def test_a_disagreeing_measurement_is_reported_not_reconciled() -> None:
    """Widening the apertures moves the recovered value and not the declared.

    The record would be worthless as evidence if it silently replaced one
    with the other, so this test moves one and watches the other stand
    still.
    """
    radius = RADEL_CATHODE_DIAMETER_M / 2.0
    wider = equal_aperture_areas(WISCONSIN_SYMMETRIC_APERTURES, radius, 0.80)
    grid = CathodeGridDeclaration(
        kind="symmetric",
        grid_diameter_m=RADEL_CATHODE_DIAMETER_M,
        bridge_thickness_m=RADEL_CATHODE_WIRE_DIAMETER_M,
        symmetric_rings=RADEL_SYMMETRIC_CATHODE_RINGS,
        aperture_areas_m2=wider,
    )
    point = level0_physics(anchor_configuration(), grid).operating_point
    assert point.declared_grid_transparency == SYNTHETIC_GRID_TRANSPARENCY
    assert point.recovered_geometric_transparency == pytest.approx(0.80)


def test_the_well_voltage_reaches_the_record_as_an_ion_energy() -> None:
    """A singly-charged ion gains the well voltage in kiloelectronvolts."""
    point = level0_physics(anchor_configuration(), anchor_grid()).operating_point
    assert point.max_ion_energy_kev == SYNTHETIC_WELL_VOLTAGE_KV


def test_the_pass_bound_follows_the_declared_transparency() -> None:
    """The gridded class carries a pass bound computed from its own grid."""
    point = level0_physics(anchor_configuration(), anchor_grid()).operating_point
    assert point.maximum_ion_passes == pytest.approx(
        SYNTHETIC_GRID_TRANSPARENCY / (1.0 - SYNTHETIC_GRID_TRANSPARENCY**2)
    )


def test_the_bridge_angle_reaches_the_record() -> None:
    """The record carries the half-angle the declared wire subtends."""
    point = level0_physics(anchor_configuration(), anchor_grid()).operating_point
    assert point.bridge_half_angle_rad == bridge_half_angle_rad(
        RADEL_CATHODE_WIRE_DIAMETER_M, RADEL_CATHODE_DIAMETER_M
    )


def test_a_polywell_carries_no_grid_and_no_pass_bound() -> None:
    """Where the cathode is virtual, the grid relations have no value.

    This is the family's physics dividing, not a missing field: a
    transparency of exactly one is the polywell's class invariant, and
    the pass relation diverges there.
    """
    record = level0_physics(polywell_configuration())
    point = record.operating_point
    assert record.grid is None
    assert point.declared_grid_transparency == 1.0
    assert point.maximum_ion_passes is None
    assert point.aperture_count is None
    assert point.bridge_half_angle_rad is None
    assert point.recovered_geometric_transparency is None
    assert point.circular_transparency is None
    assert point.normalised_circular_transparency is None


def test_a_physical_cathode_must_be_described() -> None:
    """A gridded configuration without a grid declaration is refused."""
    with pytest.raises(DeviceConfigurationError, match="requires a grid declaration"):
        level0_physics(anchor_configuration())


def test_a_virtual_cathode_admits_no_grid() -> None:
    """The refusal runs in both directions."""
    with pytest.raises(DeviceConfigurationError, match="admits no grid declaration"):
        level0_physics(polywell_configuration(), anchor_grid())


def test_both_admissible_pairings_are_accepted() -> None:
    """The guard passes exactly the two pairings the family has."""
    require_grid_for_class(anchor_configuration(), anchor_grid())
    require_grid_for_class(polywell_configuration(), None)


def test_a_grid_without_measurements_still_yields_a_record() -> None:
    """Aperture areas and neighbour angles are optional, and stay optional."""
    point = level0_physics(
        anchor_configuration(), anchor_grid(with_areas=False)
    ).operating_point
    assert point.aperture_count == WISCONSIN_SYMMETRIC_APERTURES
    assert point.recovered_geometric_transparency is None
    assert point.circular_transparency is None
    assert point.normalised_circular_transparency is None


def test_declared_neighbour_angles_add_the_circular_metrics() -> None:
    """Equations 9 and 10 appear once the half-angles are declared."""
    bridge = bridge_half_angle_rad(
        RADEL_CATHODE_WIRE_DIAMETER_M, RADEL_CATHODE_DIAMETER_M
    )
    grid = CathodeGridDeclaration(
        kind="symmetric",
        grid_diameter_m=RADEL_CATHODE_DIAMETER_M,
        bridge_thickness_m=RADEL_CATHODE_WIRE_DIAMETER_M,
        symmetric_rings=RADEL_SYMMETRIC_CATHODE_RINGS,
        minimum_half_angles_rad=circular_half_angles(
            WISCONSIN_SYMMETRIC_APERTURES, bridge, 0.20
        ),
    )
    point = level0_physics(anchor_configuration(), grid).operating_point
    assert point.circular_transparency is not None
    assert point.normalised_circular_transparency is not None
    assert point.normalised_circular_transparency == pytest.approx(
        point.circular_transparency / SYNTHETIC_GRID_TRANSPARENCY
    )


def test_a_globe_grid_counts_its_apertures_from_its_rings() -> None:
    """The globe branch of the declaration uses equation 12."""
    point = level0_physics(anchor_configuration(), globe_grid()).operating_point
    assert point.aperture_count == 50


def test_a_globe_grid_declares_no_great_circle_rings() -> None:
    """The two grid families do not share a ring count."""
    with pytest.raises(DeviceConfigurationError, match="symmetric_rings"):
        CathodeGridDeclaration(
            kind="globe",
            grid_diameter_m=RADEL_CATHODE_DIAMETER_M,
            bridge_thickness_m=RADEL_CATHODE_WIRE_DIAMETER_M,
            latitude_rings=4,
            longitude_rings=5,
            symmetric_rings=9,
        )


def test_a_symmetric_grid_declares_no_latitudes_or_longitudes() -> None:
    """The refusal runs in the other direction too."""
    with pytest.raises(
        DeviceConfigurationError, match="latitude_rings, longitude_rings"
    ):
        CathodeGridDeclaration(
            kind="symmetric",
            grid_diameter_m=RADEL_CATHODE_DIAMETER_M,
            bridge_thickness_m=RADEL_CATHODE_WIRE_DIAMETER_M,
            symmetric_rings=9,
            latitude_rings=4,
        )


def test_an_unknown_grid_family_is_refused() -> None:
    """Only the two published families are admitted."""
    with pytest.raises(DeviceConfigurationError, match="kind: must be one of"):
        globe_grid(kind="buckyball")


def test_a_bridge_that_spans_the_grid_is_refused() -> None:
    """A bridge as thick as the grid leaves no aperture to subtend."""
    with pytest.raises(DeviceConfigurationError, match="leaves no aperture"):
        globe_grid(bridge_thickness_m=RADEL_CATHODE_DIAMETER_M)


def test_a_grid_needs_a_positive_diameter() -> None:
    """Both declared lengths are validated where they are declared."""
    with pytest.raises(DeviceConfigurationError, match="grid_diameter_m"):
        globe_grid(grid_diameter_m=0.0)


def test_a_grid_needs_a_positive_bridge() -> None:
    """A grid of zero-thickness conductor is not a grid."""
    with pytest.raises(DeviceConfigurationError, match="bridge_thickness_m"):
        globe_grid(bridge_thickness_m=0.0)


@pytest.mark.parametrize("field_name", ["aperture_areas_m2", "minimum_half_angles_rad"])
def test_a_measurement_of_the_wrong_grid_is_refused(field_name: str) -> None:
    """One entry per aperture, or the measurement describes another grid.

    Parameters
    ----------
    field_name
        Which optional per-aperture sequence carries the wrong length.
    """
    wrong = (0.1, 0.2, 0.3)
    areas = wrong if field_name == "aperture_areas_m2" else None
    angles = wrong if field_name == "minimum_half_angles_rad" else None
    with pytest.raises(DeviceConfigurationError, match=f"{field_name}: carries 3"):
        globe_grid(aperture_areas_m2=areas, minimum_half_angles_rad=angles)


def test_the_grid_radius_is_half_the_declared_diameter() -> None:
    """The declaration carries a diameter and the equations want a radius."""
    assert anchor_grid().grid_radius_m() == RADEL_CATHODE_DIAMETER_M / 2.0


def test_the_record_serialises_canonically() -> None:
    """Sorted keys, no NaN, one trailing newline, and a stable digest."""
    record = level0_physics(anchor_configuration(), anchor_grid())
    raw = record.canonical_bytes()
    assert raw.endswith(b"\n")
    decoded = json.loads(raw.decode("utf-8"))
    assert decoded["schema"] == LEVEL0_SCHEMA
    assert decoded["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert decoded["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert list(decoded) == sorted(decoded)
    assert (
        record.digest_sha256()
        == level0_physics(anchor_configuration(), anchor_grid()).digest_sha256()
    )


def test_the_polywell_record_serialises_without_a_grid() -> None:
    """A record with no grid carries an explicit null, not a missing key."""
    decoded = json.loads(
        level0_physics(polywell_configuration()).canonical_bytes().decode("utf-8")
    )
    assert decoded["grid"] is None
    assert decoded["operating_point"]["maximum_ion_passes"] is None


def test_the_grid_record_carries_every_declared_field() -> None:
    """The declaration projects itself completely, optionals included."""
    projected = anchor_grid().to_record()
    assert projected["kind"] == "symmetric"
    assert projected["symmetric_rings"] == RADEL_SYMMETRIC_CATHODE_RINGS
    assert projected["minimum_half_angles_rad"] is None
    areas = projected["aperture_areas_m2"]
    assert isinstance(areas, list)
    assert len(areas) == WISCONSIN_SYMMETRIC_APERTURES


def test_a_different_grid_gives_a_different_digest() -> None:
    """The digest identifies the grid, not only the configuration."""
    first = level0_physics(anchor_configuration(), anchor_grid())
    second = level0_physics(anchor_configuration(), globe_grid())
    assert first.digest_sha256() != second.digest_sha256()


def test_the_non_claims_are_carried_verbatim() -> None:
    """Every non-claim reaches the record, and none is empty."""
    assert len(LEVEL0_NON_CLAIMS) == len(set(LEVEL0_NON_CLAIMS))
    for statement in LEVEL0_NON_CLAIMS:
        assert statement.strip() == statement
        assert statement
