# PII-14: a cable-driven gondola on a deployed truss, and the number that decides it

> **Read this section before the rest.** The headline that made this concept attractive —
> **+49.7 % exit velocity in the existing 1.30 m track** — assumed the drivetrain has **zero
> rotating inertia**. That is not a small idealisation, it is the entire margin. Under a
> realistic drivetrain the gain is **+15 to +30 %, and possibly zero.** The concept is recorded
> here because it may still be right; it is recorded *this way* because the optimistic case is
> what a reader will reconstruct on their own, and the ceiling is what they will not.

**Phase II.** Four ideas that arrived separately over one conversation and compose into a single
machine: propulsion moved off the vehicle onto a cable, energy moved from a supercapacitor bank
to a flywheel, structure moved from a rigid track to a permanently-locked deployed truss, and the
running surface moved from a beam to a tensioned wire supported by the truss.

**It deletes the ironless Halbach linear synchronous motor**, which is what the flagship is. That
is stated first because it is the cost, and because every number below is easier to like than
that sentence is.

---

## 0. Status and entry criterion

**Not adopted. Not recommended for Phase I.** Assessed 2026-08-10 and declined on margin — see
§6.

**Entry criterion:** a computed drivetrain inertia budget referred to the cable showing
**m_eff ≤ 2 kg**, *and* a Phase I baseline that has been measured rather than modelled. Neither
exists. Nothing else opens this item — not a better cable, not a better boom, not enthusiasm.

---

## 1. Move the motor off the vehicle

The flagship's sled is **9.445 kg**, and it is heavy because it carries its own motor:

| On the sled today | Mass | Why it exists |
|---|---:|---|
| Halbach magnets, two faces | 3.67 kg | the moving half of the linear motor |
| chassis plates | ~2.5 kg est. | to resist 2.69 kN of inter-array attraction (A12) |
| brake fin | ~0.9 kg est. | the eddy brake |

A cable-driven **gondola** carries none of them. Take it at **2 kg**, and the same commanded
1389 N in the same 1.30 m track gives:

| Gondola | Moving mass | Accel | Exit velocity | vs 16.388 |
|---:|---:|---:|---:|---:|
| 9.445 kg (flagship) | 13.45 | 10.53 g | 16.39 m/s | — |
| 3.0 kg | 7.00 | 20.2 g | 22.72 m/s | +38.6 % |
| **2.0 kg** | **6.00** | **23.6 g** | **24.54 m/s** | **+49.7 %** |
| 1.5 kg | 5.50 | capped at 25 g | 25.25 m/s | +54.1 % |

**No envelope change.** This is why the concept looked compelling: the flagship's own conclusion
had been that mass could not reach the 25 g ceiling and 2.37× thrust was required — but that was
true *only because the sled carries its motor*. Take the motor off and the arithmetic inverts.

**24.5 m/s is +104 % orbital lifetime at 450 km** against the flagship's +61.8 %, computed from
`analysis/astro.py`. Crossing to "doubles the life" is a categorical change in how the product
can be described.

## 2. The number that decides it, and it is not the cable

Rotating inertia referred to the cable is **`m_eff = I_total / r²`**, and it adds **directly** to
the moving mass. It is not a second-order correction; it is the same term as gondola mass.

| m_eff | Moving mass | Exit velocity | Gain | |
|---:|---:|---:|---:|---|
| 0 kg | 6.0 | 24.54 m/s | **+49.7 %** | the case as pitched, and physically impossible |
| 1 kg | 7.0 | 22.72 m/s | +38.6 % | worth it |
| 2 kg | 8.0 | 21.25 m/s | +29.7 % | worth it |
| **4 kg** | 10.0 | 19.01 m/s | **+16.0 %** | marginal |
| 6 kg | 12.0 | ~17.5 m/s | ~+7 % | not worth the rewrite |
| **7.4 kg** | 13.4 | 16.42 m/s | **+0.2 %** | the entire gain is gone |

**7.4 kg is exactly what the gondola saved.** If the drivetrain weighs what the sled lost, the
architecture buys nothing and costs everything.

**Is 2–5 kg plausible? Yes, and that is the problem.** The drive must deliver 1389 N at up to
24.5 m/s — **34 kW peak**, and 139 N·m at a 100 mm drum. A machine of that class has rotor
inertia of order **0.01–0.05 kg·m²**, which at r = 0.1 m is **1–5 kg effective**, before the drum
(another ~1 kg for a 2 kg solid drum — note `m_eff = m_drum/2` *regardless of radius*) and before
any gearbox.

**Gearing cannot rescue it.** A reduction gearbox multiplies reflected rotor inertia by the ratio
**squared**. And the classic servo-sizing result is that peak load acceleration occurs at
**inertia matching** — reflected load inertia equal to rotor inertia — at which point *half the
torque is accelerating the motor*. A badly-chosen drivetrain lands near `m_eff ≈ 6 kg` by
construction.

> **This is the first thing anyone reopening this item must compute.** Not the boom, not the
> cable, not the wire tension. Everything else in this document is comfortable; this one is not.

> **CLOSED 2026-08-20. This section is settled and the answer is no.**
> The flywheel was split out here as *"a Phase I candidate against P26 in its own right"*. **That
> question is now Gen6's pulse store, and [A64](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A64_pulse_store_technology.md)
> answered it at ~70 g** on published pulsed-power capacitor data, at 400 kW/kg. *A rotating
> machine with bearings, containment and the **7.15 N·m·s** this section itself computes does not
> beat seventy grams* — and that momentum is a disturbance in a machine whose shot already dumps
> **3.28 N·m·s**, which this section also says. **The entry retired itself; it just did not know
> what it was competing against yet.**

## 3. The flywheel, which does not need the rest of this

Peak electrical demand is ~33 kW for 158 ms. A flywheel motor-generator supplies that from stored
kinetic energy:

| Flywheel | rpm for 2.56 kJ | Stored angular momentum |
|---|---:|---:|
| 2 kg, r 100 mm | 6,832 | 7.15 N·m·s |
| 3 kg, r 120 mm | 4,649 | 10.52 N·m·s |
| 1.5 kg, r 80 mm | 9,862 | 4.96 N·m·s |

Spin up over minutes, discharge in 158 ms.

**This attacks P26 — the supercapacitor bank that cannot source the shot on purchasable parts,
the flagship's largest open defect — and it is completely independent of the cable drive.** An
energy store does not care what load it feeds. The ESR ceiling that inverted the ranking of every
lever in `DESIGN_OPTIONS_exit_velocity.md` is a property of capacitors, not of rotating machines.

**It has therefore been split out and does not belong in this file's trade.** It is a Phase I
candidate against P26 in its own right. Recorded here only because this is where it came from.

Two cautions travel with it either way: a flywheel is a rotating mechanism and a new failure
mode, and at 6,800 rpm it stores 7.15 N·m·s — comparable to the **3.28 N·m·s** angular impulse a
single shot dumps at a 50 mm CoM miss. That coupling could be a disturbance or, with a
counter-rotating pair, a mitigation. It is unmodelled.

## 4. The structure: three dead ends and one answer

**This section is the useful half of the document.** The route to the answer went through two
proposals that fail by orders of magnitude, and knowing *why* they fail is what stops them being
re-proposed.

### 4.1 A tensioned wire as the running surface — fails by 10⁴

A wire has no bending stiffness. All transverse stiffness is `k = 4T/L`, bought with tension. The
load is not avoidable: the payload's own thrust reacts **70 mm above the thrust line** (413 N ×
0.070 m = 28.9 N·m), reacted across the 300 mm roller base as **96 N transverse**.

| Deflection budget over 3.3 m | Tension required |
|---|---:|
| 0.05 mm (the gap shim spec) | **1,591 kN** |
| 0.10 mm | **795 kN** |
| 1.00 mm — i.e. contact | 80 kN |

At a buildable 5 kN the wire deflects **15.8 mm — sixteen times the airgap.**

**And the reaction kills it independently.** Tension must be reacted in compression by the spine
spreading the wires, over the same span. An 80 kN spine over 3.3 m needs **EI ≥ 88,271 N·m² just
not to buckle — 2× the flagship track's entire bending stiffness**; at 795 kN it is 16×. The
tension architecture does not remove the stiff structure, it relocates the load and adds to it.

Third failure, sufficient on its own: **the couple reverses sign** as the gondola passes, and
cables only pull, so both wires need preload never to go slack — roughly doubling the tension
again.

**Tension structures win when the load is one-directional and the compression path is short.**
Here the load reverses and the compression path is exactly as long as the beam being avoided.

### 4.2 Maglev — solving a problem that does not exist in orbit

**There is no weight to levitate.** The rollers do not carry the gondola; they react the 96 N
couple and hold the airgap. Remove the airgap (§4.4) and four rollers are comfortably adequate.

Active maglev needs sensors, power and control distributed along the whole track — strictly worse
than four rollers. Passive Inductrack-style levitation needs relative motion to generate lift and
produces drag below transition speed, which is most of a 158 ms stroke starting from rest.

**Maglev is unnecessary for the same reason the cable drive works.**

### 4.3 Heat- or field-stiffened materials — the wrong mechanism

| Approach | What it does | Verdict |
|---|---|---|
| SMA (Nitinol) | modulus 28 → 75 GPa, 2.7× | actuation and latching, not EI |
| Shape-memory polymer / EMC | large modulus swing, rigid state only ~1–3 GPa vs CFRP's 100 | hinges, not load paths |
| MR / ER fluid | yield stress under field; it is a fluid | damping, not bending stiffness |
| Rigidizable inflatable | genuinely stiffens, cures once | real, immature, single-shot |

None deliver EI. Two structural objections settle it: **anything requiring power to stay stiff is
a single-point failure** with a gondola at 24 m/s on the track, and **heat is a budget that does
not exist** — the campaign thermal case is 24.4 kJ over twelve shots against a 0.32 m² radiator,
and P10 already records the thermal and enclosure mass line items as incomplete.

**The coiled boom is already the smart material**: stored elastic strain energy, released on
command, passively stable when deployed, zero power to hold. The only place a smart material
earns its place is **SMA latches at the spreaders**.

### 4.4 What works: a twin-boom truss, a separate running surface

**Decouple structure from running surface.** The structure carries bending and may be jointed,
because bending stiffness tolerates a step at a joint. The running surface must be continuous,
because the gondola runs on it.

That dissolves the joint-step problem — the one risk PII-11 raised and could not answer
(*"a step at each telescoping joint … nothing here shows anyone can hold one"*) — and it puts
**telescopic sections back on the table**, which are more mature and stiffer per kilogram than
coilable booms.

**Bending stiffness required at 3.3 m deployed**, from the flagship track's own 54,324 N·m²
scaled as L³:

| | Required EI |
|---|---:|
| Holding the 1 mm magnetic airgap (linear motor retained) | 334,749 N·m² |
| At 10× looser guidance (cable drive, no airgap) | ~33,000 N·m² |

**Removing the linear motor removes the airgap, and with it an order of magnitude of structural
requirement.** This is the largest single benefit of the cable drive and it is not the velocity.

| Configuration | EI | Covers |
|---|---:|---|
| Single BeCu boom, 50 × 0.2 mm | 1,257 N·m² | neither |
| Single CFRP boom, 150 × 0.3 mm | 39,761 N·m² | cable drive only |
| **Two 100 mm booms, spreaders at 300 mm** | **424,115 N·m²** | both |
| Two 150 mm booms, spreaders at 300 mm | 636,173 N·m² | both |

The parallel-axis term `EI = 2·A·E·(d/2)²` scales with **separation squared**, so the spreaders
do more work than the booms. **Derate to ~50–70 % of ideal** for shear and joint compliance —
call the 100 mm/300 mm case **~250,000 N·m²**, ample for the cable drive, marginal for the airgap.

**Permanent locking is what recovers most of that derate.** Deploy-once removes the requirement
for re-openable joints, so a one-way tapered wedge under spring preload has no free play — and
free play is what costs real deployable masts their stiffness. Springs, not electromagnets:
anything needing power to stay locked fails soft under load.

### 4.5 And now the wire works — as the running surface

`δ = P·L/(4T)` where **L is the spreader pitch, not the span**:

| Spreader pitch | Tension for a 2 mm budget (cable drive) |
|---:|---:|
| 3.3 m — unsupported | 39.6 kN |
| 1.0 m | 12.0 kN |
| **0.5 m** | **6.0 kN** |
| **0.25 m** | **3.0 kN** |

**Four orders of magnitude below §4.1**, and entirely buildable. Two conditions, both met by the
rest of the stack: the truss carries the bending, and the cable drive has deleted the airgap.

The wire was never wrong. It was being asked to be a beam.

## 5. Cable dynamics, which are survivable

| Cable | Stretch at 1389 N | Natural freq | Cycles per 158 ms stroke | UTS margin |
|---:|---:|---:|---:|---:|
| 2 mm | 2.87 mm | 45 Hz | 7.1 — arrives ringing | 4.1× |
| **4 mm** | **0.72 mm** | **90 Hz** | **14.3** | **16.3×** |
| 6 mm | 0.32 mm | 136 Hz | 21.4 | 36.6× |

**4 mm or larger.** Below that the gondola is still ringing on the cable at release, straight into
the tip-off budget A23 spent so much effort on.

Unresolved and unmodelled: the **release transient** (tension collapses when the payload leaves,
and the stored stretch snaps back), **tension matching** between two cables or they yaw the
gondola, and **slack management** in zero-g.

One genuine advantage over a distributed linear motor: **the cable pulls at a point you choose**,
so it can be aimed through the payload CoM. The 70 mm offset becomes a design variable rather than
a given.

## 6. Why this was declined for Phase I

Assessed 2026-08-10 against an explicit willingness to bend the Phase I freeze if the advantage
outweighed the cost by a margin. **It does not.**

| | |
|---|---|
| **Gain** | +15 to +30 % velocity, uncertain, possibly zero (§2) |
| **Cost** | A1–A24 largely inapplicable — field model, thrust constant, ripple, regen, finite-stator, sensitivity ranking are all about the LSM |
| | `paper.tex` rewritten; the frozen baseline void |
| | Zero validations behind the new architecture, against 24 behind the current one |
| | The novel contribution replaced by a mature one: an ironless Halbach LSM deployer is a contribution, a winch is engineering |

**The evidence base is the Phase I deliverable.** Discarding it does not cost rework, it costs
the thing the flagship exists to demonstrate.

Two pieces were extracted and do not require this architecture:

- **the flywheel energy store** (§3), a Phase I candidate against P26 on its own merits;
- **the CoM-offset lever**, cradle geometry that attacks tip-off, angular impulse and track
  stiffness together, with no architecture change at all.

## 7. Bands, for whoever reopens this

Declared here so that the first analysis is falsifiable rather than confirmatory.

| # | Band | Why it decides something |
|---|---|---|
| **1** | **Drivetrain inertia referred to the cable ≤ 2 kg** | Below this the concept is worth it; at 7.4 kg the entire gain vanishes. **Compute this first** |
| 2 | Truss shear compliance ≥ 50 % of ideal parallel-axis EI | The derate that decides whether 424,000 N·m² is real or fictional |
| 3 | Section root moment at full deployment, and the drum/motor sized from it | What actually sizes the deployment mechanism |
| 4 | Guide-wire tension ≤ 6 kN at ≤ 500 mm spreader pitch | Cheapest of the four; §4.5 suggests it passes comfortably |

**Band 1 is the gate.** If it fails, bands 2–4 are wasted work.

---

## Provenance

Every figure computed against the flagship's own `analysis/motor_model.py` and `analysis/astro.py`
at flagship baseline **Kt = 11.0258 N/kA·m, v_exit = 16.388 m/s, sled 9.445 kg, F_cmd 1389 N**.
Gondola mass, drum mass, rotor inertia, boom wall thicknesses and the 10 g shim are **assumptions,
not sourced values**. Nothing here has been built, measured, or independently checked, and
**nothing in this repository should be cited.**
