# VLAB-B001: BOLLEY without inherited interface constraints

**State:** OPEN QUESTION. No model, CAD or result exists here.

## The boundary I remove

BOLLEY began by relaxing one VOLLEY requirement: the spacecraft may carry a passive reaction
interface. I now ask what the architecture becomes if I stop inheriting the rest of the dispenser
before I know that I need it.

The question is:

> How much programmable orbital-placement authority becomes possible when I design the spacecraft,
> its deployment interface and the spent upper stage as one temporary machine?

This does not waive physics or flight safety. It makes the following design choices variables:

- payload class and external geometry;
- passive versus powered spacecraft hardware;
- 0.40 kg gross interface limit;
- 0.90 m powered stroke;
- purely axial release;
- one-payload-at-a-time sequencing;
- nitrogen as the working fluid;
- a dispenser independent of the stage structure.

## The architecture worth screening

I make the spacecraft's outer frame perform several duties at once:

- primary bus structure and deployment load path;
- full-face pressure piston and replaceable labyrinth seal land;
- wide passive electromagnetic secondary;
- thermal spreader and electrical ground plane;
- launch guide and wear surface;
- optional passive eddy-current damper after release.

The host carries a long low-pressure tube, four independently metered plenums, external position
sensing and a short four-face trim stator. Gas supplies the bulk impulse. Differential pressure
centres and steers. Electromagnetics shape the exit condition. The stage engine, where the provider
permits, supplies only coarse orbital repositioning.

## Entry gate, declared before a model

The first executable screen must:

1. select one real bus envelope and one explicit host tube envelope;
2. publish a before/after parts ledger and grant no multifunctional mass credit without naming the
   removed part;
3. close a full system mass boundary including structure, gas store, valves, sensing, harness and
   electronics;
4. retain an explicit 4 kg reference and 6 kg qualification case or record why a new payload class
   replaces them;
5. compute axial velocity, lateral velocity, tip-off and host impulse together;
6. count every shared element whose failure forfeits the remaining manifest;
7. compare against current VOLLEY Gen6 and BOLLEY Fluxpiston on identical mission and host
   boundaries;
8. stop if the cooperative bus adds functions but deletes no controlling requirement.

Passing opens a generation proposal in BOLLEY. It does not itself create one.
