# VLAB-X005: Segmented stator energization hypothesis

**Disposition: unselected electrical architecture hypothesis.** The Gen5 finite-force review changed the motor question. A finite 3-D analytic stator integral gives 1,041.7 J ideal work, while a separate 2-D finite-element field solve gives 1,081.6 J on its finest mesh. Both show the force declining near the end of the drawn stator. The 2-D solve omits magnet-depth end effects; neither result is measured thrust.

A subsequent independent numerical surface-charge integration over the full magnet depth and 162 stator belts reproduces **1,041.7 J ideal work** under the same geometry, remanence and ideal-phase assumptions. Illustrative gap cases give **906.7 J at 14 mm** and **789.9 J at 16 mm**, versus the 12 mm nominal face gap. This exposes a clearance-versus-force trade for any segmented winding. The cases are not measured tolerances; the local architecture question remains a selected coil, switch and installed-mass design with actual clearance control.

The conditional bank/trajectory model retained a 96 V, 6 F, 12 mΩ source, 95% converter, 200 W auxiliary load, ideal phase and a prescribed 126 kA/m sheet current. It compared two *assumed copper lengths*, not two designed winding and switch sets:

| Assumed energized copper | Gross capacitor draw | Copper heat | Computed ideal-phase exit speed |
|:--|--:|--:|--:|
| Entire 1.30 m winding | 2,098.6 J | 927.3 J | 12.448 m/s |
| Hypothetical 0.34 m active length | 1,394.4 J | 242.5 J | 12.448 m/s |

The apparent 704 J gross saving is a **conditional model difference**. Both branches impose the same force rather than solving voltage-limited current rise and commutation. The short-copper case has no selected coil segmentation, bus, gate driver, switch, thermal path or mass ledger. It is therefore a reason to study segmented energization, not an electrical efficiency claim for a product. The earlier 16.029 m/s periodic shot and 2.782 kJ gross draw remain historical model outputs.

![Conditional finite-force bank histories imported from the Gen5 study](figures/gen5_finite_coupled_shot.png)

*Software-generated model history; no hardware test. The source run and its assumptions are recorded in the [Gen5 P120 validation sheet](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/main/validation/P120_gen5_finite_coupled_shot.md). The numbers and their limits are stated here so this hypothesis can be reviewed on its own.*

## Reopening gate

1. Define a winding and switch topology with physical conductor fill, end turns, hot resistance, inductance and insulation.
2. Solve position-dependent force with commanded current, voltage limits, switching delay and thermal rise; retain the finite stator and end effects.
3. Include inverter, protection, harness, cooling and bank in installed mass and energy per shot for a full twelve-release duty cycle.
4. Compare to the unchanged Gen5 screen and spring/host alternatives on the same mission and payload boundary.
5. Require an independent 3-D field/force cross-check and, before a product claim, calibrated hardware tests.

This study has no passing promotion result. Any selected design needs a new configuration and decision record.
