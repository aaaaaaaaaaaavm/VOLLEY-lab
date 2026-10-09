# VLAB-X004 — widened-enclosure feeder route

**Disposition: unselected geometry candidate.** This study asks whether a simple side-transfer plus central lift path can remove the evaluated Gen5 cassette/track interference. It does not select a production feeder or change the evaluated Gen5 model.

| Screen | Evaluated Gen5 | R1 candidate |
|:--|--:|--:|
| External enclosure width | 530 mm | 570 mm |
| Internal width available | 526 mm | 566 mm |
| Track plus two cassette widths | 537 mm before clearance | Cassettes moved outside track |
| Track/cassette exact-solid overlap | 32,915 mm³ each side | 0 mm³ |
| Cassette/track lateral clearance | Clash | 5 mm per side |
| Cassette/inner-skin clearance | Fails reference placement | 9.5 mm per side |
| Scripted 3U envelope routes clearing listed fixed parts | Unrun | 12/12 |

The geometry run uses exact STEP-solid intersections at route poses and conservative axis-aligned swept boxes for each side transfer and vertical lift. It exports a 21-instance native FreeCAD review document, STEP parts and two assembly STEP versions in the Gen5 engineering repository. The 0.99 kg simple aluminium-skin increment is a material-volume proxy only; no revised installed mass exists.

![R1 parameter-derived feeder section](figures/gen5_feeder_candidate_r1.png)

*Parameter-derived section, not an interactive FreeCAD screenshot or built mechanism.*

## Reopening gate

Model the actual lift carriage/actuator and launch restraint, clear tolerances, harness and jam states, and rerun structural, thermal, installed mass, magnetic force and host accommodation against a named provider interface. Preserve the existing Gen5 failure as the evaluated result. The [exact CAD report and files](https://github.com/aaaaaaaaaaaavm/VOLLEY/tree/main/cad) are supporting artifacts; the table above states this candidate's finding without requiring the other repository to understand it.
