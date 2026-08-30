# VLAB-B003: distributed Fluxpiston feed

**State:** OPEN QUESTION. No executable model or result exists here.

## Why I opened it

BOLLEY A11 showed that a deliberately leaking full-face pressure interface is not killed by first-order gas use across its declared clearance and temperature grid. That result does not answer how pressure is held while the chamber volume grows, how lateral pressure imbalance behaves or whether one feed location produces a useful force distribution.

The controlled Fluxpiston concept therefore has a known next question: should one source feed one chamber, or should the pressure interface be divided axially or by face so gas delivery and centring can be controlled where they are needed?

This branch changes the feed topology. It does not change the controlled BOLLEY requirements.

## Candidate families

The first screen may compare:

- one source with several axial injection stations;
- several small local accumulators charged before release;
- four face or quadrant plenums with independent metering;
- a staged chamber in which upstream volume opens only after a declared position;
- a hybrid in which one path supplies axial impulse and separate low-flow paths supply centring.

These are families, not five designs. I will not draw all five before the model identifies which
question is worth CAD.

## What I may borrow

- A11's exact reference and qualification payload cases;
- A11's declared clearance and temperature grid;
- A11's gas-use result as a comparison only;
- the unchanged BOL-R-004 acceleration limit;
- the unchanged BOL-R-005 tip-off limit;
- BOL-R-013 as the controlled exit-dispersion requirement;
- VLAB-X001's idea that pressure imbalance may be useful for centring, without importing a bearing
  stiffness or flow result.

No valve coefficient, plenum pressure, accumulator mass, pressure uniformity or control bandwidth is inherited.

## First gate before any executable model

The first executable model must use one common source model for all candidate topologies and report:

1. chamber pressure versus position and time for the 4 kg reference and 6 kg qualification cases;
2. axial exit velocity and peak longitudinal acceleration;
3. total gas used per shot and over the declared campaign;
4. source pressure, regulator duty, valve flow area and accumulator inventory where present;
5. pressure imbalance across faces or quadrants and the resulting lateral force and moment;
6. the effect of one stuck-open path, one stuck-closed path and one biased pressure sensor;
7. whether any candidate reduces the pressure-control burden without increasing stored-system mass
   or failure concentration on the same boundary;
8. whether the candidate can hand centring authority to VLAB-X001 without changing axial departure
   outside the controlled mission requirement.

The first gate stops the family if distributed hardware only reproduces one lumped chamber with
more valves and more single-point failures. It also stops any candidate that needs an unbounded
pressure reservoir or hides gas outside the mass ledger.

## Promotion condition

A candidate may open a BOLLEY-specific run sheet only after the source, valve and gas inventory are
closed on the same boundary as the controlled Fluxpiston comparison. A pass here would not close
seal contact, contamination, plume, rear-panel load or provider integration.
