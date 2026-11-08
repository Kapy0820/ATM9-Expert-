"""Tests: unsupported JSON must never be converted into a fictitious recipe."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("import_json", ROOT / "tools" / "import_json.py")
import_json = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_json)

class RecipeImporterTests(unittest.TestCase):
    def test_powah_energizing_counts_and_cost(self):
        rec = import_json.parse({
            "type": "powah:energizing",
            "ingredients": [{"item": "minecraft:blue_ice"}] * 4,
            "energy": 20000,
            "result": {"item": "powah:dry_ice", "count": 2}
        })
        self.assertEqual(rec["inputs"], [{"choice": {"item": "minecraft:blue_ice"}, "count": 4}])
        self.assertEqual(rec["output"]["count"], 2)
        self.assertEqual(rec["costs"]["energy"], 20000)

    def test_botania_catalyst_is_reusable(self):
        rec = import_json.parse({
            "type": "botania:mana_infusion",
            "input": {"item": "minecraft:dirt"},
            "output": {"item": "minecraft:dirt", "count": 2},
            "catalyst": {"type": "block", "block": "botania:conjuration_catalyst"},
            "mana": 2000
        })
        self.assertFalse(rec["catalysts"][0]["consumed"])
        self.assertEqual(rec["costs"]["mana"], 2000)

    def test_shaped_ingredients_count_pattern(self):
        rec = import_json.parse({
            "type": "minecraft:crafting_shaped",
            "pattern": ["II", " S"],
            "key": {"I": {"tag": "forge:ingots/iron"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "minecraft:iron_sword"}
        })
        self.assertIn({"choice": {"tag": "forge:ingots/iron"}, "count": 2}, rec["inputs"])

    def test_alternatives_not_collapsed_to_single_item(self):
        rec = import_json.parse({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [[{"item": "minecraft:iron_ingot"}, {"item": "minecraft:copper_ingot"}]],
            "result": {"item": "test:item"}
        })
        self.assertEqual(len(rec["inputs"][0]["choices"]), 2)

    def test_unknown_machine_shape_rejected(self):
        with self.assertRaises(import_json.Unsupported):
            import_json.parse({
                "type": "gtceu:assembler",
                "result": {"item": "gtceu:circuit"},
                "inputs": ["minecraft:iron_ingot"]
            })

    def test_conditional_recipe_rejected(self):
        with self.assertRaises(import_json.Unsupported):
            import_json.parse({
                "type": "minecraft:crafting_shapeless",
                "ingredients": [{"item": "minecraft:dirt"}],
                "result": {"item": "test:item"},
                "conditions": [{"type": "unknown"}]
            })

if __name__ == "__main__":
    unittest.main()
