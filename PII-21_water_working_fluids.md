# PII-21: water as the working fluid, in three forms

**Proposed 2026-08-20. Stopped 2026-08-20 by [ADR-035](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/035-drive-tube-material.md) and by arithmetic. Nothing in it was refuted.**

> **Why it stopped, in one sentence.** **Steam works and is not worth it**: it needs a bore above
> 473 K, which forces a steel tube that costs **2.154 kg — more than everything water removes** —
> and the material decision went to aluminium on its own merits.

## What it was

**Replace the cold nitrogen working fluid with water**, in one of three forms. The gun is unchanged
in every case: a pre-charged chamber firing a piston down a tube, exactly as ADR-032 and ADR-034
specify. **Only the fluid and how it is charged differ.**

| | |
|---|---|
| **Pressurised liquid water** | water as the store itself, compressed |
| **Steam** | water raised to vapour by **solar flux alone** — no heater, no combustion |
| **Electrolysis to H₂/O₂** | water split by solar power over the inter-shot window, then combusted |

**The motivation was the 200 bar composite pressure vessel.** [A56](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A56_reservoir_resized.md)
sized the nitrogen store at **3.1216 kg**, of which the vessel and its gas are **1.283 kg** — and a
water tank is a low-pressure part with no burst-safety case and a much shorter conversation with a
launch provider.

## Pressurised liquid water — stopped on bulk modulus

**2 L of water compressed by 22.73 bar stores 2.35 J. The shot needs 2350 J.**

> **Short by a factor of 1001.**

Water's bulk modulus is **2.2 GPa**; it is incompressible and stores essentially nothing. If the
water is instead pressurised *by* a gas blanket, **the gas is doing the work and the water is dead
mass.** *This is not an engineering shortfall to be closed. It is the wrong physics for a gun.*

## Electrolysis to H₂/O₂ — stopped on architecture, not energy

**The energy case is excellent** — roughly **8.5 g of water for a twelve-shot campaign** at
plausible efficiencies, and a few watts of electrolysis across the 1200 s cadence.

**Four objections, and the fourth is the one that matters:**

- **It is a ~3000 K combustion chamber beside eleven stowed, unmodified customer satellites.** The
  drive tube is a 1.0 mm wall, not a rocket engine.
- **It re-adds two pressure vessels**, for H₂ and O₂ separately. The thing water was meant to delete
  comes back doubled.
- **An igniter is a new manifest-forfeiting shared element** in an FMEA that already counts eight
  ([A47](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A47_gen6_fmea.md)).
- **It replaces a cleanly-commanded charge pressure with ignition timing, mixture ratio and
  flame-front variability.** [A44](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A44_gen6_dispersion.md)
  measured velocity commanding at **0.499 % per 1 %** of charge pressure. **This attacks the one
  claim the machine is sold on.**

**Water electrolysis propulsion is flown** — it is not speculative — but every flown system is a
*thruster*, where specific impulse is the figure of merit. **A gun is sized by pressure-volume work
released in milliseconds, and Isp says nothing about it.**

## Steam — the one that was run properly, twice

**[A62](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A62_steam_working_fluid.md)
screened it at nitrogen's design point and was wrong to.** Every figure came from a 2.0 L chamber
sized by A41 for a different fluid. **That is recorded as P90 and the run sheet is annotated rather
than rewritten.**

**[A63](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A63_steam_design_point.md)
swept 108 points. Eight of ten bands. What it found is worth keeping:**

| | |
|---|---|
| **The heating works** | **57.3 W**, **α/ε 6.4** — inside the selective-coating class, **no concentrator and no sun-tracking**. A **27 cm square** absorber, and it **survives eclipse** because the low emissivity that makes the coating work also makes it a poor radiator |
| **The fluid is better** | **101.98 %** of nitrogen's shot work on **35.1 %** of the charge mass — molecular weight 18 against 28, γ 1.33 against 1.4 |
| **The shot is gentler** | **34.33 m/s at 10.00 g** against nitrogen's 34.28 at **11.36** |
| **Propellant halves** | **296 g** against 612 g over a campaign |
| **The seal survives** | 43 of 108 points sit inside filled PTFE's 533 K limit, so [A61](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A61_seal_class.md)'s 17.8 N specification holds |

**And then the bore temperature settles it.**

**The expansion must end above the saturation line or it condenses**, and the floor on the charge
temperature is **T_sat(p₀) itself**. Every charge pressure that makes 2350 J puts that floor above
**473 K — aluminium's limit. Zero of 108 points reach it.**

| At the best point, 20 bar and 3 L | |
|---|---:|
| Removes — vessel, gas, old chamber | **−1.622 kg** |
| Adds — water, tank, a larger chamber, **and a steel tube** | **+3.434 kg** |
| **Net** | **−1.813 kg** |

> **The steel tube penalty alone is 2.154 kg — larger than everything water removes.** And **none of
> the 43 feasible points is a saving.**

## The conditional, and the decision that closed it

**A63 found that if the tube were steel for reasons independent of the fluid, steam stops paying for
it and becomes +0.341 kg.** The tube material was genuinely undecided at that moment — **P85**.

**[ADR-035](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/035-drive-tube-material.md)
decided it on 2026-08-20, and it went to aluminium.** Strength, stiffness and buckling were all
indifferent between the metals; matching the piston and bore removes the thermal differential
whichever is chosen; **so the decision fell to 2.154 kg**, which is 0.18 kg per satellite against
the project's tightest threshold.

**Steam is foreclosed by a decision taken on its own merits, not by a judgement about steam.**
*ADR-035 falsifier 4 names this: if a fluid change is ever forced, that ADR is what has to move
first.*

## What would reopen it

- **A working fluid that stays dry below 473 K.** The constraint is thermodynamic, not about water:
  *any* condensable fluid faces the same floor at its own saturation curve.
- **A tube material with aluminium's density and a higher ceiling**, which is a materials question
  this project has not asked.
- **A requirement that values deleting the COPV above 2.154 kg** — a launch-provider constraint, a
  range-safety objection, or a customer who will not fly beside a 200 bar vessel. **That is the most
  likely of the three, and it is an external decision rather than an engineering one.**

**Nothing here was refuted. The heating works, the fluid is better, and the machine that has to
contain it is worse by more.**
