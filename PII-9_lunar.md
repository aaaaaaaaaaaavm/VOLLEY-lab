# PII-9: the lunar case, and the mass driver this descends from

Phase II. The Moon is the application electromagnetic launch was invented for, and every
constraint that dominates the flagship design either relaxes or disappears there.

This is not a new idea, and the document is worthless if it pretends otherwise. Gerard K.
O'Neill proposed lunar mass drivers at Princeton in the 1970s. Mass Driver I, II and III were
built and tested with Henry Kolm at MIT, and the 1977 NASA Ames summer study worked the mining
architecture in detail. VOLLEY's possible contribution is the implementation, not the
concept: an ironless double-sided Halbach machine with programmable per-shot velocity and a
reusable sled, which fifty-year-old mass drivers did not have. Claiming novelty here would repeat
exactly the error P22 records in the flagship.

---

## Why the Moon inverts the problem

| | Earth | Moon |
|---|---|---|
| Escape velocity | 11 200 m/s | 2376 m/s |
| Atmosphere | drag, heating, a release port to punch through | none |
| Payload | a delicate satellite, 25 g limit | ore, thousands of g |

The g-limit that governs the entire flagship design is a property of the payload. Regolith in a
canister does not care.

| Destination | 100 g | 1000 g | 5000 g |
|---|---|---|---|
| Lunar orbit, 1634 m/s | 1360 m | 136 m | 27 m |
| Lunar escape, 2376 m/s | 2878 m | 288 m | 58 m |

The number that makes the case: 1.33 MJ per kg to lunar orbit.

| Throughput | Average power | At 50 % efficiency |
|---|---|---|
| 1 tonne/day | 15.4 kW | 31 kW |
| 10 tonne/day | 154 kW | 309 kW |

A tonne a day off the Moon on a modest solar array. That is the entire economic argument for
mining lunar material rather than lifting it from Earth, and it has been the argument since 1977.

---

## Where SpinLaunch fits, and it is not where it first appears

SpinLaunch's hardest problem on Earth is the release port: getting a payload out of a vacuum
chamber into atmosphere at Mach 6 without destroying the chamber. On the Moon that problem does
not exist. The vacuum is free and there is nothing to punch through.

But the reason to combine the two is energy storage, and it answers the flagship's worst
open defect at scale:

| | Stores 1.33 MJ as | Pulse power needed |
|---|---|---|
| Supercapacitor bank | charge | 460x the flagship bank, which already fails (P26) |
| Spinning mass | rotation | none: spin up over hours, release in milliseconds |

A centrifuge stores bulk kinetic energy directly and spins up on a small continuous motor. It
sidesteps the pulse-power chain entirely, which is the single hardest unsolved problem in the
current design.

So the division of labour is: centrifuge for bulk velocity, linear motor for precision.

| | Good at | Bad at |
|---|---|---|
| Centrifuge | storing and delivering bulk energy cheaply | release timing, and therefore aim |
| Linear motor | programmable velocity to 0.027 m/s | bulk energy, per P26 |

Each covers the other's weakness. A 100 m arm reaching lunar orbit velocity imposes 2720 g on the
payload, which is fine for ore; a short electromagnetic section then trims the final few percent
and aims it. Precision is what the flagship has already demonstrated, and it is precisely what
a centrifuge alone cannot do.

---

## The catcher

A platform in lunar orbit catches the incoming canister, then fires it toward Earth. Trans-Earth
injection from low lunar orbit is about 1000 m/s: 51 m of track at 1000 g, or 510 m at 100 g.

The elegant part is momentum. Catching adds momentum, throwing removes it. With the geometry
chosen well the station approaches momentum-neutral and needs little propellant to hold its
orbit. That is O'Neill's mass catcher, and it is why the architecture closes instead of slowly
deorbiting itself.

---

> ## Re-examined 2026-08-20: not revivable, and it got there first
>
> The stop holds and is structural. This entry has no host, its payload is ore, and the
> g-limit that governs the whole flagship disappears, *it describes a different programme, and no
> analysis or source changes that.* Do not open it.
>
> But its bank objection died anyway. The *"460x the flagship bank, which already fails"* row
> above was aimed at a capacitor bank that
> [ADR-032](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/032-gen6-stage-integrated-gas-store.md)
> deleted and [A64](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/A64_pulse_store_technology.md)
> re-priced. Three vault entries were resting on that same objection. It is worth knowing it is
> gone even where the entry stays shut.
>
> ### The part worth keeping is the sentence in the middle
>
> > *"The division of labour is: centrifuge for bulk velocity, linear motor for precision."*
>
> [ADR-033](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/docs/adr/033-gen6-trim-stage.md)
> adopted that exact principle on 2026-08-16, sixteen days after this file was written, with a
> different bulk store: *"Gas supplies the energy. The motor supplies the control."*
>
> Two unrelated bulk stores, a centrifuge and a gas charge, and the same conclusion: a linear
> machine is a mediocre energy store and an excellent servo. *That is stronger evidence for the
> principle than either document makes on its own*, and it is why this entry stays in the vault
> rather than being deleted. The idea outlived the architecture it was written for.

## The three hard problems, named next to the numbers

1. Catching an unpowered projectile in orbit is harder than launching one. Arrival
   dispersion, closing-rate control, capture mechanics, and what happens on a miss. The launcher
   is the easy half of this architecture.
2. Sled recovery. The sled must be arrested and returned every shot. On Earth the flagship's
   brake dissipates 1291 J; on the Moon at 1634 m/s it is megajoules per shot, continuously,
   with no atmosphere to reject heat into.
3. Regolith abrasion on a precision airgap. The flagship holds a 0.05 mm shim tolerance
   across a 12 mm gap. Lunar dust is electrostatically charged, sharp, and gets into everything.
   This may be the item that decides the architecture.

---

## The deliverable

A scaling study, not a design. How the flagship model extrapolates to lunar gravity, ore
payloads and thousand-g operation: where the linear-motor terms still hold, and where they break.

The most useful single output would be the crossover point: at what throughput does a lunar
mass driver beat lifting the same mass from Earth, given launch costs and the capital mass that
has to be delivered to build it. That number decides whether any of this is worth anything, and
it is computable from what already exists.

> This is the furthest thing from the thesis in the entire programme. It sits here because
> the physics is worth recording, not because it should be worked on. The flagship has three
> crossed kill criteria and no measured number; those come first.
