# PII-11: a deployable track, and the side-rail layout that makes it buildable

> **Baseline note, 2026-08-05.** The Phase I numbers this file compares against have moved.
> The 2026-08-03 quadrature correction gives Kt = 11.03 N per kA/m, 16.388 m/s at 10.53 g,
> 2.85 kJ gross and 2.56 kJ net, 20.99 % net efficiency and a 68 mohm bank ESR ceiling. Figures
> below written at 11.22, 16.53 m/s, 10.7 g, 2.88 kJ or 19.0 % predate it. The **ratios and
> conclusions** here are not sensitive to a 0.9 % shift in the comparator and are left as
> written; the absolute Phase I values are not current. `docs/BASELINE.md` in the flagship is
> authoritative.

**Phase II.** Two ideas that arrived separately and turn out to be one item: a telescoping track
that deploys after the host reaches orbit, and a layout with the motor split into two rails on
either side of the payload instead of one track beneath it.

**The headline, stated before the argument.** A deployed track long enough to both accelerate and
regeneratively arrest the sled reaches **48 % electrical-to-payload efficiency against 21.2 %
today**, deletes the eddy-current brake, closes P28, and **stows inside the ESPA Grande envelope
the current design misses by 44 %**. It is the only option in this programme that improves
velocity and envelope at the same time; every other lever trades one against the other.

**What it is not.** A velocity play. The side-rail split loses on thrust in every variant priced
below, and the argument for it is tip-off and deployability. Anyone reading this for a bigger
number is reading it wrong.

---

## 0. The prerequisite: a long stator must be block-commutated

This decides everything downstream and it is worth stating first.

`motor_model.shot()` computes copper loss over the **whole** 1.30 m winding. A real long-stator
machine energises only the section under the mover. Which convention holds decides whether a
long track is possible at all:

| Track | Whole stator energised | Segmented, 340 mm energised |
|---|---|---|
| 1.30 m | 828 J copper, **19.0 %** | 217 J, **24.4 %** |
| 2.00 m | 1580 J, 17.5 % | 269 J, 24.8 % |
| 3.00 m | 2901 J, 16.0 % | 329 J, **25.0 %** |
| 5.00 m | 6243 J, 13.5 % | 424 J, 25.0 % |
| 7.50 m | **bank limit, no shot** | 520 J, 24.5 % |

Un-segmented, copper grows as `L^1.5` and the idea dies before 7.5 m. Segmented, copper is nearly
flat and efficiency stops falling. **Everything below assumes segmentation.**

> **This had a Phase I consequence, logged upstream as P29, and it has now been decided.**
> `paper/paper.tex` §VII states the winding is segmented for redundancy, while `motor_model`
> charges copper for the whole 1.30 m. Whether that was deliberate conservatism or an
> inconsistency was recorded nowhere, which is why it was a defect rather than a finding.
>
> **ADR-022, 2026-08-10: the winding is segmented for *fault isolation* and driven as a single
> energised section.** `vol_cu = ACCEL_ZONE` stands and no baseline value moves. Both branches
> were priced first, by re-running the real pipeline with the energised length as a parameter:
>
> | | Whole winding, adopted | ~One sled length | 4 segments |
> |---|---:|---:|---:|
> | Copper per shot | **834.7 J** | 218.3 J | 208.7 J |
> | Net efficiency | **20.99 %** | **28.07 %** | 28.22 % |
> | Phase inductance | 19.70 µH | 5.15 µH | 4.92 µH |
> | **Exit velocity** | **16.388** | **16.388** | **16.388 m/s** |
>
> **The last row is why.** Force is commanded, so copper loss is a power draw and not a thrust
> reduction — segmentation changes what the shot *costs*, never what it *delivers*. The earlier
> "nearer 24 %" estimate in this file is superseded; the real figure is **28.07 %**.
>
> **It was declined for Phase I on mass, not on physics.** Efficiency appears in no kill
> criterion; mass appears in the one crossed by a factor of three, and block commutation costs an
> inverter per segment or a switching assembly, none of it in the rollup (**P10**).
>
> **So everything below still assumes something Phase I does not do.** Block commutation is now
> **PII-12** upstream, with a stated entry criterion: P10 closing with margin, or some claim
> becoming efficiency-limited. **PII-11's efficiency case is contingent on PII-12 being taken
> first**, and that dependency was not visible before this note.

## 1. Track length, at constant force

`v = sqrt(2aL)`. The machine is thrust-and-mass limited, not acceleration-limited, so extending
the track at unchanged commanded force leaves acceleration at **10.7 g** the whole way. No
qualification margin is spent, no current density changes, K<sub>t</sub> is untouched, and the
release is untouched.

| Deployed | Exit velocity | Pulse | Peak current | Lifetime multiplier |
|---|---|---|---|---|
| 1.30 m, today | 16.54 m/s | 157 ms | 296 A | x1.624 |
| 2.00 m | 20.51 m/s | 195 ms | 376 A | x1.806 |
| 3.00 m | 25.12 m/s | 239 ms | 481 A | x2.032 |
| 5.00 m | 32.42 m/s | 308 ms | 694 A | x2.424 |

Velocity goes as `sqrt(L)` and the mission number moves much less than the machine number: **a
2.5x track buys 1.5x velocity and 1.25x lifetime.** That diminishing return is the reason the
next section matters more than this one.

## 2. The prize: full regenerative arrest, and no eddy brake

A deployed track can be long enough to do both jobs. Release the payload part-way, then
regeneratively brake the sled to rest over the remainder. At the rated sheet current the sled
needs `m_sled/(m_sled + m_sat) = 0.70` of the acceleration distance to stop, so release at
`L/1.70`.

| Deployed | Accel | Brake | Exit velocity | Sled KE | Recovered | Copper | **Efficiency** | Multiplier |
|---|---|---|---|---|---|---|---|---|
| 1.70 m | 1.00 | 0.70 | 15.72 m/s | 1167 J | 939 J | 145 J | **45.2 %** | x1.588 |
| 2.60 m | 1.53 | 1.07 | 17.92 m/s | 1517 J | 1241 J | 161 J | **46.8 %** | x1.686 |
| **3.30 m** | **1.94** | **1.36** | **20.18 m/s** | **1924 J** | **1592 J** | **186 J** | **48.0 %** | **x1.790** |
| 5.00 m | 2.94 | 2.06 | 24.85 m/s | 2917 J | 2450 J | 226 J | **49.6 %** | x2.018 |
| 6.60 m | 3.88 | 2.72 | 28.55 m/s | 3850 J | 3253 J | 259 J | **50.0 %** | x2.211 |

Against **21.2 %** today. Three things make this better than it looks:

1. **Regeneration peak current stays below the shot's own** — 274 A against 369 A at 3.30 m — so
   the drive is not re-rated. Braking power is highest at release and falls with velocity, while
   the shot's peak comes at the end.
2. **The eddy brake, the copper fin and the ring spring all disappear.** 2.88 kg of hardware, and
   with them **P28**, the packaging conflict between the 240 mm regen stator and the 300 mm fin
   that A11 opened. There is no fin to conflict with.
3. **Every metre of brake track is copper already paid for.** On a fixed-track machine a
   regenerative brake section is added hardware; here it is the same track running backwards.

Note the shape: efficiency saturates near 50 % because the sled's energy round-trips through the
converter twice at 95 % each way, and the payload is only 30 % of the moving mass. **50 % is the
asymptote of this architecture, not a target to push past.**

## 3. It is the only lever that fixes the envelope

P9: the closed envelope is 1839 mm against ESPA Grande's ~1270 mm, **44 % over**, because the
brake sits beyond the 1500 mm release point and the enclosure must span it.

Nested sections with 150 mm of overlap per joint, plus 100 mm of end structure:

| Deployed reach | Sections | Stowed | Against ESPA Grande |
|---|---|---|---|
| 3.75 m | 4 x 1.05 m | **1150 mm** | **fits** |
| 4.15 m | 4 x 1.15 m | 1250 mm | **fits** |
| 5.15 m | 5 x 1.15 m | 1250 mm | **fits** |

Today: 1839 mm stowed, 1.30 m of stroke. A four-section track stows **689 mm shorter** and
delivers **2.9x the stroke**. Every other option in
[`DESIGN_OPTIONS_exit_velocity.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/DESIGN_OPTIONS_exit_velocity.md)
trades envelope against velocity. This is the only one that buys both, and it does it by
decoupling stowed length from stroke, which is a thing no fixed track can do.

**"Deployable" and "retractable" are different requirements.** On a hosted upper stage, deploy-once
is sufficient and retraction adds a second mechanism, a second failure mode and no benefit this
document can find. Retraction should be justified separately if it is wanted at all.

## 4. What it costs

| Deployed | Exit velocity | ESR ceiling | Bank strings | Track added | Net mass | kg per satellite |
|---|---|---|---|---|---|---|
| 1.70 m | 14.49 m/s | 92 mohm | 3 | 2.6 kg | −0.3 kg | 7.47 |
| 2.60 m | 17.92 m/s | 72 mohm | 3 | 14.2 kg | 11.3 kg | 8.43 |
| **3.30 m** | **20.18 m/s** | **62 mohm** | **3** | **23.2 kg** | **20.3 kg** | **9.18** |
| 5.00 m | 24.85 m/s | 47 mohm | 4 | 45.0 kg | 48.7 kg | 11.55 |
| 6.60 m | 28.55 m/s | 38 mohm | 5 | 65.6 kg | 75.8 kg | 13.80 |

Net mass credits the deleted eddy brake and charges extra supercapacitor strings; the baseline
column is against a **3-string** bank, which is the honest current position under P26 rather than
the single string the flagship draws.

- **Mass is the real cost.** Track is 4.84 kg/m of copper plus 0.75 kg/m of formers plus longerons,
  and telescoping adds roughly 60 % to the structural part for overlaps, rails and latches. At
  PocketQube class the per-satellite number is 110.2/326 = **0.34 kg**, still ahead of a cold-gas
  module, so the payload ladder absorbs this. At 3U it does not.
- **The bank does not get worse until about 4 m.** 62 mohm at 3.30 m against 66 today, still three
  strings. Segmentation is what pays for that: it cuts the copper term out of peak power.
- **Deployed stiffness collapses and stowed stiffness improves.** First mode 10 Hz deployed at
  3.30 m against 48 Hz today, but **170 Hz stowed at 1.15 m sections**, so the launch vibration
  case gets easier and the on-orbit dynamic case is new. Buckling under the 1413 N thrust reaction
  is a non-issue: 40.6x margin at 3.30 m, 17.7x at 5 m.
- **A failure mode that does not exist today.** A fixed track cannot fail to deploy.

> **Re-examined 2026-08-20. This section transfers to Gen6 with its sign reversed.**
> The argument below rests on a **1 mm airgap** in an ironless machine, where gap error costs
> thrust rather than running away. **Gen6's 8.0 m bore has a sliding seal in it, and a seal's job
> is to maintain contact** — so the tolerance that makes a deployed *track* plausible does not
> exist for a *bore*. [A59](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A59_tube_structure.md)
> already found the tube needs **seven supports**, and **P67, P88 and P89** inherit the
> consequence. *The arithmetic below is still right. It just stopped being good news.*

## 5. The straightness requirement has been overstated, including by PII-8

`cad/parameters.json` `groups.sled.airgap_per_side = 1.0 mm`. **That is the contact limit.** The
0.05 mm figure quoted elsewhere is `gap_shim_tolerance`, an assembly spec for thrust uniformity at
13.1 %/mm — and thrust error is what the closed loop exists to reject.

[`PII-8`](PII-8_free_flyer.md) computes 0.7 to 2 ppm for a 30–300 m track by holding 0.2 mm over
the length. Against the real 1 mm clearance that is roughly 10 ppm at 100 m, and:

| | Straightness for contact clearance |
|---|---|
| Flagship today, 1 mm over 1.8 m | 555 ppm |
| **3.30 m deployed, 1 mm** | **303 ppm** |
| 5.00 m deployed, 1 mm | 200 ppm |

**A 3.3 m deployed track is a looser straightness requirement than the machine already meets.**
PII-8's numbers should be corrected; they overstate the hardest problem in that document by
several times.

**Being ironless is what makes this true.** In an iron-cored linear motor an off-centre gap
produces a large destabilising normal force that grows as the gap closes. An ironless winding in a
symmetric Halbach field does not, so gap error costs thrust rather than causing runaway. This is
the single design decision that makes a deployed track plausible, and it was made for other
reasons.

**The real problem is joints, not bow.** A smooth 1 mm bow over 3.3 m is easy; a **step** at each
telescoping joint is not, and nothing here shows anyone can hold one. That is the first thing to
compute.

---

## 6. The side-rail layout, priced

Two rails either side of the payload instead of one track beneath it. Halbach thrust scales as
`(1 − e^{−kt})` with `k = 2π/λ = 130.9 /m`, the repo's own law from `sizing.pole_pitch_sweep`
(it reproduces the re-integrated 6 mm and 5 mm rows of `DESIGN_OPTIONS` to 2 %):

| Magnet thickness | Relative K<sub>t</sub> | N per kA/m per motor |
|---|---|---|
| 8 mm, today | 1.000 | 11.22 |
| 6 mm | 0.838 | 9.40 |
| 4 mm | 0.628 | 7.05 |

Diminishing returns are steep, so **two 4 mm arrays beat one 8 mm array by 25.6 % at identical
magnet mass.** That is a real gain and it is not enough:

| Configuration | Sled | Exit velocity | Accel | Copper | Efficiency | ESR ceiling |
|---|---|---|---|---|---|---|
| **A** one stator under the sled | 9.45 kg | **16.53 m/s** | 10.7 g | 827 J | **19.0 %** | **67 mohm** |
| **B1** split, 45 mm depth each, 8 mm mags | 10.95 kg | 15.68 m/s | 9.6 g | 873 J | 16.8 % | 69 mohm |
| **B2** split, 90 mm depth each, 4 mm mags | 10.95 kg | 17.58 m/s | 12.1 g | 1557 J | 14.7 % | 43 mohm |
| **C** split, 90 mm depth each, 8 mm mags | 15.12 kg | 19.61 m/s | 15.1 g | 1396 J | 13.4 % | **25 mohm** |

B1 is the neutral split: two 45 mm rails have the same K<sub>t</sub> and the same copper as one
90 mm stator, so **splitting is electromagnetically free** and only the frame mass moves. B2 buys
6 % velocity for 23 % less efficiency and half the bank ceiling. C reaches 19.6 m/s and drops the
ceiling to **25 mohm, six to eight parallel strings** — the two-layer stator problem arriving from
a third direction. Every lever that raises force raises current, and the bank is what breaks.

**So do not sell this as a velocity lever. It is not one.**

### What it is actually for

`cad/parameters.json` `groups.sled.payload_com_offset_above_thrust_line = 70`.

The payload's centre of mass sits **70 mm above the thrust line**. Every shot:

```
payload inertia force   4.0 kg x 105.1 m/s^2  = 420 N
pitching moment         420 N x 0.070 m       = 29.4 N.m
reacted over the 250 mm roller base           = 118 N per roller pair
```

Structurally that is nothing against 18.5 kN of arrest load. But it is **the driving term for
tip-off**, and tip-off is the least validated claim in the design: A7 has not run, and its declared
band (≤5 °/s citing NRCSD-E) already disagrees with the sibling NRCSD ICD at 2 °/s, unresolved.

**A symmetric layout puts the thrust line through the payload CoM and drives that term to zero.**
Not smaller — gone. That is worth more than a metre per second, and it is the reason to look at
this at all.

Three more things fall out, none of them about thrust:

- **The array attraction drops.** At 4 mm per side the inter-array Maxwell load is **1.45 kN
  against 3.68 kN**, and side-plate stress 13 MPa against 33. The split structure is genuinely
  less loaded, which pushes back on the frame-mass penalty assumed above.
- **Two motors give differential control**: command a differential force to null residual moment
  or bias the release direction. One track cannot do that.
- **Graceful degradation.** One rail failing halves thrust rather than ending the campaign — a
  stronger version of the segmented-winding redundancy the paper already claims.

### And it is the right topology for a deployed track

Two rails can be **pretensioned between end fittings**: a determinate, tensioned deployed
structure whose straightness comes from tension rather than from bending stiffness. A single track
beneath the sled can only be a beam, and cannot be pretensioned against anything. **If the
deployable track is built, this is probably how.** That is why these are one item.

### Checked and closed: the magnets stay on the sled

Putting magnets on the rails and the winding on the sled removes the long stator, but magnets cost
**10.79 kg per metre against copper at 4.84**, 2.2x heavier. Long stator is the right choice and
becomes more right as the track lengthens.

---

## 7. The number that actually decides it

```
dv/dm_sled = -v/(2*m_total) = -0.615 m/s per kilogram
```

The flagship's mass rollup carries **4.59 kg of unexplained "CAD reconciliation"** on the sled:
the drawn chassis is far heavier than its itemised parts, and it is still
`PROVISIONAL_PENDING_FEA`. A frame carrying loads in **tension between two rails** may well be
lighter than a plate cantilevering the payload above a track — the attraction load per side is
2.5x smaller, which helps.

| Frame mass change | Exit velocity |
|---|---|
| −2 kg | 17.92 m/s |
| 0 | 16.53 m/s |
| +2 kg | 15.43 m/s |

**That is the whole decision, and nobody can settle it without designing both.** Everything else
in section 6 is second order next to ±2 kg.

---

## The hard problems, named next to the numbers

1. **Steps at the telescoping joints.** Section 5 shows the *straightness* requirement is looser
   than the current machine's. It says nothing about whether a nested joint can be held to a
   fraction of the 1 mm clearance, repeatably, after launch vibration and thermal cycling. **This
   is the item that decides the architecture** and it should be studied before anything else.
2. **Frame mass, and it is worth 2 m/s either way.** Section 7.
3. **Deployed dynamics.** A 10 Hz structure under a 239 ms thrust pulse is two and a half cycles,
   which is transient, not quasi-static. The gap variation that produces has not been computed.
   Buckling is fine; ringing is the question.
4. **Deployment reliability.** A single-point failure that a fixed track does not have. Whatever
   the mechanism, it must be single-fault tolerant or the whole manifest is lost.

## The deliverable

**A mass and stiffness estimate for a symmetric frame between two rails, against the current
cantilever chassis, and a joint concept with a straightness budget.** Both are mechanical design
rather than analysis, and both are cheap compared with what they settle. Everything else in this
document is arithmetic that already exists in `analysis/`.

> **Entry criterion for promotion to Phase I: none, deliberately.** This is a fundamental
> architecture change and `docs/BASELINE.md` puts those in Phase II by type. The correct outcome
> for the thesis is that PII-11 stays closed: the flagship has three crossed kill criteria, one
> failed validation and no measured number, and those come first. The one piece of this that does
> belong upstream is **P29**, the stator segmentation question, because that is an inconsistency
> in what is already published rather than an improvement.
