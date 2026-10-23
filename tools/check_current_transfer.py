"""Verify current repository-local selected mechanism and system captures."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
for name in ['selected_feeder','system_feasibility_closure','lunar_native_coast']:
 subprocess.run([sys.executable,str(R/'experiments'/name/'check_capture.py')],check=True,cwd=R)
