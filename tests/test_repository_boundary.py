"""Keep archived side-project records outside current VOLLEY requirements."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repository_boundary_gate", SOURCE / "tools/check_repo.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class RepositoryBoundary(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.old_root = gate.ROOT
        self.addCleanup(setattr, gate, "ROOT", self.old_root)
        gate.ROOT = self.root
        for filename in gate.CURRENT_ENTRY_FILES.values():
            shutil.copyfile(SOURCE / filename, self.root / filename)

    def test_current_entries_work_without_side_project_archive(self):
        gate.check_entries()

    def test_current_entry_cannot_be_omitted(self):
        (self.root / gate.CURRENT_ENTRY_FILES["VLAB-X004"]).unlink()
        with self.assertRaisesRegex(SystemExit, "missing required entry"):
            gate.check_entries()

    def test_historical_audit_still_detects_absent_records(self):
        with self.assertRaisesRegex(SystemExit, "missing required files"):
            gate.check_required(gate.ARCHIVE_REQUIRED)

    def test_present_archive_cannot_duplicate_a_current_namespace(self):
        (self.root / "VLAB-duplicate.md").write_text("# VLAB-X004: duplicate\n")
        with self.assertRaisesRegex(SystemExit, "duplicate authoritative entry"):
            gate.check_entries()


if __name__ == "__main__":
    unittest.main()
