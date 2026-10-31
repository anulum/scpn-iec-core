<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms of spherical
cathode grid geometry evaluated in IEEE-754 binary64 on the Python floor
(lengths in metres, angles in radians, the well voltage in kilovolts):

| Module | Kernels | Operations |
|---|---|---|
| `physics/grid_geometry.py` | bridge half-angle `atan(t / D)`, globe aperture count `2 n_long (n_lat + 1)`, symmetric aperture angle `360 / (2 n)`, the four symmetric grids | integer arithmetic, `/`, **`atan`** |
| `physics/transparency.py` | sphere area `4 pi R^2`, geometric transparency, circular aperture radius `R sin(theta - alpha)`, spherical-cap area `2 pi R^2 (1 - cos(asin(r / R)))`, circular and normalised circular transparency | `* / -`, `math.fsum`, **`sin`, `asin`, `cos`** |
| `physics/ion_transit.py` | maximum ion passes `eta / ((1 - eta)(1 + eta))` | `* / - +` |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. The sums over apertures use `math.fsum`, which is correctly
rounded. The trigonometric functions are the platform's `atan`, `sin`,
`asin` and `cos`, which IEEE-754 does not require to be correctly rounded.
A native backend that must agree bit for bit would therefore have to use
one deterministic implementation of each function on both sides. No physical constant enters any
kernel: the ion energy in keV equals the well voltage in kV for a singly
charged ion.

**Backend status.** Python floor only. There is no native crate. The
ecosystem production standard asks for a native path on required numeric
paths and allows a scoped, owner-approved exception for trivial non-hot
arithmetic; that decision is the owner's and is recorded as open in the
backlog. The benchmark marks the native backend as unavailable instead
of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-iec-core.level0-physics-benchmark.v1`, generated 2026-10-31T09:58:44.254026+00:00, at commit
`2ed15ae1c07c` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 11.41 (other sessions were active on the host);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (bridge half-angle, circular aperture radius, spherical-cap area and maximum ion passes per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.408 | 1.508 | 1.599 | 1.279 | 710427 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 212.757 | 284.192 | 287.372 | 211.238 | 4700 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
