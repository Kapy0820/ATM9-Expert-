"""Pinned GTCEu 7.5.3 LV Assembler recipe and dependency checks."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import recipe_query
import explain_recipe

class LVAssemblerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = recipe_query.read_db(ROOT / "data")
        cls.manifest = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))

    def test_source_is_locked_to_matching_gtceu_753(self):
        rec = self.db["gtceu:lv_assembler"][0]
        self.assertEqual(rec["source"]["repository"], "GregTechCEu/GregTech-Modern")
        self.assertEqual(rec["source"]["commit"], "91a79b8a7a2b62ec6277423e6c0ded4af89a831e")
        self.assertEqual(rec["pack_context"]["mod_version"], "7.5.3")
        self.assertEqual(rec["verification"]["status"], "source_parsed")
        self.assertFalse(rec["verification"]["effective_in_game"])

    def test_exact_shaped_grid_and_counts(self):
        rec = self.db["gtceu:lv_assembler"][0]
        self.assertEqual(rec["crafting_pattern"], ["ACA", "VMV", "WCW"])
        amounts = {
            json.dumps(ing["choice"], sort_keys=True): ing["count"]
            for ing in rec["inputs"]
        }
        for ingredient, qty in [
            ({"item": "gtceu:lv_robot_arm"}, 2),
            ({"item": "gtceu:lv_conveyor_module"}, 2),
            ({"item": "gtceu:lv_machine_hull"}, 1),
            ({"item": "gtceu:tin_single_cable"}, 2),
            ({"tag": "gtceu:circuits/lv"}, 2)
        ]:
            self.assertEqual(amounts[json.dumps(ingredient, sort_keys=True)], qty)

    def test_assembler_bootstrap_does_not_require_itself(self):
        report = recipe_query.plan(self.db, "gtceu:lv_assembler", 1, {}, set())
        self.assertEqual(report["status"], "partial")
        steps = [x["output_item"] for x in report["steps"]]
        self.assertIn("gtceu:lv_machine_casing", steps)
        self.assertIn("gtceu:lv_machine_hull", steps)
        self.assertIn("gtceu:lv_robot_arm", steps)
        self.assertIn("gtceu:lv_conveyor_module", steps)
        self.assertEqual(steps[-1], "gtceu:lv_assembler")
        self.assertEqual(report["steps"][-1]["crafts"], 1)
        self.assertTrue(report["unresolved"])

    def test_assembler_rendered_answer_cites_source(self):
        report = recipe_query.plan(self.db, "gtceu:lv_assembler", 1, {}, set())
        output = explain_recipe.render(report, self.manifest)
        self.assertIn("ACA", output)
        self.assertIn("VMV", output)
        self.assertIn("WCW", output)
        self.assertIn("MetaTileEntityLoader.java", output)
        self.assertIn("source_parsed", json.dumps(report))
        self.assertIn("未解決", output)

if __name__ == "__main__":
    unittest.main()
