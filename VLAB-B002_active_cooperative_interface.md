# VLAB-B002: active cooperative spacecraft interface

**State:** OPEN QUESTION. No executable model or result exists here.

## Why I opened it

BOLLEY's controlled baseline keeps all spacecraft-side deployment hardware passive under
BOL-R-007. That rule keeps the spacecraft concession small, but it also forces field generation,
sensing, switching and stored shot energy onto the launcher. BOLLEY P41 already asks whether I
removed the mover while keeping the more expensive pulse problem.

I therefore reopen one assumption only: the spacecraft may participate electrically during
release. The controlled BOLLEY requirement does not change unless this branch later earns a
BOLLEY ADR.

## What I am allowed to change

I may place sensing, switching, conductors, coils or a small local energy store on the spacecraft.
I may let the spacecraft exchange state information with the launcher before release. I may keep
hardware after release only if I name the orbital function it performs.

I do not waive ascent retention, debris containment, magnetic compatibility, tip-off, provider
acceptance or evidence provenance.

## What I may borrow

- BOLLEY's exact 4 kg reference and 6 kg qualification cases as comparison cases;
- the selected Fluxrelay force duty and four-channel force-centroid method as a control;
- the current 0.37136 kg passive-interface mass as a comparison, not a credit;
- the current 900 J shot-energy requirement as the controlled electrical benchmark;
- the 2 deg/s per-axis tip-off requirement.

I do not inherit any force, mass, efficiency or thermal result after changing the spacecraft
hardware.

## First gate before any executable model

The first model may start only after I select one explicit spacecraft electrical architecture and
write down every added part. It must compare against the controlled Fluxrelay point on the same
system boundary and report:

1. spacecraft-side added mass and launcher-side deleted mass separately;
2. total installed system mass, including source, switching, harness, cooling and containment;
3. spacecraft energy used during deployment and the post-release function, if any, of each retained
   active part;
4. the 4 kg reference and 6 kg qualification departure states under the unchanged acceleration and
   tip-off limits;
5. magnetic field at the payload boundary in both powered and unpowered states;
6. the single-fault consequence of losing spacecraft power, communications, one switch or one
   active channel before release;
7. whether the architecture still needs the launcher shot-time pulse that controls P41;
8. which current BOLLEY part or requirement the active interface actually deletes.

The branch stops if it adds spacecraft power and software while deleting no controlling BOLLEY
problem. A lower coil loss alone is not enough.

## Promotion condition

A passing screen may open a target-specific BOLLEY run sheet. It does not modify BOL-R-007 by
itself. The controlled passive design remains the comparison until an ADR changes that requirement.
