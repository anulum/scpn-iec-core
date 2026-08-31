<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-IEC-CORE` is the device-family owner for inertial electrostatic
confinement systems in the SCPN Reactor Systems Research Group portfolio.
The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_iec_core/`, design record ADR 0002,
evidence record `VALIDATION.md#device-configuration-model`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — confinement and reaction in an
   electrostatic potential well that accelerates ions towards a converged
   core and recirculates them through it. The `gridded_iec` realises the
   well with a transparent cathode grid (grid interception and
   ion-recirculation lifetime as defining budgets); the `polywell`
   replaces the grid with a virtual cathode formed by electron injection
   into a magnetic-cusp trap (electron confinement and virtual-cathode
   depth as defining budgets). The registry classifies `gridded_iec` as
   `electrostatic` and `polywell` as `magnetic_open`; the portfolio
   standard assigns both here because the device-level workflow of each
   is the potential well — the cusp field in the Polywell serves electron
   confinement, not ion confinement. Purely magnetic cusp devices,
   mirrors, and external-accelerator beam-target systems are excluded.
2. **Primary driver and energy delivery** — high-voltage well drive
   (cathode-grid supply or electron guns establishing the virtual
   cathode), magnet-coil systems for the Polywell's electron trap, ion
   sources and gas feed; continuous or pulsed discharge operation is a
   configuration facet.
3. **Plant and shot lifecycle** — quasi-steady discharge lifecycle:
   vacuum and conditioning, well establishment, discharge operation with
   recirculation balance, and termination. Device-level hazard semantics
   cover grid overheating and sputtering (gridded), virtual-cathode
   collapse (Polywell), breakdown/arcing, and X-ray production at high
   well voltages.
4. **Diagnostic, reference-frame, and clock model** — well-centre radial
   conventions, well-depth and potential-profile channels, core
   convergence and neutron-yield channels, per-configuration
   electron/ion-population indicators, and continuous-operation clock
   identities with declared burst resolution.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-IEC-CORE (device truth: potential-well policy, discharge lifecycle,
               well/convergence diagnostics, safety envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
