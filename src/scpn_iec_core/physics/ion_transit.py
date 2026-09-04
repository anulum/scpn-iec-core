# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — ion transit through a physical cathode grid

"""Ion recirculation through a physical cathode grid.

One relation, the estimate of how many passes an ion can make through a
grid before it is intercepted, taken from equation 1 of Wulfkühler et
al., *Scientific Reports* **14**:2261 (2024), which cites it as an often
quoted result resting on the transparency alone.

It rests on the transparency alone, and that is the whole of its
applicability. It knows nothing about pressure, charge exchange, angular
scattering or the ion's energy, and the same source states plainly that
most IEC devices operate in a pressure range where an ion makes only a
few passes before charge exchange ends its life — a limit this relation
cannot see. Treat it as an upper bound set by geometry, never as a
predicted pass count.

The denominator is evaluated as ``(1 - eta) * (1 + eta)`` rather than as
the printed ``1 - eta**2``. The two are the same algebra and not the same
floating-point computation: over a sweep of 20029 transparencies in the
open interval, 7994 disagree, the worst by 5.5e-10 relative at
``eta = 0.99999999``, where subtracting a square from one cancels most of
the significand. Factoring subtracts before squaring and keeps the digits.
A test measures that gap rather than asserting the two forms are equal.

The relation is undefined for a transparency of one, and that is not an
edge case to paper over: it is exactly the polywell class, whose virtual
cathode intercepts nothing. A grid that intercepts nothing bounds no
number of passes, so the value is refused rather than returned as an
infinity.
"""

from __future__ import annotations

from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.parameters import require_finite


def maximum_ion_passes(transparency: float) -> float:
    """Estimate the passes an ion may make through a grid of that transparency.

    Equation 1 of the filed source, ``eta / (1 - eta**2)``.

    Parameters
    ----------
    transparency
        Geometric transparency ``eta`` of the cathode grid, strictly
        inside ``(0, 1)``.

    Returns
    -------
    float
        The estimated maximum number of passes.

    Raises
    ------
    DeviceConfigurationError
        If the transparency is non-finite, or outside ``(0, 1)``. A
        transparency of exactly one is the polywell's virtual cathode,
        for which this relation has no value; a transparency of zero is a
        solid shell, through which nothing passes at all.
    """
    require_finite("transparency", transparency)
    if transparency <= 0.0:
        raise DeviceConfigurationError(
            "transparency: must be strictly positive for a physical grid, "
            f"got {transparency!r}; a grid of zero transparency is a solid "
            "shell and passes nothing"
        )
    if transparency >= 1.0:
        raise DeviceConfigurationError(
            "transparency: must be strictly below one, got "
            f"{transparency!r}; a cathode that intercepts nothing bounds no "
            "number of passes, which is the polywell class rather than a "
            "value this relation can report"
        )
    return transparency / ((1.0 - transparency) * (1.0 + transparency))
