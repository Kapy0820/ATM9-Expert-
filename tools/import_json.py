#!/usr/bin/env python3
"""Conservative importer for JSON recipe definitions, WITHOUT running the modpack.

Recognized only: vanilla crafting/cooking, Botania mana_infusion, Powah energizing.
Unknown layouts are reported, never silently represented as complete recipes.
All imported recipes have status source_parsed, never verified.
"""
import argparse
import collections
import json
from pathlib import Path

KINDS = {
    "minecraft:crafting_shaped", "minecraft:crafting_shapeless",
    "minecraft:smelting", "minecraft:blasting",
    "minecraft:smoking", "minecraft:campfire_cooking",
    "botania:mana_infusion", "powah:energizing"
}

class Unsupported(Exception):
    pass

def atom(obj):
    if isinstance(obj, dict) and isinstance(obj.get("item"), str):
        return {"item": obj["item"]}
    if isinstance(obj, dict) and isinstance(obj.get("tag"), str):
        return {"tag": obj["tag"]}
    raise Unsupported("ingredient cannot be resolved to an explicit item or tag")

def ingredient(entry):
    if isinstance(entry, list):
        if not entry:
            raise Unsupported("empty alternatives")
        return {"choices": [atom(x) for x in entry], "count": 1}
    return {"choice": atom(entry), "count": 1}

def combine(inputs):
    grouped = collections.OrderedDict()
    for ing in inputs:
        identity = json.dumps({k: v for k, v in ing.items() if k != "count"}, sort_keys=True)
        if identity not in grouped:
            grouped[identity] = dict(ing)
        else:
            grouped[identity]["count"] += ing["count"]
    return list(grouped.values())

def parse(recipe):
    typ = recipe.get("type")
    if typ not in KINDS:
        raise Unsupported("unknown recipe type: " + str(typ))
    output = recipe.get("result", recipe.get("output"))
    if isinstance(output, str):
        output = {"item": output, "count": 1}
    if not isinstance(output, dict) or not isinstance(output.get("item"), str):
        raise Unsupported("unsupported output shape")
    count = output.get("count", 1)
    if not isinstance(count, int) or count < 1:
        raise Unsupported("invalid output count")
    extras = {}
    catalysts = []
    if typ == "minecraft:crafting_shaped":
        pattern = recipe.get("pattern")
        key = recipe.get("key")
        if not isinstance(pattern, list) or not isinstance(key, dict):
            raise Unsupported("invalid shaped crafting pattern/key")
        if not all(isinstance(row, str) for row in pattern):
            raise Unsupported("invalid shaped pattern row")
        used = collections.Counter("".join(pattern).replace(" ", ""))
        if any(char not in key for char in used):
            raise Unsupported("shaped pattern refers to missing key")
        ins = []
        for char, amount in used.items():
            ing = ingredient(key[char])
            ing["count"] = amount
            ins.append(ing)
    elif typ in ("minecraft:crafting_shapeless", "powah:energizing"):
        raw = recipe.get("ingredients")
        if not isinstance(raw, list):
            raise Unsupported("missing ingredients list")
        ins = [ingredient(x) for x in raw]
    elif typ in ("minecraft:smelting", "minecraft:blasting", "minecraft:smoking", "minecraft:campfire_cooking"):
        ins = [ingredient(recipe.get("ingredient"))]
        if "cookingtime" in recipe:
            extras["duration_ticks"] = recipe["cookingtime"]
        if "experience" in recipe:
            extras["experience"] = recipe["experience"]
    else:
        ins = [ingredient(recipe.get("input"))]
        if recipe.get("catalyst"):
            cat = recipe["catalyst"]
            if not (isinstance(cat, dict) and isinstance(cat.get("block"), str)):
                raise Unsupported("non-block catalyst layout")
            catalysts.append({"block": cat["block"], "consumed": False, "description": "mana infusion catalyst"})
    if "mana" in recipe:
        extras["mana"] = recipe["mana"]
    if "energy" in recipe:
        extras["energy"] = recipe["energy"]
    if typ == "minecraft:crafting_shaped" and "conditions" in recipe:
        raise Unsupported("conditional shaped recipe requires condition evaluation")
    if "conditions" in recipe:
        raise Unsupported("conditional recipe requires condition evaluation")
    # Unknown recipe-specific fields can affect meaning; do not silently ignore them.
    accepted = {"type", "result", "output", "group", "category", "show_notification",
                "pattern", "key", "ingredients", "ingredient", "input",
                "catalyst", "mana", "energy", "cookingtime", "experience"}
    unexpected = sorted(set(recipe) - accepted)
    if unexpected:
        raise Unsupported("unknown recipe fields: " + ", ".join(unexpected))
    return {
        "recipe_type": typ,
        "output": {"item": output["item"], "count": count},
        "inputs": combine(ins),
        "catalysts": catalysts,
        "costs": extras,
        "station": typ,
    }

def identity(path, root):
    rel = path.relative_to(root)
    parts = rel.parts
    if "recipes" not in parts:
        raise Unsupported("not inside a recipes directory")
    pos = parts.index("recipes")
    if pos == 0 or pos == len(parts) - 1:
        raise Unsupported("missing recipe namespace or path")
    namespace = parts[pos-1]
    name = "/".join(parts[pos+1:])[:-5]
    if not name or not namespace:
        raise Unsupported("missing recipe id")
    return namespace + ":" + name, rel.as_posix()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="kubejs/data directory of a pinned upstream checkout")
    ap.add_argument("--commit", required=True, help="exact official source commit SHA")
    ap.add_argument("--repository", default="AllTheMods/atm9-expert")
    ap.add_argument("--prefix", default="kubejs/data", help="source path prefix within upstream repository")
    ap.add_argument("--output", type=Path, default=Path("import-preview"))
    args = ap.parse_args()
    if not args.source.is_dir():
        ap.error("source does not exist")
    if args.output.exists() and any(args.output.iterdir()):
        ap.error("output directory is not empty; review/delete old preview first")
    output = args.output
    (output / "recipes").mkdir(parents=True, exist_ok=True)
    by_mod = collections.defaultdict(list)
    skipped = []
    for path in sorted(args.source.rglob("*.json")):
        try:
            recipe_id, rel = identity(path, args.source)
            data = json.loads(path.read_text(encoding="utf-8"))
            record = parse(data)
            source_path = args.prefix.strip("/") + "/" + rel
            record["recipe_id"] = recipe_id
            record["verification"] = {
                "status": "source_parsed", "effective_in_game": False, "pack_version": None}
            record["source"] = {
                "repository": args.repository, "commit": args.commit,
                "path": source_path,
                "url": f"https://github.com/{args.repository}/blob/{args.commit}/{source_path}"
            }
            mod = record["output"]["item"].split(":")[0]
            by_mod[mod].append(record)
        except (Unsupported, ValueError, UnicodeError, OSError) as exc:
            skipped.append({"path": str(path.relative_to(args.source)), "reason": str(exc)})
    for mod, records in sorted(by_mod.items()):
        records.sort(key=lambda r: r["recipe_id"])
        (output / "recipes" / (mod + ".json")).write_text(
            json.dumps({"schema_version": 1, "output_mod": mod, "recipes": records},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "skipped.json").write_text(
        json.dumps(skipped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "SUMMARY.md").write_text(
        "# Import preview (NOT verified)\n\n"
        + f"Parsed JSON recipes: {sum(map(len, by_mod.values()))}\n\n"
        + f"Skipped/unsupported: {len(skipped)}\n\n"
        + "Review skipped.json and compare with in-game JEI before merging into data/recipes.\n",
        encoding="utf-8")
    print(f"parsed={sum(map(len, by_mod.values()))} skipped={len(skipped)} output={output}")

if __name__ == "__main__":
    main()
