# VOLLEY Labs

### Alternative mechanisms, design history and numerical experiments

VOLLEY Labs preserves the engineering alternatives behind commanded CubeSat deployment. The current integrated academic configuration is **VOLLEY-G5-ACR1**. Its guided lead-screw feed develops the selected **FM08-R3** architecture; the mixed-size FM08 subsystem remains a separate captured study. This repository retains the other six candidates, earlier geometry revisions, their calculations and the reasons for the selection.

[Current configuration boundary](docs/CURRENT_CONFIGURATION.md) · [Selected feeder lineage](experiments/selected_feeder/README.md) · [Seven-concept trade](experiments/selected_feeder/verification/REPORT.md) · [Native CAD history](experiments/feeder_common_boundary/README.md) · [Mission studies](experiments/finite-burn-review/README.md)

<p><a href="figures/acr1-polish/assembly_hero.png"><img src="figures/acr1-polish/assembly_hero.webp" alt="CAD-derived render of all 387 represented VOLLEY Gen5 ACR1 parts in the home pose; teal marks the selected feed and captive-pallet path." width="760"></a></p>

*CAD-derived Blender render · ACR1 home pose · all 387 represented objects present. Teal identifies the selected feed/pallet path; surface colours are display choices. [View provenance](figures/acr1-polish/POLISH_PROVENANCE.json).*

[Guided-feed close-up](figures/acr1-polish/feeder_detail_annotated.png) · [Four-state custody sequence](figures/acr1-polish/operating_sequence.png) · [Caption and visibility notes](figures/acr1-polish/CAPTIONS.md)


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

[Seven source-derived feeder concept cards](figures/feeder-concepts/README.md) · [Responsive comparison gallery](docs/feeder-concepts.html)

![Seven historical four-payload feeder concepts shown with a common orthographic view and physical scale](figures/feeder-concepts/seven_feeder_concepts.png)

*CAD-derived Blender comparison · preserved FDR09-R1 geometry. Selection and runner-up roles follow the later FDR10-R0 / D27-R2 trade; each card identifies its revision and reasoning.*

## Mechanism lineage and comparison evidence

<p><a href="experiments/selected_feeder/cad/figures/FM08_assembly.png"><img src="experiments/selected_feeder/cad/figures/FM08_assembly.png" alt="FM08-R3 mixed-size four-cell guided lead-screw feeder subsystem rendered from native CAD" width="600"></a></p>

*Historical/subsystem CAD-derived render · FM08-R3, two 1U and two 3U cells. This is the selected feeder architecture study; the current integrated ACR1 machine is shown above. [Source, revision and selection rationale](experiments/selected_feeder/verification/REPORT.md).*

<p><a href="experiments/feeder_common_boundary/comparison_mass.svg"><img src="experiments/feeder_common_boundary/comparison_mass.png" alt="FDR09 partial CAD material and catalog-option mass accounting for seven common-boundary four-payload feeder concepts" width="760"></a></p>

*Computed comparison · FDR09 historical four-payload boundary. Bars show partial CAD material and catalog-option accounting, not complete installed mass. Original mandatory-gate outcomes remain in the [comparison report](experiments/feeder_common_boundary/release/READ_ME.md); the later FM08 academic selection retains its own decision rule. [Figure source](experiments/feeder_common_boundary/make_comparison_figure.py).*

## Configuration boundaries

**VOLLEY-G5-ACR1** is the corrected twelve-3U integrated academic design. **Original Gen5** is the earlier electromagnetic study with its retained adverse findings. **Gen6/FM08-R3** contains the selected mixed 1U/3U feeder and separately versioned four/twelve-payload capacity studies. Earlier FM06/FM07 transfer, release, reset and rigid-contact cases retain their original configurations and numerical outcomes. A new selection does not revise those earlier results.

| Study | What is preserved |
|:--|:--|
| [FDR09 common-boundary concepts](experiments/feeder_common_boundary/README.md) | Native CAD/STEP, represented material, catalog options and geometry findings for all seven |
| [FM07 release/reset](experiments/feeder-release-review/README.md) | Earlier receiver-lock, exit-gate and prescribed reset geometry |
| [RVC01 rotary clearance](experiments/feeder_rotary_clearance/README.md) | Restricted FM07-R6 nominal gate-relief checks |
| [FCE13 contact diagnosis](experiments/feeder_contact_diagnosis/README.md) | Native solver logs and unresolved timestep/representation sensitivity; no accepted precision/load rating |
| [Finite-force campaign](experiments/finite-burn-review/README.md) | Matched host-assisted spring and imposed-release comparisons with native Orekit replay |
| [Pre-ACR1 system assessment](experiments/system_feasibility_closure/README.md) | Four/twelve integration, declared resource accounting and feasibility sensitivities |
| [Lunar and high-speed bounds](experiments/extended_feasibility_bounds/README.md) | Reproducible conservation and incompatibility findings, with assumptions |

The independent spring-cell bank and long gas guide remain historical research alternatives. They do not define the selected feeder or the evaluated Gen5 configuration.

## Reproduction

Each captured package includes source, inputs, tool versions, raw results and a hash manifest. Native geometry uses FreeCAD and neutral STEP exchanges; technical renders are labeled. From this repository root, run `python tools/prepublish_gate.py --all` for publication consistency. For the FM08 subsystem run `cd experiments/selected_feeder` and `python check_capture.py`. Follow each package's own instructions for native application rebuilds. The [current ACR1 reproduction route](https://github.com/aaaaaaaaaaaavm/VOLLEY/tree/main/validation/acr1) is maintained with its source package.

No physical prototype, measured release performance, environmental qualification or provider approval is claimed. Catalog references and declared analytical screens support an academic design decision; hardware testing remains a separate development phase.

## Project editions

[Main engineering study](https://github.com/aaaaaaaaaaaavm/VOLLEY) · [College thesis and presentation](https://github.com/aaaaaaaaaaaavm/VOLLEY-thesis) · [IEEE-formatted manuscript](https://github.com/aaaaaaaaaaaavm/VOLLEY-paper)

Each edition includes its relevant evidence. Historical source and failed cases remain traceable through package manifests and Git history.

## Citation and reuse

[License: CC BY 4.0](LICENSE) · [Attribution](NOTICE) · [Citation](CITATION.cff) · [Scientific figure conventions](docs/FIGURE_STANDARD.md) · [Source and result cutoff](docs/CURRENT_CONFIGURATION.md)

Cite the exact experiment/configuration and its captured source revision when reusing results. A new academic selection does not change the outcome of earlier failed cases.
