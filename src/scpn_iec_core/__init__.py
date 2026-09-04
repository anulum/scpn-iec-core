# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — device capability package

"""Device capability models of the SCPN IEC device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics`` and ``level0_device_physics``
capabilities at ``computational_prototype`` maturity: validated
parameter objects, synthetic diagnostic and clock declarations aligned
with the pinned SPO observability catalogue, the published closed-form
geometry of a spherical cathode grid evaluated on a declared grid,
documented consistency estimates, canonical serialisation with SHA-256
digests, and data-only pins to the SPO registries. No claim about any
real machine or diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_iec_core.configuration import (
    IEC_MIN_OPERATING_KV,
    KIND_BY_IDENTIFIER,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_iec_core.errors import DeviceConfigurationError, DiagnosticPlanError
from scpn_iec_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_iec_core.parameters import (
    CONFINEMENT_KINDS,
    POLYWELL_MIN_COILS,
    ConfinementStructure,
    ElectrostaticDrive,
)
from scpn_iec_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    SYMMETRIC_GRIDS,
    CathodeGridDeclaration,
    Level0Physics,
    OperatingPoint,
    SymmetricGrid,
    bridge_half_angle_rad,
    circular_aperture_radius_m,
    circular_transparency,
    geometric_transparency,
    globe_aperture_count,
    level0_physics,
    maximum_ion_passes,
    normalised_circular_transparency,
    spherical_cap_area_m2,
    symmetric_grid,
    symmetric_grid_aperture_angle_deg,
)
from scpn_iec_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "CONFINEMENT_KINDS",
    "IEC_MIN_OPERATING_KV",
    "KIND_BY_IDENTIFIER",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "POLYWELL_MIN_COILS",
    "SYMMETRIC_GRIDS",
    "CandidateProfile",
    "CathodeGridDeclaration",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConfinementStructure",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "ElectrostaticDrive",
    "FrameKind",
    "Level0Physics",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "SymmetricGrid",
    "__version__",
    "bridge_half_angle_rad",
    "circular_aperture_radius_m",
    "circular_transparency",
    "configuration_from_bytes",
    "configuration_from_record",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "geometric_transparency",
    "globe_aperture_count",
    "level0_physics",
    "maximum_ion_passes",
    "normalised_circular_transparency",
    "plan_from_bytes",
    "plan_from_record",
    "spherical_cap_area_m2",
    "symmetric_grid",
    "symmetric_grid_aperture_angle_deg",
    "verify_envelope",
]
