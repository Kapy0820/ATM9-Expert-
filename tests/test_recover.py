"""Tests of official pinned-source recovery, with no network access."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("recover_recipe", ROOT / "tools" / "recover_recipe.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)

COMMIT = "309d0fa357b00d855f3a50739ae64737f7537936"
MANIFEST = {"upstream_repository": "AllTheMods/atm9-expert", "upstream_commit": COMMIT}
JS = """
ServerEvents.recipes(event => {
    event.shaped('ignored:output', ['SS', 'SS'], { S: 'minecraft:stone' });
    allthemods.shaped('ars_nouveau:novice_spell_book', [
        'PSP',
        'PBP',
        'PMP'
    ], {
        P: 'gtceu:blueprint_blank',
        S: 'ars_nouveau:source_gem',
        B: '#forge:books',
        M: 'botania:rune_mana'
    }).id('gregification:novice_spell_book');
});
"""

class SourceRecoveryTests(unittest.TestCase):
    def test_js_shaped_reconstruction(self):
        parsed = recovery.parse_shaped_js(JS)
        self.assertEqual(len(parsed), 1)
        record = parsed[0][2]
        self.assertEqual(record["output"]["item"], "ars_nouveau:novice_spell_book")
        self.assertEqual(record["crafting_pattern"], ["PSP", "PBP", "PMP"])
        self.assertIn({"choice": {"item": "gtceu:blueprint_blank"}, "count": 6}, record["inputs"])
        self.assertIn({"choice": {"tag": "forge:books"}, "count": 1}, record["inputs"])

    def test_source_metadata_is_fixed_and_unverified(self):
        records = recovery.extract(JS, "ars_nouveau:novice_spell_book",
            "AllTheMods/atm9-expert", COMMIT, "kubejs/server_scripts/Gregification/Mods/ars.js")
        self.assertEqual(records[0]["verification"]["status"], "source_parsed")
        self.assertFalse(records[0]["verification"]["effective_in_game"])
        self.assertIn(COMMIT, records[0]["source"]["url"])
        self.assertIn("#L", records[0]["source"]["url"])

    def test_rejects_non_pinned_or_untrusted_links(self):
        valid = ("https://github.com/AllTheMods/atm9-expert/blob/" + COMMIT
                 + "/kubejs/server_scripts/Gregification/Mods/ars.js")
        self.assertEqual(recovery.parse_url(valid, MANIFEST)[1], COMMIT)
        for bad in (
            valid.replace("AllTheMods", "another-author"),
            valid.replace(COMMIT, "a" * 40),
            valid.replace("github.com", "evil.example"),
            valid.replace("kubejs/server_scripts/", "other/"),
            "http://" + valid[8:]
        ):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                recovery.parse_url(bad, MANIFEST)

    def test_rejects_recipe_that_cannot_be_parsed(self):
        with self.assertRaises(ValueError):
            recovery.extract("allthemods.shaped('test:thing', unknown)", "test:thing",
                "AllTheMods/atm9-expert", COMMIT, "kubejs/server_scripts/test.js")

    def test_json_recovery_does_not_claim_verification(self):
        data = json.dumps({
            "type": "powah:energizing",
            "ingredients": [{"item": "minecraft:blue_ice"}] * 4,
            "result": {"item": "powah:dry_ice", "count": 2},
            "energy": 20000
        })
        rec = recovery.extract(data, "powah:dry_ice", "AllTheMods/atm9-expert", COMMIT,
            "kubejs/data/powah/recipes/energizing/dry_ice/2x_dry_ice.json")[0]
        self.assertEqual(rec["inputs"][0]["count"], 4)
        self.assertEqual(rec["recipe_id"], "powah:energizing/dry_ice/2x_dry_ice")
        self.assertEqual(rec["verification"]["status"], "source_parsed")

if __name__ == "__main__":
    unittest.main()
