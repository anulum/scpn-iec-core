<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — Architecture summary
-->

# Architecture summary

`SCPN-IEC-CORE` is the device-family owner for inertial electrostatic
confinement systems (gridded fusor and Polywell) inside the SCPN Reactor
Systems Research Group. The repository is currently `architecture_only`: it
defines the device boundary, its ecosystem contracts, and the validation
tooling that enforces both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns IEC plant and experiment
truth — configuration policy for electrostatic potential wells that
accelerate and recirculate ions towards a converged core, realised by a
transparent cathode grid or by an electron-injected virtual cathode in a
magnetic-cusp trap, quasi-steady discharge lifecycle semantics with arcing
and cathode-collapse hazard records, well-depth and convergence diagnostic
and clock declarations, actuator-response boundaries, safety-envelope
declarations, and the device-owned CONTROL adapter specification. The
registry's family split (`electrostatic` fusor, `magnetic_open` Polywell)
is intentionally bridged by the portfolio standard and recorded in the map;
purely magnetic cusp confinement stays with `SCPN-MAGNETIC-CUSP-CORE`;
solver mathematics in `SCPN-FUSION-CORE`; typed semantics in
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection keeps the
final veto; portfolio presentation belongs to `SCPN-STUDIO`, towards which
this project is `not_federated`.
