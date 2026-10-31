# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN IEC Core — installed-wheel contract check tests

"""Every finding of the installed-wheel check fires on its fault.

The hosted installed-wheel job runs the check against a real wheel in a
clean environment. These tests prove, in the development environment,
that each check reports its fault: a package imported from the checkout,
a missing ``py.typed`` marker, absent or mismatched metadata, and that the
public path passes on the committed fixture.
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path

import pytest
from installed_package_check import (
    CONFIGURATION_DOCUMENT,
    check_installed,
    failed,
    layout_findings,
    main,
    metadata_findings,
    public_path_findings,
    report,
)

from scpn_iec_core import configuration_from_bytes

REPO = Path(__file__).resolve().parents[1]


def test_layout_accepts_an_installed_package_with_its_marker(tmp_path: Path) -> None:
    """A package outside the checkout that ships py.typed passes."""
    package = tmp_path / "site-packages" / "scpn_iec_core"
    package.mkdir(parents=True)
    (package / "py.typed").write_text("", encoding="utf-8")
    assert layout_findings(package, REPO) == []


def test_layout_rejects_checkout_import_and_omitted_marker(tmp_path: Path) -> None:
    """A checkout import and a wheel without py.typed are both findings."""
    package = tmp_path / "scpn_iec_core"
    package.mkdir()
    findings = layout_findings(package, tmp_path)
    assert any("imported from the checkout" in item for item in findings)
    assert any("no py.typed" in item for item in findings)


def test_metadata_reports_a_missing_distribution() -> None:
    """An absent distribution is a finding, not an exception."""
    assert metadata_findings("1", "no-such-distribution-for-this-test") == [
        "no-such-distribution-for-this-test is not installed"
    ]


def test_metadata_checks_version_and_requirements() -> None:
    """A real distribution passes or fails on exact metadata."""
    version = importlib.metadata.version("sortedcontainers")
    assert metadata_findings(version, "sortedcontainers") == []
    findings = metadata_findings("0.0.0", "hypothesis")
    assert any("installed version" in item for item in findings)
    assert any("declares runtime requirements" in item for item in findings)


def test_failed_keeps_only_false_checks_in_order() -> None:
    """Only the messages of failed checks are returned."""
    assert failed([(True, "a"), (False, "b"), (False, "c")]) == ["b", "c"]


def test_configuration_document_is_canonical() -> None:
    """The embedded document is the canonical form of a valid configuration."""
    configuration = configuration_from_bytes(CONFIGURATION_DOCUMENT)
    assert configuration.canonical_bytes() == CONFIGURATION_DOCUMENT


def test_public_path_passes_on_the_committed_fixture() -> None:
    """Configuration, plan and envelope round-trip and verify."""
    assert public_path_findings(REPO) == []


def test_check_from_the_checkout_fails(capsys: pytest.CaptureFixture[str]) -> None:
    """Run from the source tree, the check refuses the checkout import."""
    findings = check_installed(REPO)
    assert any("imported from the checkout" in item for item in findings)
    assert main(["--checkout", str(REPO)]) == 1
    assert "installed-package: FAIL" in capsys.readouterr().err


def test_report_exit_status(capsys: pytest.CaptureFixture[str]) -> None:
    """No findings is a pass; any finding is a failure with its reasons."""
    assert report([]) == 0
    assert "installed-package: PASS" in capsys.readouterr().out
    assert report(["x"]) == 1
    assert "  - x" in capsys.readouterr().err
