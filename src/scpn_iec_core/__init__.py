# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — device configuration model package

"""Device configuration model of the SCPN IEC device family.

Public surface of the ``device_configuration_model`` capability at
``computational_prototype`` maturity: validated parameter objects,
documented consistency estimates, canonical serialisation with SHA-256
digests, and a data-only pin to the SPO reactor registry. No claim about
any real machine is made anywhere in this package.
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
from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import (
    CONFINEMENT_KINDS,
    POLYWELL_MIN_COILS,
    ConfinementStructure,
    ElectrostaticDrive,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "CONFINEMENT_KINDS",
    "IEC_MIN_OPERATING_KV",
    "KIND_BY_IDENTIFIER",
    "OWNED_CONFIGURATIONS",
    "POLYWELL_MIN_COILS",
    "ConfinementStructure",
    "ConsistencyFinding",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "ElectrostaticDrive",
    "RegistryBinding",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
]
