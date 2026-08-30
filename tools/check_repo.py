"""Check the VOLLEY-lab routing record and generated repository surfaces."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "TRANSFER_LEDGER.md",
    "BOLLEY_BRANCH_REGISTER.md",
    "VLAB-B001_bolley_unbound.md",
    "VLAB-X001_quadrant_gas_bearing.md",
    "VLAB-X002_passive_trim_secondary.md",
    "experiments/VLAB-X001/RUN_SHEET.md",
    "experiments/VLAB-X001/parameters.json",
    "figures/vault-map.svg",
    "figures/reopening-ledger.svg",
    "figures/transfer-map.svg",
)
NEW_ENTRY_FILES = {
    "VLAB-B001": "VLAB-B001_bolley_unbound.md",
    "VLAB-X001": "VLAB-X001_quadrant_gas_bearing.md",
    "VLAB-X002": "VLAB-X002_passive_trim_secondary.md",
}


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


def check_required() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
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


def check_entries() -> None:
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("*.md"))
    identifiers = re.findall(r"\bVLAB-[VBX]\d{3}\b", all_text)
    for identifier, filename in NEW_ENTRY_FILES.items():
        path = ROOT / filename
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
    if authoritative != NEW_ENTRY_FILES:
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


def main() -> None:
    check_required()
    check_figures()
    check_entries()
    check_x001_freeze()
    check_links()
    print("OK: shared vault entries, generated figures, namespaces and local links are current")


if __name__ == "__main__":
    main()
