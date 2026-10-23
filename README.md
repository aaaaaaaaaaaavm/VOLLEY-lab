# VOLLEY Labs

### Alternative mechanisms, design history and numerical experiments

VOLLEY Labs preserves the engineering alternatives behind commanded CubeSat deployment. The current academic feeder architecture is the **FM08-R3 guided lead-screw design**. This repository retains the other six candidates, earlier geometry revisions, their calculations and the reasons for the selection.

[Selected design](experiments/selected_feeder/README.md) · [Seven-concept trade](experiments/selected_feeder/verification/REPORT.md) · [Native CAD history](experiments/feeder_common_boundary/README.md) · [Mission studies](experiments/finite-burn-review/README.md)

![FM08-R3 four-cell guided lead-screw feeder rendered from native CAD](experiments/selected_feeder/cad/figures/FM08_assembly.png)

*Blender render of the selected academic geometry. Nominal motion, analytical screens and interlock checks are identified separately in the evidence package.*

## Feeder decision and retained alternatives

| Rank | Architecture | Weighted judgment / 10 | Disposition |
|---:|:--|---:|:--|
| 1 | Guided lead screw | 7.30 | Selected academic mechanical architecture; guided pusher, capped channel and defined receiver stops |
| 2 | Rack and pawl | 7.10 | Runner-up; useful where tooth/support design and backlash control improve installed packaging |
| 3 | Spring and two gates | 6.90 | Retained low-active-power alternative; requires adequate end force, governed transfer and reset |
| 4 | Belt shuttle | 6.70 | Retained packaging alternative; tension, compliance, retention and skipped engagement require evidence |
| 5 | Indexed drum | 6.40 | Retained common-port architecture; indexing/extraction and shared failure path require development |
| 6 | Telescopic | 6.05 | Retained compact-stowage concept; stage alignment, overlap and binding require redesign |
| 7 | Pantograph | 5.50 | Retained collapsible-storage research; linkage connection, near-flat loads and joint play require redesign |

Weights: safety 35%, packaging/mass 25%, positioning 20%, cycle/power 10%, manufacture 10%. These are declared engineering judgments. Alternative weighting and score sensitivity can change the ranking; none of the scores is a measured reliability.

[Current top-three comparison and source-based calculations](experiments/selected_feeder/verification/REPORT.md) · [Original seven four-cell CAD/STEP assemblies](experiments/feeder_common_boundary/README.md) · [Original concept rationale](docs/GEN6_FEEDER_CONCEPT_TRADE.md)

## Configuration boundaries

**Gen5** is the fixed evaluated twelve-3U electromagnetic study. **Gen6** contains the selected mixed 1U/3U feeder and separately versioned four/twelve-payload capacity studies. Earlier FM06/FM07 transfer, release, reset and rigid-contact cases retain their original configurations and numerical outcomes. A new selection does not revise those earlier results.

| Study | What is preserved |
|:--|:--|
| [FDR09 common-boundary concepts](experiments/feeder_common_boundary/README.md) | Native CAD/STEP, represented material, catalog options and geometry findings for all seven |
| [FM07 release/reset](experiments/feeder-release-review/README.md) | Earlier receiver-lock, exit-gate and prescribed reset geometry |
| [RVC01 rotary clearance](experiments/feeder_rotary_clearance/README.md) | Restricted FM07-R6 nominal gate-relief checks |
| [FCE13 contact diagnosis](experiments/feeder_contact_diagnosis/README.md) | Native solver logs and unresolved timestep/representation sensitivity; no accepted precision/load rating |
| [Finite-force campaign](experiments/finite-burn-review/README.md) | Matched host-assisted spring and imposed-release comparisons with native Orekit replay |
| [Current system assessment](experiments/system_feasibility_closure/README.md) | Four/twelve integration, declared resource accounting and feasibility sensitivities |
| [Lunar and high-speed bounds](experiments/extended_feasibility_bounds/README.md) | Reproducible conservation and incompatibility findings, with assumptions |

The independent spring-cell bank and long gas guide remain historical research alternatives. They do not define the selected feeder or the evaluated Gen5 configuration.

## Reproduction

Each captured package includes source, inputs, tool versions, raw results and a hash manifest. Native geometry uses FreeCAD and neutral STEP exchanges; technical renders are labeled. Run `python tools/prepublish_gate.py --all` for publication consistency and follow each package's own reproduction instructions.

No physical prototype, measured release performance, environmental qualification or provider approval is claimed. Catalog references and declared analytical screens support an academic design decision; hardware testing remains a separate development phase.

## Project editions

[Main engineering study](https://github.com/aaaaaaaaaaaavm/VOLLEY) · [College thesis and presentation](https://github.com/aaaaaaaaaaaavm/VOLLEY-thesis) · [IEEE-formatted manuscript](https://github.com/aaaaaaaaaaaavm/VOLLEY-paper)

Each edition includes its relevant evidence. Historical source and failed cases remain traceable through package manifests and Git history.
