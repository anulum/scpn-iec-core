<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The IEC family spans two registry
families: `gridded_iec` is classified `electrostatic`, while `polywell` is
classified `magnetic_open` for its cusp topology. The portfolio standard
records an intentional registry-family/project-boundary distinction here; a
boundary decision was needed on that split and on the magnetic-cusp and
beam-target edges.

## Decision

1. `SCPN-IEC-CORE` owns exactly two registry configurations:
   `gridded_iec` and `polywell`. Both realise the same device-level
   workflow — an electrostatic potential well accelerating and
   recirculating ions towards a converged core — differing in how the
   well is formed (transparent cathode grid versus electron-injected
   virtual cathode in a cusp trap). That shared workflow, driver class,
   discharge lifecycle, and diagnostic model satisfy the five-surface
   sharing test; the well-formation mechanism is the configuration
   parameter.
2. The manifest declares device-family truth `electrostatic`; the
   machine-readable map records the polywell's `magnetic_open` registry
   classification as an intentional distinction. Purely magnetic cusp
   confinement stays with `SCPN-MAGNETIC-CUSP-CORE`.
3. The repository owns device-level truth only: potential-well
   configuration policy, discharge lifecycle semantics, well-depth and
   convergence diagnostic declarations, actuator-response model
   boundaries, the safety-envelope declaration, and the device-owned
   CONTROL adapter specification.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Assigning the Polywell to the magnetic-cusp repository** (registry
  family alignment): rejected by the portfolio standard — the Polywell's
  cusp field confines electrons to form the virtual cathode; the ion
  workflow that defines the device is electrostatic. The map records the
  intentional distinction.
- **Separate repositories for fusor and Polywell**: rejected — both share
  the potential-well workflow, driver class, lifecycle, and diagnostics;
  the split would duplicate contracts for a well-formation parameter.
- **Classifying IEC as beam-target fusion** (energetic-ion reactions):
  rejected — the recirculating well population is internal device truth,
  not an external accelerator facility.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity per IEC configuration and
  a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
