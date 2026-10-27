# VLAB-X003: independent motor-charged release-cell bank

**State:** WITHDRAWN FROM VOLLEY REFERENCE, RETAINED AS A LAB COMPARATOR (2026-09-28).

This is the multiple-launcher arrangement formerly presented as the next VOLLEY generation. Each payload occupied a separate retained cell. A motor charged that cell's mechanical accumulator before its latch released a guided pusher; a local catcher retained the moving hardware. The configuration was a calculation and CAD study. No cell, feeder, or release was built or tested.

## Why it was withdrawn

The arrangement isolates a jam in one mechanical cell, but it duplicates retention, charging, release, support, and catcher hardware. An emptied cell continues to occupy installed mass and volume. Shared command, electrical power, host navigation, and integration can still fail together. The study did not demonstrate that this redundancy justified its installed burden over a common loading path. It also did not meet VOLLEY's controlling objective: one reusable launch path that receives ordinary CubeSats sequentially and commands a different release speed for each shot.

The sampled 4.569852 m/s result was a bounded **two-payload** mission calculation, not a speed limit or proof of the launcher. All six sampled **twelve-payload** finite-burn mission cases failed complete delivery under their stated assumptions. The study cannot establish a broad 1–100+ m/s range, payload qualification, provider compatibility, or full-manifest benefit.

## What the lab keeps

- The independent mechanical path as a fault-isolation comparator, including how many payloads a blocked cell, small bank, or shared path would strand.
- The motor-charged accumulator, latch, guided pusher, and catcher as component hypotheses, with spring form and installed masses still unknown.
- The model inputs, failure results, and CAD snapshots as dated evidence at their original VOLLEY commit; the original calculation files and history remain in [the source record at `52429ce`](https://github.com/aaaaaaaaaaaavm/VOLLEY/tree/52429ce94).
- The [withdrawn architecture calculation](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/52429ce94/docs/GEN6_REFERENCE_ARCHITECTURE.md) and [cell mechanics study](https://github.com/aaaaaaaaaaaavm/VOLLEY/blob/52429ce94/docs/REFERENCE_CELL_MECHANICS.md), read with their original assumptions. These links preserve the prior version; they do not make it current.

## Reopening gate

Reconsider a bank only after a matched shared-path comparison at the same 1/4/12-payload missions. Account for complete installed mass, occupied and spent volume, payload retention, host reinforcement, power, thermal control, harness, operations, jam recovery, and common-mode failures. Measure release repeatability, clearance, cycle life, and payload contact on representative hardware. Define the payload-specific load and speed envelope before claiming compatibility. A favourable low-speed point or one isolated jam case alone is insufficient.

**Disposition:** lab study only. Any future VOLLEY selection requires a new dated decision and evidence; this entry does not select a propulsion or release mechanism.
