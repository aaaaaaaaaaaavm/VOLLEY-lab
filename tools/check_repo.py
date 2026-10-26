"""Check the VOLLEY-lab routing record and generated repository surfaces."""

from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CURRENT_REQUIRED = (
    "README.md",
    "docs/CURRENT_CONFIGURATION.md",
    "docs/PROJECT_BOUNDARY.md",
    "VLAB-X004_feeder_candidate_r1.md",
    "VLAB-X005_segmented_stator_hypothesis.md",
    "figures/gen5_finite_coupled_shot.png",
    "figures/r1_candidate_step.jpg",
    "figures/r1_candidate_step.provenance.json",
    "figures/vault-map.svg",
    "figures/reopening-ledger.svg",
    "figures/transfer-map.svg",
)
ARCHIVE_ENTRY_FILES = {
    "VLAB-B001": "VLAB-B001_bolley_unbound.md",
    "VLAB-B002": "VLAB-B002_active_cooperative_interface.md",
    "VLAB-B003": "VLAB-B003_distributed_fluxpiston_feed.md",
    "VLAB-X001": "VLAB-X001_quadrant_gas_bearing.md",
    "VLAB-X002": "VLAB-X002_passive_trim_secondary.md",
    "VLAB-X003": "VLAB-X003_independent_cell_bank.md",
    "VLAB-X004": "VLAB-X004_feeder_candidate_r1.md",
    "VLAB-X005": "VLAB-X005_segmented_stator_hypothesis.md",
}
CURRENT_ENTRY_FILES = {
    key: value for key, value in ARCHIVE_ENTRY_FILES.items()
    if key in {"VLAB-X003", "VLAB-X004", "VLAB-X005"}
}
ARCHIVE_REQUIRED = (
    "TRANSFER_LEDGER.md",
    "BOLLEY_BRANCH_REGISTER.md",
    *ARCHIVE_ENTRY_FILES.values(),
    "experiments/VLAB-X001/RUN_SHEET.md",
    "experiments/VLAB-X001/parameters.json",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_generator():
    path = ROOT / "tools" / "generate_readme_figure.py"
    spec = importlib.util.spec_from_file_location("vault_figures", path)
    if spec is None or spec.loader is None:
        fail("cannot load figure generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_required(paths=CURRENT_REQUIRED) -> None:
    missing = [path for path in paths if not (ROOT / path).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))


def check_figures() -> None:
    generator = load_generator()
    expected = {
        "figures/vault-map.svg": generator.render(),
        "figures/reopening-ledger.svg": generator.reopening_ledger(),
        "figures/transfer-map.svg": generator.transfer_map(),
    }
    stale = [path for path, body in expected.items() if (ROOT / path).read_text(encoding="utf-8") != body]
    if stale:
        fail("stale generated figures: " + ", ".join(stale))
    provenance = json.loads((ROOT / "figures/r1_candidate_step.provenance.json").read_text())
    image = ROOT / provenance["image"]
    if hashlib.sha256(image.read_bytes()).hexdigest() != provenance["image_sha256"]:
        fail("R1 STEP illustration differs from its source record")


def check_entries(*, historical: bool = False) -> None:
    required = ARCHIVE_ENTRY_FILES if historical else CURRENT_ENTRY_FILES
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("*.md"))
    identifiers = re.findall(r"\bVLAB-[VBX]\d{3}\b", all_text)
    for identifier, filename in required.items():
        path = ROOT / filename
        if not path.is_file():
            fail(f"missing required entry {filename}")
        title_count = len(re.findall(rf"^#\s+{re.escape(identifier)}:", path.read_text(encoding="utf-8"), re.M))
        if title_count != 1:
            fail(f"{identifier} must have exactly one authoritative title")
        if identifier not in identifiers:
            fail(f"{identifier} is absent from the vault record")
    authoritative = {}
    for path in ROOT.glob("VLAB-*.md"):
        match = re.search(r"^#\s+(VLAB-[VBX]\d{3}):", path.read_text(encoding="utf-8"), re.M)
        if not match:
            fail(f"{path.name} has no namespaced title")
        identifier = match.group(1)
        if identifier in authoritative:
            fail(f"duplicate authoritative entry {identifier}: {authoritative[identifier]} and {path.name}")
        authoritative[identifier] = path.name
    if any(authoritative.get(key) != value for key, value in required.items()):
        fail(f"entry routing mismatch: {authoritative!r}")
    # Present archive pages retain their namespaces; their absence is checked
    # only by the separately requested archive audit.
    if any(ARCHIVE_ENTRY_FILES.get(key) != value for key, value in authoritative.items()):
        fail(f"entry routing mismatch: {authoritative!r}")


def check_x001_freeze() -> None:
    import json

    path = ROOT / "experiments" / "VLAB-X001" / "parameters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "volley-lab.quadrant-bearing/1":
        fail("VLAB-X001 controlled input has the wrong schema")
    if data.get("state") not in {"FROZEN_NOT_RUN", "RUN"}:
        fail("VLAB-X001 controlled input has no recognised state")
    if set(data.get("targets", {})) != {"volley_reference", "bolley_reference", "bolley_qualification"}:
        fail("VLAB-X001 target set changed")
    if len(data.get("bands", {})) != 9:
        fail("VLAB-X001 controlled limits changed shape")


def check_links() -> None:
    failures = []
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for markdown in ROOT.rglob("*.md"):
        for target in pattern.findall(markdown.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            resolved = (markdown.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{markdown.relative_to(ROOT)} -> {target} escapes repository")
                continue
            if not resolved.exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> {target}")
    if failures:
        fail("broken local links:\n  " + "\n  ".join(failures))



def check_evidence_commands() -> None:
    """Run the same numerical/capture checks required by the CI evidence job."""
    commands = [
        ["analysis/gen6_mixed_mission.py", "--check"],
        ["analysis/gen6_matched_campaign.py", "--check"],
        ["analysis/gen6_go2_article_bounds.py", "--check"],
        ["analysis/gen6_go2_power_instrument_screen.py", "--check"],
        ["analysis/gen6_g0_reference.py", "--check"],
        ["analysis/gen6_feeder_load_screen.py", "--check"],
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
        ["experiments/feeder-design-review/check_capture.py"],
        ["experiments/coupled-delivery-review/check_capture.py"],
        ["experiments/native-campaign-review/check_capture.py"],
        ["experiments/finite-burn-review/check_capture.py"],
        ["experiments/feeder-actuation-review/check_capture.py"],
        ["experiments/feeder-integrity-review/check_capture.py"],
        ["experiments/feeder-contact-verification/check_capture.py"],
        ["experiments/feeder-release-review/check_capture.py"],
        ["experiments/feeder_rotary_clearance/check_capture.py"],
        ["experiments/feeder_contact_diagnosis/check_capture.py"],
        ["experiments/extended_feasibility_bounds/check_capture.py"],
        ["experiments/feeder_common_boundary/check_capture.py"],
        ["experiments/captive-transfer-review/check_capture.py"],
        ["experiments/replenishment-feasibility/check_capture.py"],
    ]
    for arguments in commands:
        subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-only", action="store_true",
                        help="audit retained historical records without making them current VOLLEY dependencies")
    args = parser.parse_args()
    if args.historical_only:
        check_required(ARCHIVE_REQUIRED)
        check_entries(historical=True)
        check_x001_freeze()
        check_links()
        print("OK: retained historical archive identities, namespaces and local links")
        return
    check_required()
    check_figures()
    check_entries()
    check_links()
    check_evidence_commands()
    subprocess.run([sys.executable, "figures/feeder-concepts/verify_assets.py"], cwd=ROOT, check=True)
    print("OK: current VOLLEY evidence, generated figures, namespaces and published local links")


if __name__ == "__main__":
    main()
