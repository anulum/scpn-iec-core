# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — level-0 physics record

"""Level-0 physics record of one validated IEC configuration.

The record evaluates what the family's two configurations admit, and the
split between them is not a convenience — it is where the physics
divides. A ``gridded_iec`` device has a physical cathode: it has
apertures to count, a bridge angle to subtend and a transparency below
one, so the pass-count relation has a value. A ``polywell`` has a virtual
cathode formed by magnetic fields: its class invariant fixes the
transparency at exactly one, no grid is declared for it, and the
pass-count relation has no value there rather than a large one.

A grid declaration is therefore required for the gridded class and
refused for the polywell class, in both directions and by name.

Where the declaration carries measured aperture areas, the record
recomputes the geometric transparency from them and reports it beside
the transparency the configuration declares. Neither is derived from the
other. That is what lets a test show the declared transparency is
recoverable from the grid actually described, rather than merely stored
next to it.

Design record: ADR 0005.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Final

from scpn_iec_core.configuration import DeviceConfiguration
from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import require_positive
from scpn_iec_core.physics.grid_geometry import (
    GRID_KINDS,
    MIN_LATITUDE_RINGS,
    MIN_LONGITUDE_RINGS,
    bridge_half_angle_rad,
    globe_aperture_count,
    require_ring_count,
    symmetric_grid,
)
from scpn_iec_core.physics.ion_transit import maximum_ion_passes
from scpn_iec_core.physics.transparency import (
    circular_transparency,
    geometric_transparency,
    normalised_circular_transparency,
    require_aperture_areas,
)

LEVEL0_SCHEMA: Final = "scpn.iec-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published spherical cathode grid geometry "
        "on a declared grid, composed with the well the configuration carries"
    ),
    (
        "every relation is geometry or a ratio of areas; no particle "
        "transport, sheath, space-charge or fusion-rate calculation is "
        "performed"
    ),
    (
        "the aperture areas and neighbour half-angles are declared inputs "
        "measured off a grid model this repository does not build"
    ),
    (
        "the maximum pass count rests on transparency alone and sees no "
        "pressure, charge exchange, scattering or ion energy; it is an upper "
        "bound set by geometry, never a predicted pass count"
    ),
    (
        "the declared and recovered transparencies are reported side by side "
        "and neither is derived from the other"
    ),
    (
        "the polywell class carries no grid and no pass count; its virtual "
        "cathode is a declaration, not a field calculation performed here"
    ),
    (
        "no value describes or validates any real machine; an anchor "
        "reproduces a number a filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class CathodeGridDeclaration:
    """Declared geometry of one physical cathode grid.

    Parameters
    ----------
    kind
        Grid family: ``globe`` for a latitude/longitude cage, or
        ``symmetric`` for one of the four permissible great-circle
        configurations.
    grid_diameter_m
        Outer diameter of the grid in metres; strictly positive.
    bridge_thickness_m
        Thickness of the conductor between two neighbouring apertures, in
        metres; strictly positive.
    latitude_rings
        Latitude ring count of a globe grid; zero for a symmetric grid.
    longitude_rings
        Longitude ring count of a globe grid; zero for a symmetric grid.
    symmetric_rings
        Great-circle ring count of a symmetric grid; zero for a globe
        grid.
    aperture_areas_m2
        Optional measured area of each aperture, in square metres. When
        given there must be exactly one per aperture the ring counts
        imply.
    minimum_half_angles_rad
        Optional half-angle to the nearest neighbouring aperture, one per
        aperture. When given there must be exactly one per aperture the
        ring counts imply.

    Raises
    ------
    DeviceConfigurationError
        If the kind is unknown, if a ring count contradicts the kind, if
        a length is not strictly positive, or if an optional sequence
        does not carry exactly one entry per aperture.
    """

    kind: str
    grid_diameter_m: float
    bridge_thickness_m: float
    latitude_rings: int = 0
    longitude_rings: int = 0
    symmetric_rings: int = 0
    aperture_areas_m2: tuple[float, ...] | None = field(default=None)
    minimum_half_angles_rad: tuple[float, ...] | None = field(default=None)

    def __post_init__(self) -> None:
        """Validate the declaration's class invariants.

        Raises
        ------
        DeviceConfigurationError
            If the kind is unknown, if a ring count contradicts the kind,
            if a length is not strictly positive, or if an optional
            sequence is not one entry per aperture.
        """
        if self.kind not in GRID_KINDS:
            raise DeviceConfigurationError(
                f"kind: must be one of {GRID_KINDS!r}, got {self.kind!r}"
            )
        require_positive("grid_diameter_m", self.grid_diameter_m)
        require_positive("bridge_thickness_m", self.bridge_thickness_m)
        if self.bridge_thickness_m >= self.grid_diameter_m:
            raise DeviceConfigurationError(
                f"bridge_thickness_m: {self.bridge_thickness_m!r} m is not "
                f"smaller than the grid diameter {self.grid_diameter_m!r} m; "
                "a bridge that spans the grid leaves no aperture"
            )
        if self.kind == "globe":
            require_ring_count(
                "latitude_rings", self.latitude_rings, MIN_LATITUDE_RINGS
            )
            require_ring_count(
                "longitude_rings", self.longitude_rings, MIN_LONGITUDE_RINGS
            )
            if self.symmetric_rings != 0:
                raise DeviceConfigurationError(
                    "symmetric_rings: a globe grid declares no great-circle "
                    f"ring count, got {self.symmetric_rings!r}"
                )
        else:
            symmetric_grid(self.symmetric_rings)
            if self.latitude_rings != 0 or self.longitude_rings != 0:
                raise DeviceConfigurationError(
                    "latitude_rings, longitude_rings: a symmetric grid "
                    "declares neither, got "
                    f"{self.latitude_rings!r} and {self.longitude_rings!r}"
                )
        expected = self.aperture_count()
        self._require_per_aperture(
            "aperture_areas_m2", self.aperture_areas_m2, expected
        )
        self._require_per_aperture(
            "minimum_half_angles_rad", self.minimum_half_angles_rad, expected
        )

    @staticmethod
    def _require_per_aperture(
        name: str, values: tuple[float, ...] | None, expected: int
    ) -> None:
        """Refuse an optional sequence that is not one entry per aperture.

        Parameters
        ----------
        name
            Field name reported in the rejection message.
        values
            The optional sequence, or ``None`` when not declared.
        expected
            Aperture count the ring counts imply.

        Raises
        ------
        DeviceConfigurationError
            If the sequence is present and of a different length. The
            mismatch is refused rather than truncated or padded: a per-
            aperture measurement that does not match the grid it is said
            to describe measures a different grid.
        """
        if values is None:
            return
        if len(values) != expected:
            raise DeviceConfigurationError(
                f"{name}: carries {len(values)} entries for a grid of "
                f"{expected} apertures"
            )

    def aperture_count(self) -> int:
        """Return the number of apertures the declared ring counts imply.

        Returns
        -------
        int
            Equation 12 of the filed source for a globe grid, or the
            tabulated count for a symmetric one.
        """
        if self.kind == "globe":
            return globe_aperture_count(self.latitude_rings, self.longitude_rings)
        return symmetric_grid(self.symmetric_rings).apertures

    def grid_radius_m(self) -> float:
        """Radius of the declared grid.

        Returns
        -------
        float
            Half the declared diameter, in metres.
        """
        return self.grid_diameter_m / 2.0

    def bridge_half_angle_rad(self) -> float:
        """Half-angle the declared bridge element subtends.

        Returns
        -------
        float
            Equation 5 of the filed source, in radians.
        """
        return bridge_half_angle_rad(self.bridge_thickness_m, self.grid_diameter_m)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field; the optional sequences appear as
            lists or as ``null``.
        """
        return {
            "kind": self.kind,
            "grid_diameter_m": self.grid_diameter_m,
            "bridge_thickness_m": self.bridge_thickness_m,
            "latitude_rings": self.latitude_rings,
            "longitude_rings": self.longitude_rings,
            "symmetric_rings": self.symmetric_rings,
            "aperture_areas_m2": (
                None if self.aperture_areas_m2 is None else list(self.aperture_areas_m2)
            ),
            "minimum_half_angles_rad": (
                None
                if self.minimum_half_angles_rad is None
                else list(self.minimum_half_angles_rad)
            ),
        }


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Composed level-0 operating point of one configuration.

    Parameters
    ----------
    max_ion_energy_kev
        Maximum singly-charged ion energy of the electrostatic well.
    declared_grid_transparency
        Cathode grid transparency the configuration declares.
    maximum_ion_passes
        Geometric upper bound on ion passes, or ``None`` for the
        polywell class, whose virtual cathode bounds none.
    aperture_count
        Apertures the declared grid carries, or ``None`` when no grid is
        declared.
    bridge_half_angle_rad
        Half-angle the declared bridge subtends, or ``None`` when no grid
        is declared.
    recovered_geometric_transparency
        Transparency recomputed from the declared aperture areas, or
        ``None`` when they were not declared.
    circular_transparency
        Transparency the grid would have with circular apertures, or
        ``None`` when the neighbour half-angles were not declared.
    normalised_circular_transparency
        Ratio of the circular to the declared transparency, or ``None``
        when the circular transparency is.
    """

    max_ion_energy_kev: float
    declared_grid_transparency: float
    maximum_ion_passes: float | None
    aperture_count: int | None
    bridge_half_angle_rad: float | None
    recovered_geometric_transparency: float | None
    circular_transparency: float | None
    normalised_circular_transparency: float | None

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "max_ion_energy_kev": self.max_ion_energy_kev,
            "declared_grid_transparency": self.declared_grid_transparency,
            "maximum_ion_passes": self.maximum_ion_passes,
            "aperture_count": self.aperture_count,
            "bridge_half_angle_rad": self.bridge_half_angle_rad,
            "recovered_geometric_transparency": (self.recovered_geometric_transparency),
            "circular_transparency": self.circular_transparency,
            "normalised_circular_transparency": (self.normalised_circular_transparency),
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    grid
        The declared cathode grid, or ``None`` for the polywell class.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    grid: CathodeGridDeclaration | None
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "grid": None if self.grid is None else self.grid.to_record(),
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def require_grid_for_class(
    configuration: DeviceConfiguration, grid: CathodeGridDeclaration | None
) -> None:
    """Refuse a grid declaration that contradicts the confinement class.

    Parameters
    ----------
    configuration
        Validated IEC configuration.
    grid
        The declared cathode grid, or ``None``.

    Raises
    ------
    DeviceConfigurationError
        If a gridded configuration is given no grid, or a polywell
        configuration is given one. Both directions are refused: a
        physical cathode that is not described cannot be measured, and a
        virtual cathode that is described is described as something it is
        not.
    """
    gridded = configuration.confinement.kind == "gridded"
    if gridded and grid is None:
        raise DeviceConfigurationError(
            f"grid: {configuration.identifier} has a physical cathode and "
            "requires a grid declaration"
        )
    if not gridded and grid is not None:
        raise DeviceConfigurationError(
            f"grid: {configuration.identifier} forms a virtual cathode and "
            "admits no grid declaration"
        )


def level0_physics(
    configuration: DeviceConfiguration, grid: CathodeGridDeclaration | None = None
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated IEC configuration. It supplies the well voltage and the
        declared cathode grid transparency.
    grid
        Declared cathode grid geometry. Required for the gridded class
        and refused for the polywell class.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If the grid declaration contradicts the confinement class, or if
        a declared value leaves its documented interval; the refusals
        name the field.
    """
    require_grid_for_class(configuration, grid)
    declared = configuration.confinement.cathode_grid_transparency
    passes = None if grid is None else maximum_ion_passes(declared)
    recovered: float | None = None
    circular: float | None = None
    normalised: float | None = None
    if grid is not None:
        radius = grid.grid_radius_m()
        if grid.aperture_areas_m2 is not None:
            recovered = geometric_transparency(
                require_aperture_areas(
                    "aperture_areas_m2", grid.aperture_areas_m2, radius
                ),
                radius,
            )
        if grid.minimum_half_angles_rad is not None:
            circular = circular_transparency(
                radius, grid.minimum_half_angles_rad, grid.bridge_half_angle_rad()
            )
            normalised = normalised_circular_transparency(circular, declared)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        grid=grid,
        operating_point=OperatingPoint(
            max_ion_energy_kev=configuration.drive.max_ion_energy_kev(),
            declared_grid_transparency=declared,
            maximum_ion_passes=passes,
            aperture_count=None if grid is None else grid.aperture_count(),
            bridge_half_angle_rad=(
                None if grid is None else grid.bridge_half_angle_rad()
            ),
            recovered_geometric_transparency=recovered,
            circular_transparency=circular,
            normalised_circular_transparency=normalised,
        ),
    )
