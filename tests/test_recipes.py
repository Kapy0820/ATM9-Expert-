"""Offline tests for the source-grounded ATM9 Expert recipe database."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("recipe_query", ROOT / "tools" / "recipe_query.py")
recipe_query = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe_query)

class RecipeDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = recipe_query.read_db(ROOT / "data")

    def test_fixed_source_records(self):
        manifest = __import__('json').loads((ROOT / 'data' / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(map(len, self.db.values())), manifest['recipe_count'])
        self.assertEqual(len(self.db), manifest['unique_output_items'])

    def test_index_matches_records(self):
        self.assertEqual(recipe_query.checks(self.db, ROOT / "data"), [])

    def test_recipe_source_pinned_and_unverified(self):
        for recipes in self.db.values():
            for rec in recipes:
                self.assertEqual(rec["verification"]["status"], "source_parsed")
                self.assertFalse(rec["verification"]["effective_in_game"])
                self.assertTrue(rec["source"]["commit"])
                self.assertIn(rec["source"]["commit"], rec["source"]["url"])

    def test_lookup_has_powah_choices(self):
        self.assertGreater(len(self.db["powah:dry_ice"]), 1)

    def test_plan_requires_explicit_recipe_choice(self):
        result = recipe_query.plan(self.db, "powah:dry_ice", 4, {}, set())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["steps"], [])
        self.assertEqual(result["unresolved"][0]["reason"], "multiple_recipe_options_choose_one_explicitly")

    def test_selected_recipe_exposes_missing_ingredient(self):
        rid = "powah:energizing/dry_ice/2x_dry_ice"
        result = recipe_query.plan(self.db, "powah:dry_ice", 4, {"powah:dry_ice": rid}, set())
        self.assertEqual(result["steps"][-1]["crafts"], 2)
        self.assertEqual(result["unresolved"][0]["item"], "minecraft:blue_ice")
        self.assertEqual(result["unresolved"][0]["count"], 8)

    def test_self_duplicate_does_not_invent_parallel_crafts(self):
        result = recipe_query.plan(self.db, "minecraft:dirt", 16, {}, set())
        self.assertEqual(result["status"], "partial")
        self.assertIsNone(result["steps"][-1]["crafts"])
        self.assertIn("self_referential", result["unresolved"][0]["reason"])

    def test_absence_not_mistaken_for_unobtainability(self):
        result = recipe_query.plan(self.db, "missing:item", 1, {}, set())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["unresolved"][0]["reason"], "recipe_not_in_database_not_proof_of_unobtainability")


    def test_ars_spellbook_source_and_layout(self):
        recipes = self.db["ars_nouveau:novice_spell_book"]
        self.assertEqual(len(recipes), 1)
        recipe = recipes[0]
        self.assertEqual(recipe["crafting_pattern"], ["PSP", "PBP", "PMP"])
        self.assertIn("ars.js", recipe["source"]["url"])
        self.assertIn({"choice": {"item": "gtceu:blueprint_blank"}, "count": 6}, recipe["inputs"])
        result = recipe_query.plan(self.db, "ars_nouveau:novice_spell_book", 1, {}, set())
        self.assertEqual(result["steps"][-1]["crafting_pattern"], ["PSP", "PBP", "PMP"])
        self.assertTrue(any(x.get("reason") == "tag_requires_concrete_item_resolution" for x in result["unresolved"]))

if __name__ == "__main__":
    unittest.main()
