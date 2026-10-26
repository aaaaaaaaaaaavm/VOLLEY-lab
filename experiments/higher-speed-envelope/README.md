# Higher-speed design constraints

HV-ACR1-REJECTION-SCREEN-01 · 26 October 2026. Read REPORT.md for conclusions, model limits, benchmark sources and separate hypothetical Gen6 trades.

The unchanged accepted source and four original inputs were actually evaluated at requested 10/15/30/50/100 m/s. All 22 nominal/adverse/inductance/timestep cases reject under original gates. Four 20→5 µs refinements preserve the rejection. Current accepted modeled points remain 1, 2 and 3 m/s. The 10/15 m/s intermediate release speeds are diagnostic outputs of failed complete shots, not supported operating points.

MODEL_CASES.csv and cases/ retain all real runs. CONSTRAINTS.csv and BUDGET_BOUNDS.json quantify kinetic work, acceleration/load, source voltage/power/energy, current, recoil and arrest bounds. HYPOTHETICAL_LONG_RAILS and HYPOTHETICAL_FLYAWAY_SHOES are explicitly separate arithmetic requirements, not validated redesigned force/source models. Current moving magnets alone total 3.6288 kg, excluding a 0.25/0.5/1 kg shoe retaining the current magnetic assembly.

HIGH_VELOCITY_SCREEN.png/pdf are source-linked scientific figures. EXPERIMENTAL_BENCHMARK_CARDS and literature/READING_RECEIPT distinguish actual published field/force/release measurements from simulated or closed-access claims. Existing Zhao2022 selected passages were genuinely reread from the hash-verified publisher PDF. Its PDF is not redistributed; the numerical report reproduces from captured results/cards without needing a private PDF path. A quantitative recreation of its experimental actuator remains a next benchmark task, not an accomplishment claimed here.

Reproduce with Python and the pinned requirements:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 run_screen.py
MPLCONFIGDIR=/tmp/volley-hv-mpl OPENBLAS_NUM_THREADS=1 python3 analyze_screen.py
python3 check_capture.py
```

The runner imports capture/analysis/coupled_shot.py unchanged and writes only this package. It does not invoke the original source main function. finite_motor.py is an unchanged provenance capture; its existing output maps are reused rather than rerun. No current/voltage/source limit was increased. Full reproduction changes elapsed-time fields and plot-PDF metadata; numerical outcome captures and original input hashes remain inspectable. PUBLICATION_BOUNDARY distinguishes a bounded Main research summary from Labs design variants.
