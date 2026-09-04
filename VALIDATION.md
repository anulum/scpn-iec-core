<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-IEC-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`ConfinementStructure`,
  `ElectrostaticDrive`, `DeviceConfiguration`) rejecting non-finite
  values, non-positive extents, and the hard class invariants: a
  physical cathode grid with transparency strictly inside (0, 1) and no
  magnetic coils for `gridded_iec` (Hirsch, J. Appl. Phys. 38 (1967)
  4522), and at least six polyhedral coils with no physical grid for
  `polywell` — every rejection branch is tested.
- The ion-energy relation `E = e U` as a documented derived quantity,
  with an advisory finding for well voltages below the documented IEC
  operating floor 20 kV, reported and never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not convergence, loss, or
  yield results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The nullable `timing_uncertainty_s` member, declared `null` on every
  channel because no event-relative candidate is applicable here; a
  non-null value is refused. This keeps the channel shape identical across
  the portfolio under envelope 1.1.0.
- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, and incomplete candidate coverage —
  every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: bunching probe, steady-state set, drive reference,
  loss-profile set, interchange probe array, and synthetic oscillator,
  each bound to its clock domain; the open.* candidates are recorded as
  polywell-scoped exactly as in the catalogue.
- Documented advisory band checks with their sources stated in the
  code: electrostatic bunching in the 10 kHz–10 MHz scale and RF drive
  frequencies of 1 MHz–200 GHz (Hirsch 1967); findings are reported,
  never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_iec_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; no `timing_marker` (no
  event-relative candidate is applicable); numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The closed-form geometry of a spherical cathode grid, in the forms a
  filed open-access source prints: the bridge half-angle
  `arctan(t_bridge / D_grid)`, the globe-grid aperture count
  `2 n_long (n_lat + 1)`, the four permissible symmetric grids with the
  rule `360 deg / (2 n)` for their varying aperture angle, the geometric
  transparency as the aperture area over the sphere area, the circular
  transparency of the largest circles the apertures admit, and their
  ratio.
- The often-quoted bound `eta / (1 - eta**2)` on how many passes an ion
  may make through a grid of transparency `eta`, refused outside the
  open interval — a grid of zero transparency passes nothing, and a
  transparency of exactly one is the polywell's virtual cathode, which
  bounds no number of passes at all.
- A composed record that requires a grid declaration for the gridded
  class and refuses one for the polywell class, in both directions and
  by name.
- Where per-aperture areas are declared, the record recomputes the
  geometric transparency and reports it beside the transparency the
  configuration declares. Neither is derived from the other; a test
  moves one and watches the other stand still.
- Per-aperture measurements are refused unless there is exactly one
  entry per aperture the ring counts imply, which binds the declared
  measurements to the grid they are said to describe.
- Canonical serialisation (sorted keys, NaN/infinity rejected) and
  SHA-256 digest identity of the record.

Anchors — printed values reproduced, and nothing further:

- All four bridge angles of the source's grid-angle table, to the three
  decimals it prints.
- The aperture count printed in the caption of its globe-grid figure,
  and both endpoints of the 8-to-220 range it states for the globe
  family it analyses.
- Every row of its symmetric-grid table, whose varying angle follows
  from the stated crossing rule, and two of whose aperture counts the
  same paper states a second time from two other laboratories.
- The identity it states for grids with circular apertures, whose
  normalised circular transparency is exactly one.
- A nine-ring symmetric cathode, which one filed source reports as built
  and operated at a named laboratory, reports the 48 apertures the other
  source tabulates for that ring count. The number crosses two
  independent documents.

Measured, rather than assumed:

- The bridge angle table cannot settle the form of its own equation:
  dropping the arctangent reproduces all four printed angles to the
  digit. Only the printed equation carries the tangent, and a test
  records that the table is no corroboration of the choice.
- The pass-count denominator is evaluated factored rather than as the
  printed difference of squares. Over 20029 transparencies the two forms
  disagree at 7994 of them, the worst by 5.5e-10 relative, because
  subtracting a square from one cancels the significand near one.
- Composing the circular-aperture and spherical-cap equations agrees
  with their single-step form to 8.4e-15 relative rather than exactly,
  measured over the admissible angle range.
- A spherical cap whose base is the sphere radius falls one unit in the
  last place below half the sphere, at every one of 499 radii measured,
  because `cos(asin(1))` is 6.12e-17 rather than zero.

Bounded claims — what is NOT claimed:

- No value describes, approximates, or validates any real machine. An
  anchor reproduces a number a filed source prints and nothing further.
- The pass-count bound rests on transparency alone. It sees no pressure,
  charge exchange, scattering or ion energy, and the same source states
  that most such devices operate where an ion makes only a few passes
  before charge exchange ends its life. It is an upper bound set by
  geometry, never a predicted pass count.
- Aperture areas and neighbour half-angles are declared inputs, measured
  off a grid model this repository does not build.
- The polywell's virtual cathode is a declaration here, not a field
  calculation; no magnetic geometry is computed anywhere in this
  package.
- No fusion rate, neutron yield, sheath, space-charge or transport
  result is computed, and no experimental correlation exists in this
  repository.
