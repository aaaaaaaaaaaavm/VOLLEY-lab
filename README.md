# VOLLEY-lab

**The vault: ideas that never became a complete thing, and the measurement that stopped each one.**

Most projects delete the work that did not finish, and the reasoning goes with it. This is where
the VOLLEY programme keeps it instead — an architecture priced and declined, a scaling study
answering a question nobody has asked yet, a measurement that killed something.

**It is a vault rather than a graveyard, and the difference is that a vault is organised for
retrieval.**

<!-- PROGRAMME-HEADER-START -->
| Repository | Role | You are here |
|---|---|---|
| [VOLLEY](https://github.com/aaaaaaaaaaaavm/VOLLEY) | Main: the authoritative engineering record. Improved continuously |  |
| [VOLLEY-paper](https://github.com/aaaaaaaaaaaavm/VOLLEY-paper) | The concept at its most reliable, as a conference contribution. **Frozen when published** |  |
| [VOLLEY-thesis](https://github.com/aaaaaaaaaaaavm/VOLLEY-thesis) | The same concept as a full submission. **Frozen when presented** |  |
| **[VOLLEY-lab](https://github.com/aaaaaaaaaaaavm/VOLLEY-lab)** | The vault: ideas that never became a complete thing, and why each stopped | ← |
<!-- PROGRAMME-HEADER-END -->

> **Nothing here should be cited.** No baseline, no stability promise, no acceptance bands.
> Numbers on these pages may be wrong, half-finished or abandoned mid-thought. The engineering
> record is [VOLLEY](https://github.com/aaaaaaaaaaaavm/VOLLEY), and where anything here disagrees
> with it, **it is right and this is not**.

## What this repository is for

**The main record stays clean because this exists.** A research track kept *inside* it is one
`git checkout` from becoming an edit to the record; a separate repository is a wall rather
than a line on the floor.

## The one rule

**Every entry states why it stopped.**

Not "deferred" — *why*, with the number that decided it. The rail-drive entry upstream carries
the transverse edge factor of **0.0253** that killed it, against the **0.55** it had been sized
on. PII-14 below carries the drivetrain inertia that eats its own gain. PII-19 carries the **11 %**
that made a whole architecture the wrong answer. **That is what makes this evidence rather than a
pile**, and it is the only rule here.

> ### Nine entries stopped together on 2026-08-14
>
> [ADR-032](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/032-gen6-stage-integrated-gas-store.md)
> made the payload accelerate directly, by gas, along a rail the spent stage provides — and
> **deleted the subsystem that nine vault entries improve.** No mover, so PII-1, PII-2, PII-17 and
> PII-18 have nothing to act on; no stator, so PII-3 and PII-12; no bank, so **PII-7**, which was
> P26, the largest live defect the project carried; no envelope and no track, so PII-4 and PII-11.
>
> **Not one was refuted.** Each is a correct optimisation of a part that stopped existing, and
> **PII-1's own arithmetic is why the mover went**. The full list is in the main repository's
> [`docs/VAULT.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/VAULT.md).
>
> **PII-8 gains.** Its hardest problem was airgap straightness over a deployed structure, and the
> new architecture has no airgap.

An entry without a reason is not deferred. It is abandoned with extra steps.

## What is here

Long-form entries live in this repository. The complete register — every entry, its status
and its entry criterion — is kept in the main repository so the numbering cannot fork:
**[`docs/VAULT.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/VAULT.md)**.

| | |
|---|---|
| [**PII-8** — VOLLEY as a free-flyer](PII-8_free_flyer.md) | A long deployed track and release at perigee reaches TLI and Mars-class C3 without exceeding CubeSat qualification. **Stopped by three problems named in the file**: airgap straightness at 0.7–2 ppm over a deployed structure, a 294 kJ shot against a bank that already fails at 2.88 kJ, and whether 25 g survives review as a *sustained* load |
| [**PII-9** — the lunar case](PII-9_lunar.md) | Where this technology has always belonged, and the mass driver it descends from. 1.33 MJ/kg to lunar orbit, so 15 kW launches a tonne a day. **Stopped by having no host**: it describes a different programme, not this one. The payload is ore, so the g-limit governing the whole design disappears |
| [**PII-11** — a deployable track, and the side-rail layout](PII-11_deployable_track.md) | A telescoping track long enough to accelerate *and* regeneratively arrest reaches **48 % electrical-to-payload efficiency**, deletes the eddy brake and stows inside the ESPA Grande envelope the main design misses by 44 %. The only option that improves velocity and envelope together. **Stopped by type, not by number**: a deployable structure is an architecture change however good its numbers are |
| [**PII-14** — a cable-driven gondola on a deployed truss](PII-14_cable_driven_gondola.md) | Propulsion off the vehicle onto a cable, energy from a flywheel. **Stopped by the assumption inside its own headline**: +49.7 % assumed a drivetrain with zero rotating inertia, and a real one gives +15 to +30 %, possibly zero — in exchange for deleting the linear synchronous motor and the 24 validations behind it. Its two dead ends are recorded too, because both will otherwise be re-proposed |
| [**PII-19** — the induction-drive Gen6](PII-19_induction_drive_gen6.md) | A linear induction drive on a 0.25 kg passive plate instead of a 9.445 kg magnet sled. **It was the main repository's design target for one day.** **Stopped by attribution, not refutation**: A35 measured the mover it optimises at **11 % of dry mass**, so the whole synthesis is a careful, banded, correct optimisation of the wrong term. Its nine measured bands stand |
| [**PII-21** — water as the working fluid, in three forms](PII-21_water_working_fluids.md) | Pressurised water, solar steam, and electrolysis to H2/O2, replacing cold nitrogen. **Stopped three different ways.** Liquid water stores **2.35 J against 2350 needed** — wrong physics for a gun. Electrolysis is a 3000 K chamber beside eleven stowed satellites and attacks the commanded-velocity claim. **Steam works** — the solar heating closes at 57.3 W with no concentrator, the fluid does more work on a third of the mass, and the shot is gentler — **but staying dry needs a bore above 473 K, and the steel tube that forces costs 2.154 kg, more than everything water removes.** ADR-035 then chose aluminium on mass alone |
| [`notes/`](notes/) | Unstructured, date-stamped, finished by nobody |

**PII-11 is the one that is hardest to leave shut**, because unlike the others it improves the
machine actually being built rather than describing a different one. That is exactly why it
needs a gate.

## Checked against outside evidence, 2026-08-20

**Every entry here was asked one question: did it stop on a number that came from inside the
programme?** That is the only kind of stop an outside source can move. The full map is
[`EXTERNAL_EVIDENCE.md`](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/EXTERNAL_EVIDENCE.md)
upstream. **Four outcomes:**

| | |
|---|---|
| **Most of the vault is unmoved, and that is not a failure of the check** | Nine entries stopped because [ADR-032](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/032-gen6-stage-integrated-gas-store.md) deleted the subsystem they improve. **PII-8** and **PII-9** describe different vehicles. *No literature resurrects an optimisation of a part that stopped existing, and no source supplies a host* |
| **PII-19 has a live route back** | Its stop — the mover is 11 % of dry mass — was about Gen5's whole drive. **Gen6 has a 144.01 mm motor at the muzzle with this entry's exact problem**: [ADR-033](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/033-gen6-trim-stage.md) brought magnets back to the moving part and paid **P34**, **E35** and a cradle alignment duty for them. **A passive secondary pays none of it.** And **A30's 0.0253 edge factor** may kill it — 24 mm pole pitch against a 15.805 mm bore. **Unrun** |
| **PII-14's flywheel is closed, in the losing direction** | It was split out as a candidate against **P26**. That question is now Gen6's pulse store, and **A64 answered it at ~70 g on published capacitor data.** *Bearings, containment and 7.15 N·m·s of stored angular momentum do not beat seventy grams* |
| **PII-11 §5 transfers with its sign flipped** | Its straightness argument rests on a **1 mm airgap** that costs thrust when violated. **Gen6's 8.0 m bore has a sliding seal in it**, which must maintain contact. The tolerance that made a deployed track plausible is not there — and **P67**, **P88** and **P89** inherit it |

> **The most valuable thing the check produced is not in this repository.** Reading PII-19 against
> ADR-033 meant reading how the present stator reaches its magnets — **through the drive tube**,
> which [ADR-035](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/035-drive-tube-material.md)
> made aluminium four days after the stator was placed outside it. **Nothing owned the interaction.
> That is now P92 upstream.**
>
> **The entry did not come back. Reading it found a defect in what replaced it.** *That is an
> argument for keeping a vault, and it is not the argument the vault was built on.*

## Can any of these come back? — reviewed 2026-08-20

**One can, in a restricted form. The rest cannot, and three are stronger for having been asked.**

| | Verdict |
|---|---|
| **PII-8** | **The only live route back.** Two of its three stated blockers no longer exist — [ADR-032](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/032-gen6-stage-integrated-gas-store.md) deleted the airgap, and the bank its 294 kJ was measured against. **What remains is one standards question it already cites against itself** — the CubeSat quasi-static case at about 14 g, where every table in the file is computed at 25 — **and one number nobody in this programme has computed: the thermodynamic velocity ceiling of a gas expansion.** That single figure decides the entry |
| **PII-19** | **Its idea has a route back; the entry does not.** A passive secondary is aimed at Gen6's trim stage, not its drive. **A30's own 0.0253 edge factor may kill it** — 24 mm pole pitch against a 15.805 mm bore |
| **PII-21** | **Reopens on a catalogue lookup, not a study.** A59 left the tube choice on two numbers, density and service temperature. If any alloy class clears T_sat(p₀) at aluminium's density, **every steam number here comes back unchanged** |
| **PII-11**, **PII-14**, **PII-9**, and the nine ADR-032 deletions | **No.** Motor-dependent, cable-dependent, or a different programme. *PII-14's flywheel is now formally closed rather than left ajar, and PII-11's straightness argument transfers with its sign reversed* |

> **The bank objection was doing more work in this vault than anyone noticed.** **PII-8**,
> **PII-9** and **PII-14** each stopped partly on *"the capacitor bank cannot source this"*.
> ADR-032 deleted the bank and A64 re-priced what replaced it — **so one retirement quietly
> retired a blocker in three separate entries**, and none of them had been re-read since.
>
> **That is the argument for re-reading a vault on a schedule rather than on demand.** *A stop is
> not scripture either.* An entry can be wrong about why it stopped, and the most common way is
> that the thing it was blocked by stopped existing.

## How something leaves

| From → to | Condition |
|---|---|
| **vault → main** | Its acceptance bands were declared **before its script existed**, and run |
| **main → paper / thesis** | Stable, effective and reliable against the problem statement |
| **paper / thesis → frozen** | Presented or published |

**Nothing crosses upward on enthusiasm.** An item is promoted by meeting the criterion it was
given — written when it was deferred, not when it is reviewed, because a criterion written
afterwards is written by someone who already knows what they want the answer to be.

## What does not belong here

**Corrections.** If something in the main repository is *wrong*, fix it there. The distinction
is by type, not by convenience: a tedious bookkeeping error belongs upstream, and a fascinating
architecture belongs here.

## Adding an entry

Name it. State what it buys, with a number. Say why it is improvement rather than correction.
Then write its entry criterion **before you stop thinking about it** — and when it stops, write
down what stopped it.

## Licence

**CC BY 4.0** — full text in [`LICENSE`](LICENSE), attribution form in [`NOTICE`](NOTICE).
Attribution requires credit, a link to the licence, and **an indication of whether changes were
made**.

**Not retroactive:** snapshots taken before this change remain available under the MIT licence
they carried at the time, retained at [`LICENSE-MIT-superseded`](LICENSE-MIT-superseded).

This repository carries copies of VOLLEY analysis code under `reference/volley/`. CC BY 4.0 does
not license patent rights, which is why a patent-granting licence was not used here.
