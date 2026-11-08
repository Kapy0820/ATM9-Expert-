"""Check that agents have a pinned, ordered source map and human-readable steps."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import recipe_query
import explain_recipe

class SourceAndWalkthroughTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = recipe_query.read_db(ROOT / "data")
        cls.manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "data/source_registry.json").read_text(encoding="utf-8"))

    def test_source_registry_is_pinned_and_ordered(self):
        registry, manifest = self.registry, self.manifest
        self.assertEqual(registry["upstream_commit"], manifest["upstream_commit"])
        self.assertEqual(registry["upstream_repository"], manifest["upstream_repository"])
        self.assertEqual([x["order"] for x in registry["sources"]], list(range(1, len(registry["sources"])+1)))
        self.assertGreaterEqual(len(registry["sources"]), 9)
        for record in registry["sources"]:
            if record["kind"] == "official_at_pinned_commit":
                self.assertIn(registry["upstream_commit"], record["url"])
                self.assertEqual(urlparse(record["url"]).hostname, "github.com")
            elif record["kind"] == "local":
                self.assertTrue(record["url"].startswith("https://github.com/Kapy0820/ATM9-Expert-/"))

    def test_example_dependency_steps_and_grid(self):
        report = recipe_query.plan(self.db, "ars_nouveau:apprentice_spell_book", 1, {}, set())
        self.assertEqual(report["status"], "partial")
        order = [step["output_item"] for step in report["steps"]]
        self.assertEqual(order, [
            "gtceu:blueprint_blank", "ars_nouveau:novice_spell_book",
            "ars_nouveau:apprentice_spell_book"
        ])
        self.assertEqual(report["steps"][0]["crafts"], 6)
        self.assertEqual(report["steps"][-1]["crafting_pattern"], ["PSP", "PBP", "PMP"])
        self.assertIn("forge:plates/manasteel", [x.get("tag") for x in
            [ing["choice"] for ing in report["steps"][-1]["consumed_inputs"]] if x.get("tag")])
        self.assertTrue(any(x["reason"] == "recipe_not_in_database_not_proof_of_unobtainability"
                            for x in report["unresolved"]))

    def test_readable_walkthrough_contains_source_and_unknowns(self):
        report = recipe_query.plan(self.db, "ars_nouveau:apprentice_spell_book", 1, {}, set())
        rendered = explain_recipe.render(report, self.manifest)
        self.assertIn("PSP", rendered)
        self.assertIn("PBP", rendered)
        self.assertIn("PMP", rendered)
        self.assertIn("Gregification/Mods/ars.js", rendered)
        self.assertIn("Gregification/miscItems.js", rendered)
        self.assertIn("source_parsed", json.dumps(report))
        self.assertIn("実ゲーム未検証", rendered)
        self.assertIn("未解決", rendered)
        self.assertIn("gtceu:blueprint_blank", rendered)

    def test_multiple_recipes_not_assumed_unique(self):
        report = recipe_query.plan(self.db, "powah:dry_ice", 2, {}, set())
        out = explain_recipe.render(report, self.manifest)
        self.assertIn("複数の製法", out)
        self.assertIn("powah:energizing/dry_ice/2x_dry_ice", out)
        self.assertIn("powah:energizing/dry_ice/3x_dry_ice", out)
        self.assertNotIn("## 確認できた作業", out)

    def test_unrecorded_item_does_not_claim_impossibility(self):
        report = recipe_query.plan(self.db, "example:unknown", 1, {}, set())
        out = explain_recipe.render(report, self.manifest)
        self.assertIn("未収録", out)
        self.assertIn("公式recipeRemovals", out)

if __name__ == "__main__":
    unittest.main()
