# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — device capability package

"""Device capability models of the SCPN IEC device family.

Public surface of the ``device_configuration_model`` and
``diagnostic_clock_semantics`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, canonical
serialisation with SHA-256 digests, and data-only pins to the SPO
registries. No claim about any real machine or diagnostic is made
anywhere in this package.
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
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    ObservabilityBinding,
    ObservabilityClass,
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

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "CONFINEMENT_KINDS",
    "IEC_MIN_OPERATING_KV",
    "KIND_BY_IDENTIFIER",
    "OWNED_CONFIGURATIONS",
    "POLYWELL_MIN_COILS",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ConfinementStructure",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "ElectrostaticDrive",
    "ObservabilityBinding",
    "ObservabilityClass",
    "RegistryBinding",
    "SemanticCarrier",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "plan_from_bytes",
    "plan_from_record",
]
