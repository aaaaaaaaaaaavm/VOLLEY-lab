# VLAB-X001, my frozen quadrant-bearing mechanism screen

**State: FROZEN, NOT RUN.**  
**Controlled input:** [`parameters.json`](parameters.json)  
**Executable model:** deliberately absent from this declaration commit.

## The mechanism I am actually testing

I am not wrapping a gas bearing around a CubeSat in VOLLEY. The existing Gen6 pressure piston and
carriage already depart with the payload, so I put two bearing lands on that piston assembly. Each
land has four circumferential pockets fed through independent restrictions from the drive gas.

BOLLEY is different by design. Its 100 mm spacecraft body already accepts a cooperative interface,
so I put two four-face bearing collars around that body. The pressure supply, moving area, gas
allowance and clearance belong to BOLLEY rather than being copied from VOLLEY.

In both targets, a body displacement closes the film on one side. That side must rise in pressure
and push the body back toward the local guide centreline. Two axial stations provide both lateral
force and pitch/yaw authority. No active sensor or commanded valve is allowed in this first screen.

## Equations I freeze

For each pocket I solve one quasi-steady mass balance at every dynamics evaluation:

1. compressible isentropic flow through a circular inlet restriction, including the choked branch;
2. isothermal laminar flow from the pocket through two opposed rectangular film exits;
3. pocket force from absolute pocket pressure minus the declared ambient pressure;
4. a rigid body's two lateral translations and two small-angle rotations;
5. each target's own one-dimensional axial law, used once without the bearing and once with it.

The rectangular-film relation is a reduced-order parallel-plate Reynolds/Poiseuille model. It is
not CFD, a seal design or a manufactured restrictor. I report the mean free path and Knudsen number
at the pocket and at the outlet boundary because the continuum approximation must not be hidden
where the film vents toward vacuum.

VOLLEY uses its closed adiabatic chamber law and its published 83.4037 N friction allowance for the
baseline reproduction. Bearing bleed removes mass from that chamber. BOLLEY uses A11's constant
mean-pressure model and counts bearing flow on top of A11's complete worst-corner gas allowance.
That difference is part of the target boundary, not a solver option.

## Geometry and corners I freeze

| Quantity | VOLLEY | BOLLEY |
|---|---:|---:|
| Moving reference mass | 4.000 kg | 4.000 and 6.000 kg |
| Stroke | 8.000 m | 0.900 m |
| Bearing layout | 2 round lands × 4 quadrants | 2 square collars × 4 faces |
| Station separation | 120 mm | 220 mm |
| Nominal radial/face clearance | 50 µm | 100 µm |
| Pocket loaded area | 70% of a quadrant × 10 mm | 60 × 80 mm per face |
| Restrictor diameter | 50 µm | 500 µm |
| Guide-centreline envelope | 0.2425 and 0.9052 mm | 0.05 and 0.50 mm declared screen |
| Transverse CG envelope | ±5 mm | ±20 mm |

The VOLLEY bow values are the A69 solved orbital envelope. The BOLLEY bow values are declared lab
screen inputs because BOLLEY has no guide metrology result. Passing them would not convert them
into tolerances.

The response map evaluates signed offsets at 10%, 20%, 30% and 40% of nominal clearance in both
lateral axes. Dynamic cases cross both bow amplitudes, both bow phases, both signs of the maximum
CG offset and both signs of the declared axial-force eccentricity. The three single-fault runs are:

- one inlet effectively stuck open, pocket pressure driven to its supply boundary;
- one inlet stuck closed, with that pocket at the ambient boundary;
- one inlet area biased 10% high.

I will label each fault `SAFE`, `DEGRADED` or `REJECTED` from the same contact, flow, acceleration
and exit-rate limits. The frozen gate requires an explicit label; it does not require a failed
single fault to be safe.

## The ten bands I will run unchanged

| Band | Pass condition | Meaning of failure |
|---|---|---|
| 1 | Net force opposes every non-zero signed offset in the response map | The pressure network is not restoring |
| 2 | Every nominal corner completes without film closure and the centred solution is locally stable | The bearing does not replace contact across the declared envelope |
| 3 | Every solved pocket remains between ambient and supply absolute pressure | The calculation requires suction or creates pressure |
| 4 | Baseline gas plus bearing flow is no more than 110% of each target's current allowance | Centring hides an unbounded gas system |
| 5 | Bearing-on exit velocity differs from the same-model bearing-off result by no more than 0.5% | Lateral control changes the mission result |
| 6 | Peak longitudinal acceleration remains at or below 25 g for VOLLEY and 8 g for BOLLEY | The mechanism violates an unchanged payload load limit |
| 7 | Pitch, yaw and roll exit rates are each no more than 2 deg/s | The guide still fails the common tip-off limit |
| 8 | Stuck-open, stuck-closed and +10% inlet-bias cases each receive a traceable disposition | A single-channel fault disappears from the claim |
| 9 | Pocket and outlet Knudsen numbers are reported for every target/temperature corner | Continuum validity is being assumed rather than checked |
| 10 | Plume, contamination and electrostatic charging remain explicitly outside the result | A mechanism screen is being presented as qualification |

Bands 1–10 are the same mechanism gate already declared in the root entry; this sheet makes the
geometry and numerical interpretation exact before an executable model exists.

## Reproduction and convergence checks

These checks do not replace the ten mechanism bands:

- bearing-off VOLLEY exit velocity must reproduce 29.01 m/s within 1%;
- bearing-off BOLLEY exits must reproduce 11.55 and 9.75 m/s within 1%;
- halving the maximum axial integration step changes exit speed and each exit angular rate by no
  more than 1%;
- pocket-pressure roots must close inlet/outlet mass balance to relative residual at most 1e-8;
- every evaluated corner and fault record must be retained in the result artifact.

## What a pass would mean

A pass would mean the reduced mechanism deserves target-specific CFD, tolerancing, plumbing and
CAD. It would not validate a bearing, a seal, a restrictor, a contamination environment or a
release mechanism. A fail stays here with its controlling number.
