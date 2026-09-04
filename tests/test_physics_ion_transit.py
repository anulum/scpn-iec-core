# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — ion transit tests

"""Tests of the ion recirculation bound."""

from __future__ import annotations

import math

import pytest

from scpn_iec_core.errors import DeviceConfigurationError
from scpn_iec_core.physics.ion_transit import maximum_ion_passes

# Measured over 20029 transparencies in the open interval: 7994 disagree
# between the printed 1 - eta**2 and the factored (1 - eta)(1 + eta), the
# worst by 5.5e-10 relative at eta = 0.99999999.
FORM_TOLERANCE = 1.0e-9


def test_the_relation_is_the_printed_ratio() -> None:
    """A transparency of 0.95 admits 0.95 / (1 - 0.95 squared) passes."""
    assert maximum_ion_passes(0.95) == pytest.approx(0.95 / (1.0 - 0.95**2))


@pytest.mark.parametrize("transparency", [0.5, 0.8, 0.9, 0.95, 0.99, 0.999])
def test_the_factored_denominator_agrees_with_the_printed_one(
    transparency: float,
) -> None:
    """Factoring the difference of squares is the same algebra.

    It is not the same floating-point computation. The implementation
    subtracts before squaring because ``1 - eta**2`` loses most of its
    significand as the transparency approaches one, and this test bounds
    the gap that choice opens against the form the source prints.
    """
    printed = transparency / (1.0 - transparency**2)
    assert math.isclose(
        maximum_ion_passes(transparency), printed, rel_tol=FORM_TOLERANCE
    )


def test_the_bound_rises_with_transparency() -> None:
    """A grid that intercepts less admits more passes."""
    values = [maximum_ion_passes(eta) for eta in (0.5, 0.7, 0.9, 0.99)]
    assert values == sorted(values)


def test_the_bound_grows_without_limit_towards_a_transparent_grid() -> None:
    """The relation diverges at one, which is why one is refused."""
    assert maximum_ion_passes(1.0 - 1.0e-12) > 1.0e11


def test_a_half_transparent_grid_admits_less_than_one_pass() -> None:
    """Below the golden section the bound falls under a single pass.

    ``eta / (1 - eta**2)`` equals one where ``eta**2 + eta - 1`` does, at
    the reciprocal golden ratio. The relation is an upper bound on
    geometry alone, so a value below one is not absurd: it says an ion
    is likelier than not to be intercepted on its first crossing.
    """
    reciprocal_golden = (math.sqrt(5.0) - 1.0) / 2.0
    assert maximum_ion_passes(reciprocal_golden * 0.9) < 1.0
    assert maximum_ion_passes(reciprocal_golden * 1.1) > 1.0


def test_a_virtual_cathode_bounds_no_passes() -> None:
    """The polywell's transparency of exactly one has no value here."""
    with pytest.raises(DeviceConfigurationError, match="strictly below one"):
        maximum_ion_passes(1.0)


def test_a_transparency_above_one_is_refused() -> None:
    """Nothing is more open than fully open."""
    with pytest.raises(DeviceConfigurationError, match="strictly below one"):
        maximum_ion_passes(1.5)


def test_a_solid_shell_passes_nothing() -> None:
    """A transparency of zero is refused rather than divided through."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        maximum_ion_passes(0.0)


def test_a_negative_transparency_is_refused() -> None:
    """A transparency is a fraction of an area."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        maximum_ion_passes(-0.1)


def test_a_non_finite_transparency_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        maximum_ion_passes(math.nan)
