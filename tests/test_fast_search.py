"""Fast-path source registry must stay pinned and prefer exact paths."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FastSearchRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = json.loads((ROOT / "data/search_routes.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))

    def test_version_lock(self):
        guard = self.routes["version_guard"]
        self.assertEqual(guard["pack_repository"], self.manifest["upstream_repository"])
        self.assertEqual(guard["pack_commit"], self.manifest["upstream_commit"])
        self.assertEqual(len(guard["source_commit"]), 40)

    def test_generated_gt_machine_has_exact_symbol(self):
        routing = self.routes["routing"]
        match = next(r for r in routing if r["id"] == "gtceu_tiered_machine")
        self.assertEqual(match["primary_symbol"], "GTMachines.ASSEMBLER")
        self.assertIn(self.routes["version_guard"]["source_commit"], match["primary_source"])
        self.assertIn("GTCraftingComponents.java", match["tiered_materials_source"])
        self.assertIn("MetaTileEntityLoader.java", match["primary_source"])

    def test_bound_search_depth(self):
        policy = self.routes["stopping_rules"]
        self.assertEqual(policy["default_dependency_depth"], 1)
        self.assertLessEqual(policy["broad_code_searches_before_switching_path"], 2)
        self.assertEqual(policy["max_submission_batches"], 1)
        self.assertTrue(policy["avoid_duplicate_pr"])

if __name__ == "__main__":
    unittest.main()
