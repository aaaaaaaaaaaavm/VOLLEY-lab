# VLAB-X002: deployer-owned passive trim secondary

**State:** DECLARED, NOT RUN.

## Why I opened it

VOLLEY Gen6 may retain a short electromagnetic muzzle section to recover commanded velocity. A
permanent-magnet mover brings magnetic cleanliness, cradle alignment and tube-field interaction
back into an architecture that deleted the full motor. BOLLEY has already taken a wide passive
magnetic-matrix/copper-ladder secondary through field, circuit and nominal CAD closure.

I ask whether a launcher-owned wide plate or symmetric twin-fin shuttle can use that principle for
VOLLEY's trim duty while the spacecraft remains untouched.

This is not another attempt to drive on the CubeSat's CDS rails. PII-16's measured transverse edge
factor of 0.0253 rejects that geometry. The secondary must be deliberately wide.

## What may transfer

- Fluxrelay's material roles: copper ladder for induced current, magnetic matrix for the local flux
  path;
- the symmetric multi-lane principle that avoids a single off-axis fin;
- BOLLEY's winding-window, saturation and exact-overlap checks;
- VOLLEY's current trim authority, stroke, bore and velocity-dispersion requirements.

BOLLEY's 1.2231 m primary result, 380 A point, 0.37136 kg spacecraft interface and field values do
not transfer to a short VOLLEY muzzle.

## Frozen first gate

The first model must:

1. provide VOLLEY's full declared positive and negative trim authority at the current Gen6 exit
   speed;
2. fit the current bore and tube without using the rejected standard corner rails;
3. keep the payload mechanically and electrically unmodified;
4. contain no permanent magnet on the moving member;
5. place the resultant trim force through the declared payload/carriage CG envelope or close the
   resulting tip-off below 2 deg/s per axis;
6. include end effect, slip loss, stationary copper loss, secondary heating and tube interaction;
7. remain below the installed mass of the suspended permanent-magnet trim implementation on the
   same boundary;
8. preserve the current pulse-store feasibility margin rather than citing BOLLEY's different
   source;
9. stop if its wide secondary recreates a carriage whose arrest, retention or return dominates the
   mass it removes.

Passing opens a VOLLEY trim architecture gate. It does not alter BOLLEY and does not revive the
original PII-19 entry wholesale.
