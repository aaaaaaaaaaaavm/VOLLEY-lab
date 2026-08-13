# VOLLEY, Phase II

The research track of the VOLLEY programme.

<!-- PROGRAMME-HEADER-START -->
| Repository | Role | You are here |
|---|---|---|
| [VOLLEY](https://github.com/aaaaaaaaaaaavm/VOLLEY) | Flagship, authoritative engineering record, portfolio | |
| [VOLLEY-paper](https://github.com/aaaaaaaaaaaavm/VOLLEY-paper) | IEEE companion, manuscript and reproducibility package *(generated)* | |
| [VOLLEY-thesis](https://github.com/aaaaaaaaaaaavm/VOLLEY-thesis) | Thesis companion, university submission *(generated)* | |
| **[VOLLEY-lab](https://github.com/aaaaaaaaaaaavm/VOLLEY-lab)** | Phase II, research, redesign, deliberately unstable | |
<!-- PROGRAMME-HEADER-END -->

> ## This repository makes no promises
>
> No frozen baseline. No stability requirement. Numbers here may be wrong, half-finished, or
> abandoned mid-thought. **Nothing in this repository should be cited.**
>
> The engineering record is the [flagship](https://github.com/aaaaaaaaaaaavm/VOLLEY). If
> anything here disagrees with it, the flagship is right.

## Why this exists

The [flagship](https://github.com/aaaaaaaaaaaavm/VOLLEY) is a Phase I deliverable and its
stability is a design requirement. This repository is the pressure valve that lets it stay
frozen.

A Phase II track kept *inside* the flagship is a soft boundary, one `git checkout` from
becoming an edit to the frozen baseline. This is a hard wall instead of a line on the floor.

**Redesign freely here. Do not touch the baseline there.**

## What belongs here

Anything that would make the design **better** rather than **correct**. The deferred list and
each item's entry criterion live in the flagship's
[`docs/PHASE_II.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/PHASE_II.md):

| | |
|---|---|
| PII-1 | Momentum-transfer release, recovers the full velocity shortfall for 1.6 % of shot energy |
| PII-2 | Rib-stiffened chassis, A4 leaves a 17x stress margin unspent |
| PII-3 | Two-layer stator (G3-D4), sits upstream of K<sub>t</sub> |
| PII-4 | Envelope repackaging (P9), currently 44 % over ESPA Grande |
| PII-5 | Variable-shape atmosphere, the root cause behind P16 |

More arrived on 2026-07-30, from reading the nearest published work and from the bank finding:

| | |
|---|---|
| PII-6 | **Reachable-domain analysis.** Feng et al. compute a 3-D envelope of the orbits one shot makes available. The flagship reports a scalar lifetime multiplier instead, which answers a smaller question. Their method is better and this is where adopting it belongs |
| PII-7 | **A bank that can source the shot.** P26 found the flagship's supercapacitor bank specified at an ESR no commercial cell achieves, and the shot does not close at a realistic value. Costed at four parallel strings in the flagship's PHASE_II.md |
| **PII-8** | **[VOLLEY as a free-flyer](PII-8_free_flyer.md).** A long deployed track plus release at perigee reaches TLI and Mars-class C3 without exceeding CubeSat qualification. Three hard problems in front of it, named in the file |
| **PII-9** | **[The lunar case](PII-9_lunar.md).** Where this technology actually belongs, and the mass driver it descends from. 1.33 MJ/kg to lunar orbit, so 15 kW launches a tonne a day |
| PII-10 | **Magazine indexing disturbance** (E24). Xu et al. treat the attitude disturbance from moving satellites inside a deployer as a cost worth optimising against. The flagship budgets recoil from the shot and nothing from the indexing between shots. The bookkeeping half is an error correction and belongs upstream; designing an indexing sequence that minimises it belongs here |

Added 2026-07-31:

| | |
|---|---|
| **PII-11** | **[A deployable track, and the side-rail layout](PII-11_deployable_track.md).** A telescoping track long enough to accelerate *and* regeneratively arrest the sled reaches **48 % efficiency against 21.2 %**, deletes the eddy brake, closes P28, and stows **inside** the ESPA Grande envelope the flagship misses by 44 %. The only option that improves velocity and envelope together. The side-rail layout loses on thrust in every variant and is here because it drives the **tip-off** term to zero and is the only topology a deployed track can be pretensioned in |

Added 2026-08-10:

| | |
|---|---|
| **PII-14** | **[A cable-driven gondola on a deployed truss](PII-14_cable_driven_gondola.md).** Propulsion off the vehicle, energy from a flywheel, a permanently-locked deployed truss, and a tensioned wire as the running surface. **Declined for Phase I on margin**: the +49.7 % headline assumed zero drivetrain inertia, and a realistic drivetrain gives +15 to +30 % — possibly zero — in exchange for deleting the linear synchronous motor and 24 validations. Recorded with its two dead ends, because a wire fails as a structure by four orders of magnitude and maglev is unnecessary in zero-g, and both will otherwise be re-proposed. **Band 1, drivetrain inertia ≤ 2 kg, is the gate on everything else** |

Also: anything from dossier §8's cross-industry list that turns into real work, and any idea
that does not yet have a home.

## What does not belong here

**Error corrections.** If something in the flagship is *wrong*, fix it in the flagship. The
distinction is the whole of the change-control rule in
[`BASELINE.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/BASELINE.md), and it is by
type, not by convenience. P17 is tedious and belongs upstream; the momentum-transfer release
is fascinating and belongs here.

## How work gets out

Only at a **baseline boundary**: the next opens after thesis submission, and only by meeting
the entry criterion written when the item was deferred. Not by seeming promising.

That rule exists for the same reason acceptance bands are declared before runs: a criterion
written afterwards is written by someone who already knows what they want the answer to be.

## Licence

**CC BY 4.0** — full text in [`LICENSE`](LICENSE), attribution form in [`NOTICE`](NOTICE).
Attribution requires credit, a link to the licence, and **an indication of whether changes were
made**.

**Not retroactive:** snapshots taken before this change remain available under the MIT licence
they carried at the time, retained at [`LICENSE-MIT-superseded`](LICENSE-MIT-superseded).

This repository carries copies of VOLLEY analysis code under `reference/volley/`. CC BY 4.0 does
not license patent rights, which is why a patent-granting licence was not used here.
