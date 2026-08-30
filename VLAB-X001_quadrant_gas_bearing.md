# VLAB-X001: quadrant leakage bearing

**State:** FROZEN, NOT RUN.

## Why I opened it

BOLLEY A11 treats clearance leakage as a gas cost and leaves friction, contact, rarefied flow and
contamination open in P44. VOLLEY's eight-metre Gen6 bore has the complementary defect: contact-law
uncertainty dominates the guided-exit result, while tube bow and support placement define the
centreline.

Both architectures already spend gas beside a guided moving body. I ask whether I can meter that
flow through four independent face or quadrant plenums so offset creates a restoring pressure
field. The leak becomes an aerostatic bearing and a control input rather than only a loss.

The two geometries are intentionally not made identical. VOLLEY gets two four-quadrant lands on
its departing 15.805 mm piston/carriage. BOLLEY gets two four-face collars around its 100 mm
spacecraft body. My exact pre-run geometry, source values, equations, solver tolerances and fault
definitions are frozen in [`experiments/VLAB-X001/RUN_SHEET.md`](experiments/VLAB-X001/RUN_SHEET.md)
and [`experiments/VLAB-X001/parameters.json`](experiments/VLAB-X001/parameters.json). No executable
model or result existed when I froze those files.

## What may transfer

- BOLLEY's four-channel force-centroid allocation and declared CG envelope;
- BOLLEY A11's complete clearance/temperature grid as a comparison, not a bearing model;
- VOLLEY's corrected continuous tube centreline and eight-metre contact state;
- each programme's unchanged 2 deg/s/axis exit tip-off limit.

No seal coefficient, lateral stiffness, gas-use margin or tip-off result transfers.

## Frozen mechanism screen

Before target-specific CAD, one independent compressible-flow/rigid-body model must test:

1. restoring lateral force has the correct sign at every declared positive and negative offset;
2. the centred state remains stable across the declared CG and tube-bow envelope;
3. no face requires suction or negative absolute pressure;
4. total metered flow plus uncontrolled clearance leakage is no more than 110% of the target
   architecture's current gas allowance;
5. axial exit velocity changes by no more than 0.5% when centring is active;
6. pressure imbalance does not push either target above its unchanged longitudinal acceleration
   limit;
7. six-degree-of-freedom exit rate is no more than 2 deg/s per axis;
8. a stuck-open, stuck-closed and biased-pressure quadrant each produce an explicit safe, degraded
   or rejected disposition;
9. continuum validity is reported rather than assumed at the smallest clearance;
10. plume, contamination and electrostatic charging remain explicitly outside the model.

The 110% flow band prices a small centring allowance without letting the mechanism hide an
unbounded leak. The 0.5% axial band prevents lateral control from quietly changing the mission
result it is meant to protect.

## Transfer condition

A shared mechanism result is not enough. VOLLEY and BOLLEY each need a separate run at their own
pressure, stroke, geometry and gas inventory. A pass may open a target-specific ADR; a fail stays
here and neither flagship moves.
