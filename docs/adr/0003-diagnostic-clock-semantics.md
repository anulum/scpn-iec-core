<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — ADR 0003
-->

# ADR 0003 — Diagnostic and clock semantics aligned with the SPO catalogue

Status: accepted (2026-08-31). Extends ADR 0001 (boundary) and ADR 0002
(device configuration model, evidence-maturity ceiling rule).

## Context

The SCPN Phase Orchestrator observability-profile catalogue (release
`1.0.0`, digest
`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`,
bound to reactor registry `1.0.0`) fixes, per candidate phenomenon, the
epistemic route (observability class), the admissible semantic carriers,
and the class-fixed evidence vocabulary a diagnostic must eventually
bind. Six candidates apply to the configurations this repository owns:
`iec.resolved_bunching` (derived cyclic) and `iec.steady_state`
(noncyclic feature) for both `gridded_iec` and `polywell`;
`open.drive_reference` (direct cyclic), `open.equilibrium_and_loss`
(noncyclic feature), and `open.resolved_interchange_mode` (derived
cyclic) through `polywell` only, exactly as scoped by the catalogue;
and `model.synthetic_oscillator_coordinate` (numerical only).

## Decision

1. The capability `diagnostic_clock_semantics` is implemented as a
   declaration model (`src/scpn_iec_core/observability.py`): frozen
   `ClockModel`, `DiagnosticChannelPlan`, `DeferredCandidate`, and
   `DiagnosticPlan` objects with fail-closed invariants, an
   advisory-only consistency report, canonical serialisation with
   SHA-256 digests, and a strict round-trip parser.
2. The catalogue is bound as DATA ONLY (`ObservabilityBinding` pinned
   to the exact release and digest above); this package never imports
   SCPN Phase Orchestrator code. A plan whose binding differs from the
   embedded pin is rejected.
3. Alignment is enforced structurally: a channel must address an
   applicable candidate; its carrier must be admissible for the
   candidate's class; its evidence-binding keys must equal the
   class-fixed vocabulary exactly; the clock slot must reference a
   declared clock whose kind is compatible with the class
   (numerical-only to the simulation clock, direct and derived cyclic
   to the facility monotonic clock, noncyclic to either non-simulation
   clock). The per-candidate configuration scoping records the
   polywell-only applicability of the open.* candidates.
4. Timing is fail-closed where physics fixes the bound: the Nyquist
   criterion for both cyclic classes. The device-typical band checks
   are advisory only: electrostatic bunching oscillations in the
   10 kHz–10 MHz scale and RF drive frequencies of 1 MHz–200 GHz
   (R. L. Hirsch, J. Appl. Phys. 38 (1967) 4522).
5. The reference plan mirrors canonical practice with synthetic
   declarations: an electrostatic-bunching probe (derived cyclic), a
   steady-state potential/current set and a loss-profile set
   (noncyclic), an RF drive-phase reference (direct cyclic), an
   interchange-mode probe array (derived cyclic), and the model-owned
   synthetic oscillator (simulation clock). Every applicable candidate
   must be planned or explicitly deferred with a reason; every channel
   is `synthetic=True` by hard invariant. No SPO semantic-profile
   ingress is declared: the profile registry's `ingress_state` for
   this device family stays `not_declared` until a real, versioned
   adapter exists.

## Consequences

- The manifest gains the capability `diagnostic_clock_semantics` at
  `computational_prototype` (evidence:
  `VALIDATION.md#diagnostic-and-clock-semantics`); the repository-level
  maturity remains `computational_prototype` under the ADR 0002 ceiling
  rule.
- No diagnostic, measurement, facility, adapter, or ingress is claimed
  to exist. The model constrains future declarations; it evidences
  none.
- A catalogue release change is a governed data change: the embedded
  subset and pin must be updated together, in coordination with the
  SPO owner.
