#!/usr/bin/env python3
"""Source-aware ATM9 Expert recipe lookup and conservative crafting-path planner.

Requires Python >=3.9, standard library only. Never assumes the database is complete.
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def read_db(data_dir=DATA):
    records = defaultdict(list)
    folder = data_dir / "recipes"
    for file in sorted(folder.glob("*.json")):
        document = json.loads(file.read_text(encoding="utf-8"))
        for recipe in document.get("recipes", []):
            records[recipe["output"]["item"]].append(recipe)
    return records

def index_from_db(db):
    return {
        "schema_version": 1,
        "items": {
            item: [
                {"recipe_id": r["recipe_id"],
                 "file": "data/recipes/" + item.split(":")[0] + ".json",
                 "status": r["verification"]["status"]}
                for r in sorted(recipes, key=lambda r: r["recipe_id"])
            ]
            for item, recipes in sorted(db.items())
        }
    }

def checks(db, data_dir):
    errors = []
    seen = set()
    for item, recipes in db.items():
        for r in recipes:
            rid = r.get("recipe_id")
            if rid in seen:
                errors.append("Duplicate recipe_id: " + str(rid))
            seen.add(rid)
            out = r.get("output", {})
            if out.get("item") != item or not isinstance(out.get("count"), int) or out["count"] < 1:
                errors.append("Invalid output: " + str(rid))
            if not r.get("source", {}).get("url") or not r.get("source", {}).get("commit"):
                errors.append("Missing pinned source: " + str(rid))
            state = r.get("verification", {}).get("status")
            if state not in ("source_parsed", "verified"):
                errors.append("Invalid verification status: " + str(rid))
            if state == "verified" and not r["verification"].get("pack_version"):
                errors.append("Verified recipe missing pack_version: " + str(rid))
            if not isinstance(r.get("inputs"), list):
                errors.append("Invalid inputs: " + str(rid))
                continue
            for ing in r["inputs"]:
                if not isinstance(ing.get("count"), int) or ing["count"] < 1:
                    errors.append("Invalid input count: " + str(rid))
                choice = ing.get("choice")
                choices = ing.get("choices")
                if (choice is None) == (choices is None):
                    errors.append("Must have exactly one of choice or choices: " + str(rid))
                for alternative in ([choice] if choice is not None else (choices or [])):
                    if not isinstance(alternative, dict) or ("item" in alternative) == ("tag" in alternative):
                        errors.append("Invalid ingredient alternative: " + str(rid))
    indexed = data_dir / "item_index.json"
    if indexed.exists():
        try:
            current = json.loads(indexed.read_text(encoding="utf-8"))
            if current != index_from_db(db):
                errors.append("item_index.json is stale (run rebuild-index)")
        except (OSError, ValueError):
            errors.append("item_index.json is invalid")
    else:
        errors.append("item_index.json is missing")
    return errors

def plan(db, item, requested, choices, inventory):
    steps = []
    unresolved = []
    supplied = []
    def descend(target, amount, trail):
        if target in inventory:
            supplied.append({"item": target, "count": amount, "source": "user-provided"})
            return
        if target in trail:
            unresolved.append({"item": target, "count": amount, "reason": "cycle_or_self_duplication_requires_seed", "path": trail + [target]})
            return
        options = db.get(target, [])
        if not options:
            unresolved.append({"item": target, "count": amount, "reason": "recipe_not_in_database_not_proof_of_unobtainability"})
            return
        selected_id = choices.get(target)
        if selected_id:
            matching = [r for r in options if r["recipe_id"] == selected_id]
            if len(matching) != 1:
                unresolved.append({"item": target, "reason": "invalid_recipe_choice", "available": [r["recipe_id"] for r in options]})
                return
            chosen = matching[0]
        elif len(options) != 1:
            unresolved.append({"item": target, "count": amount, "reason": "multiple_recipe_options_choose_one_explicitly", "available": [r["recipe_id"] for r in options]})
            return
        else:
            chosen = options[0]
        runs = math.ceil(amount / chosen["output"]["count"])
        for ing in chosen["inputs"]:
            options_ing = [ing["choice"]] if "choice" in ing else ing.get("choices", [])
            need = ing["count"] * runs
            if len(options_ing) != 1:
                unresolved.append({"item": target, "count": need, "reason": "alternative_ingredients_unresolved", "choices": options_ing})
            elif "tag" in options_ing[0]:
                unresolved.append({"tag": options_ing[0]["tag"], "count": need, "reason": "tag_requires_concrete_item_resolution"})
            else:
                descend(options_ing[0]["item"], need, trail + [target])
        steps.append({
            "output_item": target, "requested_count": amount, "produced_count": chosen["output"]["count"] * runs,
            "recipe_id": chosen["recipe_id"], "crafts": runs, "station": chosen.get("station"),
            "consumed_inputs": chosen["inputs"], "reusable_catalysts": chosen.get("catalysts", []),
            "costs_per_craft": chosen.get("costs", {}), "source": chosen["source"],
            "verification": chosen["verification"],
        })
    descend(item, requested, [])
    has_unverified = any(step["verification"]["status"] != "verified" for step in steps)
    # Even with a closed dependency graph, the station and in-game availability need verification.
    return {
        "requested": {"item": item, "count": requested},
        "status": "partial" if unresolved or has_unverified else "graph_resolved_requires_station_verification",
        "steps": steps,
        "provided_by_user": supplied,
        "unresolved": unresolved,
        "warnings": ["The pack-wide recipe set is incomplete. No absence claim is justified.",
                     "Craft counts do not optimize by-products, reusable inputs, inventory, or batch merging.",
                     "Source-parsed recipes are NOT confirmed active in the running pack."],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA, help="data directory")
    sub = parser.add_subparsers(dest="command", required=True)
    look = sub.add_parser("lookup", help="Find all recipes with this output item ID")
    look.add_argument("item")
    pl = sub.add_parser("plan", help="Show conservative dependency plan")
    pl.add_argument("item")
    pl.add_argument("--count", type=int, default=1)
    pl.add_argument("--choose", action="append", default=[], metavar="ITEM=RECIPE_ID")
    pl.add_argument("--have", action="append", default=[], metavar="ITEM")
    sub.add_parser("validate")
    sub.add_parser("rebuild-index")
    args = parser.parse_args()
    db = read_db(args.data)
    if args.command == "validate":
        errors = checks(db, args.data)
        print(json.dumps({"ok": not errors, "recipe_count": sum(map(len, db.values())),
                          "output_items": len(db), "errors": errors}, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    if args.command == "rebuild-index":
        path = args.data / "item_index.json"
        path.write_text(json.dumps(index_from_db(db), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(str(path))
        return 0
    if args.command == "lookup":
        recipes = db.get(args.item, [])
        print(json.dumps({"item": args.item, "status": "found" if recipes else "not_in_database",
                          "recipes": recipes, "caution": "Missing does not imply unobtainable; source_parsed is not verified."},
                         ensure_ascii=False, indent=2))
        return 0
    if args.count < 1:
        parser.error("--count must be positive")
    selections = {}
    for text in args.choose:
        if "=" not in text:
            parser.error("--choose format: ITEM=RECIPE_ID")
        key, value = text.split("=", 1)
        selections[key] = value
    print(json.dumps(plan(db, args.item, args.count, selections, set(args.have)),
                     ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
