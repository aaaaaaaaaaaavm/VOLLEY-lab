# Higher-speed design constraints

**HV-ACR1-REJECTION-SCREEN-01 ·26 October 2026.** The unchanged source/geometry was actually run at requested 10, 15, 30, 50 and 100 m/s. All 22 target/inductance/adverse/timestep cases fail the original accepted gates. Current modeled command points remain 1, 2 and 3 m/s. No higher achieved or hardware-rated operating point is established.

## What was executed

Unchanged coupled_shot.py was imported from a private byte-identical capture. Its finite magnetic/brake maps, computed phase resistance, CAD mass and all source/inverter/current/voltage/arrest checks were preserved. The runner calls the existing function with new target arguments only: all five targets at 20 µH/20 µs, nominal and adverse; 10/15 m/s at 3/100 µH; and four decisive 10/15 m/s nominal/adverse 20 µH refinements at 5 µs. Twenty-two cases took a single CPU process; no finite-field map, accepted source output or geometry was regenerated. Exact accepted copies and pins accompany this packet.

| Target | Condition |5 µs release (m/s)|Speed at >1.511 m abort (m/s)|Draw until abort (J)|
|---:|---|---:|---:|---:|
|10|nominal|9.683448|8.492971|2274.991|
|10|adverse|7.615979|6.198837|1812.642|
|15|nominal|9.866017|8.700224|2582.359|
|15|adverse|7.615926|6.198748|1812.589|

Every listed case is **ARREST_STROKE_EXCEEDED**, with release-speed failure as well. The physical arrest end is 1.510 m; the inherited numerical abort guard is 1.511 m. The reported nonzero speed is at that abort, not a completed stop. Requested 30/50/100 m/s trajectories saturate toward roughly the same current/source-limited release regime; their requested value is not their achieved release speed. Individual failed gates, including adverse modulation and some 100 µH current overshoot, remain in MODEL_CASES and full case JSON.

## Why the current device rejects these requests

The accelerated assembly is **17.127805767 kg=13.127805767 kg retained sled/pallet+4 kg payload**. The finite retained-host reduced masses are 16.711428033 kg during acceleration and 12.881802439 kg during arrest. Momentum and energy accounting use those masses; fixed-lab kinetic energies are also tabulated separately.

Integrating the actual current brake map across 210 mm gives 0.236268830 J per peak phase ampere. Even an instantaneous, loss-free, constant 600 A brake supplies at most **141.761 J** of relative work, corresponding to an optimistic **4.691 m/s** ceiling. That is a necessary bound, not an achievable rating. At 10 m/s the sled alone requires 644.09 J relative arrest work and 3067.1 N mean force. The field-map work bound would require 2726 A before current ramp/source/regeneration constraints. Longer acceleration alone cannot fix the retained 210 mm arrest region.

The same 600 A idealized drive-work bound reaches only 11.427 m/s within 1.3 m, ignoring all losses and source voltage. Nominal energy usable between 86.4 V and the 60 V stop gate is 12078.0 J; the adverse capacitance case gives 7609.1 J. The initial positive source-power budgets are 8482.9/4241.5 W and decrease with bank voltage. Those are distinct from stored energy. A no-ESR/no-load q-voltage bound is 47.39 V; 100 m/s back-EMF alone requires about 93.30 V before resistance/inductance/control margin. Current ratings and voltage cannot be relaxed to make a case pass.

CONSTRAINTS includes launch/arrest energy, acceleration/load, mean force, phase-current work bounds, source voltage/power, transient/final host recoil and angular impulse for a declared 0.1 m offset. Counter-torque, actual mounting offset/inertia and source thermal/contact/actuator limits still require a selected new configuration. Draw-until-abort is not a complete-shot efficiency or a full brake-heat measurement.

## Next design targets

1. **10 m/s first:**a separately identified design with adequate drive voltage/current/power and a much longer or different arrest system. Even an unrealistically constant best-case 600 A force needs at least 0.995 m drive and 0.767 m arrest. Add margin, mass and finite-field/end/custody/source/thermal analyses; these are lower bounds, not a proposed accepted layout.
2. **15 m/s second:**its ideal lower bounds rise to 2.239 m drive/1.726 m arrest. It needs a new power/controller/mechanism and coupled re-evaluation. Qualifying 10 m/s would not automatically qualify 15 m/s.
3. **30 m/s and above later:**quadratic launch/arrest energy and load growth changes the architecture.50/100 m/s launch kinetic work alone exceeds the present usable bank boundary before losses; 100 m/s also exceeds its ideal back-EMF voltage headroom. Do not transfer the historical 16.029 m/s periodic result or induction-launch simulation into a current rating.

HYP-L2 m, HYP-L5 m andHYP-L10 m are explicitly **different hypothetical revisions**, shown only as static requirement arithmetic. The unchanged local k(x) does not validate a longer winding, commutation, end coverage, inductance, added structural mass, cooling or arrest system. No long-rail source simulation or linear-force extrapolation is claimed validated.

## Published experiments: what can support model applicability

The actual existing 20-page [Zhao et al. (2022)](https://doi.org/10.3390/rs14174205) publisher PDF was hash-verified, and selected topology/model, field/force and release passages were reread(pp 3–14, 17–18). Its measured gap-center field is about 0.424 T in the ejection unit; field-position curves and force-current/coil-position tests are genuine benchmark observables. The counterweighted 1 kg/3 kg tests reach 0.67–1.42/0.40–0.85 m/s at 0.5–2.5 A. Derived payload kinetic-energy ranges are 0.22445–1.0082 J and 0.24–1.08375 J. These are measured data ranges under the source's conditions, not ACR1 measurements.

Those experiments can substantiate a reconstruction of the **published** force/field/work-energy model at its own geometry and currents. They do not physically validate VOLLEY or directly substantiate 10/15/30/50/100 m/s. Its yoked, double-magnetic-circuit voice coil differs from the finite air-core Halbach topology: ACR1 has six blocks per 48 mm magnetic period and 42 blocks per side, with 12 mm magnet-face spacing in the field model. That magnetic gap is not a mechanical running-clearance rating. Gap, turns/material properties, current density, armature reaction, contact/friction and speed must be matched or bounded. The authors explicitly note increasing high-current force overprediction from omitted armature reaction, and release differences below 11% from their model under their tests. That 11% is neither a measured dispersion nor an ACR1 uncertainty allowance. No digitized-curve fit or quantitative external-model reproduction was performed here.

EXPERIMENTAL_BENCHMARK_CARDS identifies measured field/force/release observables and the exact next reconstruction/uncertainty steps. The 2025 gravity-assisted transport experiments are a separate contact/custody benchmark. Feng's 230–321 m/s induction-launch results are simulation; Yamaguchi's relevant end-effect work is 2 D theory with hardware future work; the closed voice-coil paper remains metadata-only. None is relabeled measured support for this rail. No new paywall bypass, provider contact or invented full-text reading occurred.

## Numerical checks and reproducibility

Four 20→5 µs pairs retain the same rejection. Maximum release-speed change is 0.00052502 m/s; abort-position change 0.054339 mm. Independent reduced-mass kinetic-energy plus friction agrees with signed motor work to 1.09 e-11 J. Original declared total-energy checks are retained; failed physical/design gates are not overridden by numerical convergence.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 run_screen.py
python3 analyze_screen.py
python3 check_capture.py
```

The field map and accepted original outputs are inputs, not rerun scripts. finite_motor.py is captured unchanged for provenance. The runner changes only arguments and output location. The higher-target trajectories and changed-configuration sensitivities are separately identified research results. New 10–15 m/s operating claims require the separately designed coupled configuration, appropriate model benchmarks, convergence, uncertainty and targeted physical measurements. External experiments can support applicable equations; VOLLEY-specific experimental validation still requires relevant article measurements.

## Separate Gen 6/Labs trade: attached flyaway launch shoe

A shoe that remains attached to a modified CubeSat can remove the successful-departure sled-arrest/return requirement. It creates a different payload interface and outbound mass. The 0.25/0.5/1 kg shoe values below are unsubstantiated sensitivity assumptions, not feasible designs or achieved adapter masses. No current k(x), current waveform or force map is transferred to the redesigned magnetic/guide structure.

At the same ideal fixed-lab launch work, the moving-mass-only speed ratio is sqrt[(13.127805767+4)/(4+m_shoe)]. This relation omits changes in field, source, friction, geometry, finite-host mass and losses. It is not a predicted achieved release speed.

| Hypothetical shoe | Outbound payload+shoe | Same-work ideal mass-only ratio | Twelve adapters | Successful-departure arrest |
|---:|---:|---:|---:|---|
|0.250000 kg|4.250000 kg|2.007504×|3.000000 kg|No retained sled to arrest|
|0.500000 kg|4.500000 kg|1.950943×|6.000000 kg|No retained sled to arrest|
|1.000000 kg|5.000000 kg|1.850827×|12.000000 kg|No retained sled to arrest|
|13.127806 kg|17.127806 kg|1.000000×|157.533669 kg|No retained sled to arrest|

The full-sled flyaway row keeps the same 17.127806 kg moving assembly and a 1× ideal ratio: removing arrest supplies no launch-energy mass saving. It also needs twelve full launch members, versus one reusable 13.127806 kg sled today. The lightweight-shoe rows require twelve attached adapters; their inventory is 3/6/12 kg, but this limited comparison says nothing about complete installed-device mass or actual magnetic hardware feasibility. No adapter is assumed discarded as free debris.

The frozen CAD BOM provides a decisive compatibility check: 84 moving magnet blocks already total 3.6288 kg under the current density/geometry model. The assumed 0.25/0.5/1 kg shoes cannot retain that magnet set, even before guide, structure and positive attachment mass. Those small sensitivities therefore require a materially redesigned electromagnetic geometry/topology; they are not achievable mass estimates for a trimmed current carrier. Six blocks describes one magnetic period, not the entire current array.

Removing arrest does not convert any rejected current-model trajectory into a qualified flyaway design. The current ten-metre-per-second cases already miss their requested speed before the arrest failure; changing release/custody and exit dynamics requires a new model. A flyaway configuration also carries the adapter's momentum away, changes host recoil and per-release mass history, and changes payload magnetic exposure, centre of gravity, structural attachment and later attitude/mission behavior.

Next gates are: define the actual minimum field/guide/interface assembly and substantiate its mass; retain the shoe positively on the payload; develop storage/transfer/rail-exit/partial-launch containment; calculate its new finite magnetic field and current/source/thermal response; propagate all twelve adapter inventories and recoils; and establish payload structural, magnetic, contamination and mission acceptance. A lighter shoe is a reasonable next architecture study, not a demonstration that a 0.25–1 kg launcher adapter is achievable.
