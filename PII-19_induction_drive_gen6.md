# PII-19: the induction-drive Gen6, and the day it was the target

**Adopted 2026-08-13 by ADR-029. Superseded 2026-08-14 by ADR-032. Nothing in it was refuted.**

> **Why it stopped, in one sentence.** The mover it spent its whole design effort making lighter
> turned out to be **11 % of dry mass**, so this is a careful, banded, correct optimisation of the
> wrong term.

## What it was

A linear induction drive on a **passive aluminium mover** — a 0.25 kg plate instead of a 9.445 kg
permanent-magnet sled. No magnets anywhere on the moving part. Arrest of **82 J instead of 1938**.
The satellite untouched.

It was assembled from the vault rather than invented: **PII-18**'s plate-as-shuttle, **PII-1**'s
momentum-conserving release, and the observation that a light mover makes the 25 g qualification
headroom affordable. It reached **850 mm of stroke at 16.1 g** against Gen5's 1300 mm at 10.1 g.

## The evidence it carries, which stands

**Nine measured bands**, declared before their scripts as always:

| | |
|---|---|
| **A30** bands 4–5 | The rail-drive variant, and the measurement that killed it |
| **A31** bands 1–4 | Normal force on the plate, against the magnetic-pressure ceiling |
| **A32** bands 1–2 | The entry transient, and the segment-crossing ripple |

**A30 is the one worth keeping.** The rail drive was sized on a transverse edge factor of **0.55**
and measured at **0.0253** — a factor of 22. The Russell–Norsworthy factor collapses as
(πc/τ)²/3 for a secondary narrower than the pole pitch, and a CubeSat's corner rails are very
narrow indeed. **That is a measurement, not an opinion, and it is why PII-16 is struck through.**

**A32 band 4 is the one that was still open.** Thrust ripple at a segment boundary is **30.1 %
peak-to-peak** against a 20 % band, and it is not the joint gap — closing the gap to zero leaves
25 %. The cause is longitudinal truncation of the travelling field, intrinsic to a segmented long
stator with a short secondary. With four segments the crossing frequency sweeps **0 → 61.5 Hz**
through a track whose first two modes are at 48 and 109 Hz. **P52 records it and it is still open.**

## Why it stopped, at length

**A35 attributed every kilogram in the machine to the requirement that causes it.** Three numbers
came out of it and all three point away from this design:

| | |
|---|---|
| The mover, as a fraction of **dry mass** | **11 %** |
| The mover, as a fraction of **accelerated mass** | **70 %** |
| The pulse chain — stator, bank, converter, thermal | **28.1 %** |

**Both mover figures are true and they say different things.** This architecture read the second
and optimised it: 70 % of every joule went into launcher hardware, so making the mover light was
obviously right. **It is right, and it buys 11 % of the mass.** The 49.23 kg that survives every
requirement deletion in all 64 corners does not care how light the plate is.

**The pulse was the term worth attacking, and this design keeps it.** An induction drive still
needs a stator, still needs a bank, still needs the 17 kW that P26 says no commercial capacitor
string can source. ADR-032 deletes all of it by moving the energy delivery off the shot and into
the sixty seconds already spent indexing — **25 to 131 W**.

**The sibling repository is the corroboration.** BOLLEY deleted the mover a different way, by
putting a passive cage on the satellite, and its primary grew back to **15.91 kg** because it kept
the pulse. Two architectures, opposite premises about payload modification, same conclusion:
**the mover is not where the mass is.**

## What replaced it

**ADR-032.** The payload accelerated directly, by gas, along a rail the spent stage provides. No
mover at all rather than a light one, which deletes this entry's entire subject.

## Entry criterion

**None, and deliberately.** This is not held for a future baseline boundary — it is superseded, and
what superseded it did so by measuring a quantity this design never questioned.

**It is here because two things in it outlive it:** A30's edge-factor measurement, which kills any
future proposal to use a CubeSat's own rails as a secondary, and A32 band 4's segment ripple, which
applies to **any** segmented long stator with a short secondary and will be rediscovered by anyone
who proposes one.
