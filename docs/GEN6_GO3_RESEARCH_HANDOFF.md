# Gen6 Go 3 research handoff — 12 October 2026

The mixed-size Gen6 service has a **surrogate**, not a customer-approved, definition: two passive 1U and two passive 3U spacecraft, four releases within one orbit from an approximately 500 km sun-synchronous host, and distinct full position/velocity states 24 hours after the last release. P130 constructs mathematically exact terminal states for both commanded release and spring-plus-host controls. Under assumed 30/16 kg installed devices, commanded release saves 3.2823 kg of host fuel but loses by 10.7177 kg on device plus consumed fuel. A +0.1 m/s release perturbation changes one-day position by about 25–27 km. These are model screens, not achieved delivery accuracy or market value.

## Two first-article hypotheses

| Candidate | Reason to retain | Fastest falsification question |
|:--|:--|:--|
| A: captured permanent-magnet carrier | Directly tests the Gen5 finite-array motor lineage with a physically different, lower-speed first article | Can a selected winding, drive, source and capture chain deliver a 4 kg dummy within rated current, temperature, exposure and mass? |
| B: captured conductive-plate carrier | Tests induction drive without a permanent magnet on the moving carrier | Do slip-dependent force, reactive power, normal force and plate heating leave a usable efficiency and precision range? |

P131's native FreeCAD/STEP envelopes are editable geometry screens. They show approximately 9.93 kg of **partial** frame/guide/carrier material, nominal clearance at five stroke stations, and a clash for an assumed 0.7° yaw plus 1.5 mm stack. P132 gives an approximately 82 J moving-energy floor at 6 m/s and an 818 J input floor **only if** end-to-end efficiency is assumed to be 10%. Neither artifact selects a source or motor. The first-article 3–6 m/s proposal does not cover P130's approximately 7 and 9 m/s mission commands.

The research decision is to carry both A and B into source-rated force, circuit, contact and containment calculations. Select neither for purchase or fabrication until a full installed bill of materials, payload/host interface, safe restraint/release path, carrier arrest and measured acceptance bands are reviewed. Preserve failed variants and source revisions in this vault. The [local P130](../validation/P130_gen6_matched_campaign.md), [P131](../validation/P131_gen6_go2_article_bounds.md), [P132](../validation/P132_gen6_go2_power_instrument_screen.md) and [candidate CAD/STEP record](../cad/gen6_first_article/README.md) are sufficient to reproduce the present screen without another repository.

Gen5 remains a separate negative computational study. A 1 km/s-class departure is a long-range research question, not a Gen6 prototype rating.
