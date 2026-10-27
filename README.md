# VOLLEY Labs
### Mechanism research, higher-speed launchers and orbital delivery

VOLLEY Labs develops and preserves the engineering experiments behind commanded CubeSat deployment: feeder mechanisms, finite electromagnetic models, source-coupled launchers and mission architecture studies. Each experiment has its own configuration, inputs, results and reproduction route.

[10 m/s design study](experiments/ten-metre-per-second-design/README.md) · [Current-setup speed envelope](experiments/speed-envelope-extension/README.md) · [Feeder trade](experiments/selected_feeder/verification/REPORT.md) · [Lunar delivery](experiments/lunar-delivery-design-space/README.md)

<p><a href="figures/acr1-polish/assembly_hero.png"><img src="figures/acr1-polish/assembly_hero.webp" alt="VOLLEY Gen5 ACR1 academic reference assembly, showing the storage banks and central feed and launch mechanism" width="900"></a></p>

*CAD-derived Blender render · Gen5 ACR1 academic reference. [Source and render provenance](figures/acr1-polish/POLISH_PROVENANCE.json). Research configurations below retain their separate identities.*

## Higher-speed launcher research

| Experiment | Question and result |
|:--|:--|
| **[R10 / F10: new 10 m/s configurations](experiments/ten-metre-per-second-design/README.md)** | New finite winding/magnet maps, source and installed-mass accounting. R10 passes its declared nominal/adverse circuit/motion cases; the attached-shoe F10 adverse case misses the speed tolerance. |
| **[Unchanged-configuration speed envelope](experiments/speed-envelope-extension/README.md)** | 106 records, including 88 new computations and 17 timestep refinements. Common sampled upper command points are 4.60 m/s nominal and 3.70 m/s adverse across three inductances. |
| **[Published experimental benchmark](experiments/published-force-benchmark/README.md)** | Traceable reconstruction of a measured force/current observable, with separate calibration and held-out comparisons. |
| **[Earth-to-lunar-orbit delivery](experiments/lunar-delivery-design-space/README.md)** | Departure, host recoil and lunar capture treated separately; analytical bounds plus an ideal numerical five-day transfer and post-capture coast. |

<p><a href="experiments/ten-metre-per-second-design/R10_VELOCITY.svg"><img src="experiments/ten-metre-per-second-design/R10_VELOCITY.png" alt="Computed reusable-carrier R10 launch and arrest velocity histories for the separately specified 10 m/s configuration" width="850"></a></p>

*Computed result · R10-R1. The study supplies finite field, winding, source, energy, mass and one-shot thermal calculations. It is a new computational design, separate from the Gen5 1–3 m/s academic reference.*

## Feeder architectures

The selected guided lead-screw principle provides controlled transfer through a restrained channel into a defined receiver. The trade preserves all seven candidates, their common-boundary CAD, quantitative sizing and failure mechanisms.

![Seven feeder concepts shown at common orthographic view and physical scale](figures/feeder-concepts/seven_feeder_concepts.png)

*CAD-derived Blender comparison · FDR09-R1 geometry. Selection follows the separately identified later FM08 / FDR10 trade.*

| Rank | Architecture | Weighted judgment / 10 | Engineering role |
|---:|:--|---:|:--|
| 1 | Guided lead screw | 7.30 | Selected transfer principle; guided pusher and positive receiving stops |
| 2 | Rack and pawl | 7.10 | Runner-up; backlash, tooth support and engagement require control |
| 3 | Spring and two gates | 6.90 | Low-active-power alternative; governed motion and reset are decisive |
| 4 | Belt shuttle | 6.70 | Flexible packaging; tension and skipped engagement drive the comparison |
| 5 | Indexed drum | 6.40 | Common-port storage; indexing and shared-path isolation drive integration |
| 6 | Telescopic | 6.05 | Compact stowage; stage overlap, alignment and binding govern performance |
| 7 | Pantograph | 5.50 | Collapsible storage; near-flat linkage loads and joint play govern sizing |

Weights: safety 35%, packaging/mass 25%, positioning 20%, cycle/power 10%, manufacture 10%. Scores are declared engineering judgments, not measured reliability; the sensitivity study records ranking changes.

[Selection report](experiments/selected_feeder/verification/REPORT.md) · [Seven native CAD/STEP concepts](experiments/feeder_common_boundary/README.md) · [Concept cards](figures/feeder-concepts/README.md) · [Interactive gallery](docs/feeder-concepts.html)

## Design lineage and numerical studies

| Study family | Contents |
|:--|:--|
| [Selected FM08 feeder](experiments/selected_feeder/README.md) | Mixed 1U/3U subsystem, native CAD, sizing and selection rationale |
| [Release and reset](experiments/feeder-release-review/README.md) | Receiver locking, gate motion and prescribed reset geometry |
| [Contact diagnosis](experiments/feeder_contact_diagnosis/README.md) | Solver histories and timestep/representation sensitivity |
| [Finite-force orbital campaigns](experiments/finite-burn-review/README.md) | Matched host-assisted spring and imposed-release comparisons with Orekit replay |
| [System feasibility studies](experiments/system_feasibility_closure/README.md) | Four/twelve-payload integration and installed-resource accounting |
| [Extended physical bounds](experiments/extended_feasibility_bounds/README.md) | Conservation, scaling and architecture constraints |

The [configuration guide](docs/CURRENT_CONFIGURATION.md) separates original Gen5, the integrated Gen5 ACR1 academic reference, mixed-size Gen6 feeder studies and later launcher experiments. A new configuration does not replace an earlier calculation or inherit its verification.

## Inspect and reproduce

Follow each experiment's README for exact inputs, dependencies and commands. Captured packages include source identities, numerical outputs and hash manifests. Native CAD uses FreeCAD/STEP; render captions identify visualization and provenance. Computational criteria and physical tests remain distinct evidence stages.

```bash
python3 tools/prepublish_gate.py --all
```

[Integrated VOLLEY study](https://github.com/aaaaaaaaaaaavm/VOLLEY) · [Academic report](https://github.com/aaaaaaaaaaaavm/VOLLEY-thesis) · [Research manuscript](https://github.com/aaaaaaaaaaaavm/VOLLEY-paper) · [Scientific figure conventions](docs/FIGURE_STANDARD.md) · [Citation](CITATION.cff) · [Licensing](LICENSE)
