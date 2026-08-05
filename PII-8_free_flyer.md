# PII-8: VOLLEY as a free-flyer, and how it would reach translunar and Mars

> **Baseline note, 2026-08-05.** The Phase I numbers this file compares against have moved.
> The 2026-08-03 quadrature correction gives Kt = 11.03 N per kA/m, 16.388 m/s at 10.53 g,
> 2.85 kJ gross and 2.56 kJ net, 20.99 % net efficiency and a 68 mohm bank ESR ceiling. Figures
> below written at 11.22, 16.53 m/s, 10.7 g, 2.88 kJ or 19.0 % predate it. The **ratios and
> conclusions** here are not sensitive to a 0.9 % shift in the comparator and are left as
> written; the absolute Phase I values are not current. `docs/BASELINE.md` in the flagship is
> authoritative.

**Phase II. A programme direction, not a deferred fix.** Nothing here is in the flagship
baseline and the thesis does not depend on it.

**The claim, stated before the argument so it cannot be mistaken for more than it is:** an
electromagnetic launcher cannot perform translunar injection unaided. TLI from LEO needs about
3150 m/s. Held to a CubeSat's 25 g limit, `v = sqrt(2aL)` puts that at **20.2 km of track**. The
launcher supplies an *injection*, not a *transfer*. A chemical stage does the transfer.

What follows is what the combination can do, which is more interesting than what either does
alone.

---

## Lever 1: a free-flyer is not bound by a rideshare envelope

The flagship's stroke is 1.3 m because it must fit an ESPA-class port, and it fails that anyway
by 44 % (P9). A free-flyer makes track length a design variable.

At the same 25 g cap that governs the flagship, so **no payload qualification is being stretched
anywhere in this table**:

| Deployed track | Exit velocity |
|---|---|
| 1.3 m, flagship | 25.3 m/s |
| 30 m | 121 m/s |
| 100 m | 222 m/s |
| 300 m | **384 m/s** |

**A 300 m track exceeds Feng et al.'s 321.56 m/s while staying inside CubeSat qualification.**
Feng buys velocity with 1352 g of acceleration; this buys it with distance. Same physics,
opposite side of the trade.

That is also the honest answer to "how do we get back above 200 m/s". It was always a
track-length problem, and the flagship's track length was always an envelope constraint rather
than a physics one.

## Lever 2: fire at perigee, where a m/s is worth twenty

Adding `dv` at perigee changes hyperbolic excess energy by `dC3 = 2*vp*dv`. On an ellipse with
perigee at 400 km and apogee at lunar distance, perigee velocity is **10.75 km/s**:

| Track | Exit velocity | C3 delivered | Reaches |
|---|---|---|---|
| 1.3 m | 25 m/s | 0.54 km²/s² | LEO phasing |
| 30 m | 121 m/s | 2.61 km²/s² | **TLI with margin** |
| 100 m | 222 m/s | 4.76 km²/s² | TLI with margin |
| 300 m | 384 m/s | **8.25 km²/s²** | **Mars-class C3** |

TLI needs about −1.9 km²/s²; Mars transfer about +8 to +16. **A 300 m track firing at perigee
puts a CubeSat on a Mars trajectory without exceeding 25 g at any point.**

## The architecture that follows

1. A chemical stage raises the mothership to a high-eccentricity parking orbit. About 3.1 km/s
   from LEO, **once**.
2. At each perigee pass, VOLLEY fires satellites individually.
3. Each gets its own C3, so one mothership burn produces many independent trajectories and
   arrival dates.

**One chemical burn, hundreds of independent injections.** Every orbital transfer vehicle on the
market burns propellant per deployment. This spends electrical energy, recharged by solar
between perigee passes. That is the differentiator worth testing, and it is a different claim
from "electromagnetic launch reaches Mars".

---

## The three things that decide whether any of this is real

### 1. Airgap straightness over a deployed track

The make-or-break item, and it should be studied before anything else.

> **Corrected 2026-07-31. The numbers below were computed against the wrong tolerance and this
> section overstated its own problem by roughly five times.** They held 0.2 mm over the length,
> taken from the flagship's `gap_shim_tolerance` of 0.05 mm. That figure is an **assembly spec for
> thrust uniformity** at 13.1 %/mm, and thrust error is what the closed loop exists to reject. The
> figure that cannot be violated is `cad/parameters.json` `groups.sled.airgap_per_side = 1.0 mm`,
> the **contact clearance**. Working to that:
>
> | | Straightness for contact clearance |
> |---|---|
> | Flagship today, 1 mm over 1.8 m | 555 ppm |
> | 100 m track, 1 mm | **10 ppm** |
> | 300 m track, 1 mm | **3.3 ppm** |
>
> Still hard, and still the make-or-break item. But an order of magnitude less hard than stated,
> and the distinction matters because it is what makes the much shorter deployed track of
> [PII-11](PII-11_deployable_track.md) *easier* than the machine already built rather than harder.
> **Being ironless is why this works at all**: an iron-cored machine develops a destabilising
> normal force as the gap closes, and an ironless winding in a symmetric Halbach field does not,
> so gap error costs thrust rather than running away.

The original figures, kept for the record:

| | Straightness required |
|---|---|
| Flagship today | 0.2 mm over 1.8 m = **111 ppm** |
| 100 m track | **2 ppm** |
| 300 m track | **0.7 ppm** |

Those already assume the gap is widened from 12 to 48 mm and the wavelength from 48 to 192 mm,
which buys back a factor of four in tolerance while preserving the field ratio `exp(-2*pi*g/λ)`.

Precision machine-tool ways achieve 1 to 5 ppm on a granite bed in a temperature-controlled
room. On a deployable structure with orbital thermal gradients, a single rigid 300 m beam is not
credible.

**The route is segmentation with active alignment**: roughly 66 segments of 1.5 m for a 100 m
track, each aligned to the local sled path rather than to one global line, the way segmented
telescope mirrors work. Nobody has costed this and it is the first thing to compute.

### 2. Energy per shot scales as v²

4 kg at 384 m/s is **294 kJ**, against 2.88 kJ today: a factor of **102**.

P26 already establishes that the flagship's bank cannot source 30 kW through a purchasable ESR.
This is not a bigger version of that problem, it is a different power system, and PII-7's
parallel-string answer does not scale to it. Rotational storage is the obvious candidate and is
explored in PII-9.

### 3. Sustained acceleration is a different load case

25 g for **1.57 seconds** over a 300 m track is a quasi-static load, not the transient a launch
qualification covers. The CubeSat Design Specification quasi-static case is about 14 g.

**The 25 g cap may not survive a real qualification review for a sustained application**, and if
it drops, every number in both tables above drops with it. This is the assumption most likely to
be wrong and it is load-bearing for the whole document.

---

## Who this would compete with

| | |
|---|---|
| **Impulse Space** | Mira for LEO to cislunar, Helios kick stage. The most capable |
| **D-Orbit** | ION Satellite Carrier. Flown repeatedly; the closest operational analogue |
| **Momentus** | Vigoride, 750 kg to LEO, three flights |
| **Launcher / Vast** | Orbiter, 90U of CubeSats. The most directly comparable carrier |
| **Atomos / Katalyst** | Quark: deployment plus servicing and docking |
| **Exolaunch** | Reliant, plus EXOpod Nova and CarboNIX. **Also a direct deployer competitor** |
| **Firefly** | Elytra |
| **Intuitive Machines** | OTV in development under contract |
| **Exotrail** | spacevan |
| **Bellatrix Aerospace** (India) | Pushpak |
| **Skyroot** (India) | Orbit Adjustment Module, already analysed as a flagship host |
| **NEC, Mitsubishi Electric** (Japan) | OTV programmes announced |

None offers per-satellite differential injection without propellant. **That is the claim PII-8
exists to test, and it is the only one worth making**: on mass, cost and flight heritage this
would lose to every name above.

---

## The deliverable

**Start with [PII-11](PII-11_deployable_track.md), not here.** It asks the same question at 3 to
5 m instead of 30 to 300, on the existing hosted architecture rather than a mothership, and it
reaches 48 % efficiency and an envelope that fits ESPA Grande. If a deployed track cannot be made
to work at 3 m it will not work at 300, and PII-11 is where the joint problem gets solved or does
not.

**A scaling law, not a design.** Using the flagship model as the datum: how thrust, sled mass,
track mass, segment count, bank energy and recharge time scale with track length and payload
class, and what a mothership sized for several hundred PocketQubes to TLI would mass.

Every term is already in `analysis/`. The output is a defensible statement of what the endgame
costs, so the decision to pursue it can be made against numbers rather than enthusiasm.

> **Entry criterion for promotion to Phase I: none, and deliberately.** This is not a candidate
> for the baseline. It becomes a programme only if the flagship's Phase I deliverables ship
> first, and the correct outcome for the thesis is that PII-8 is never opened.
