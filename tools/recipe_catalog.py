#!/usr/bin/env python3
"""Create mod-sorted Markdown recipe tables from exported JSON (Python 3)."""
import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

def flatten(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return ", ".join(flatten(t) for t in x)
    if isinstance(x, dict):
        if "item" in x:
            return str(x["item"]) + (" x" + str(x["count"]) if x.get("count", 1) != 1 else "")
        if "tag" in x:
            return "#" + str(x["tag"])
        if "fluid" in x:
            return str(x["fluid"]) + " " + str(x.get("amount", "")) + "mB"
        return "; ".join(k + "=" + flatten(v) for k, v in x.items())
    return str(x)

def result_ids(recipe):
    items = []
    for field in ("result", "results", "output", "outputs", "itemOutputs", "item_outputs", "item_output"):
        r = recipe.get(field)
        if r is None:
            continue
        for value in r if isinstance(r, list) else [r]:
            if isinstance(value, str) and ":" in value:
                items.append(value)
            if isinstance(value, dict) and "item" in value:
                items.append(str(value["item"]))
    return sorted(set(items))

def esc(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace(chr(96), "'")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="folder with exported effective recipe JSON files")
    ap.add_argument("--output", type=Path, default=Path("generated-recipes"))
    args = ap.parse_args()
    if not args.source.is_dir():
        ap.error("Source directory not found")
    groups, unclassified = defaultdict(list), []
    count = 0
    for path in sorted(args.source.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError, UnicodeError):
            unclassified.append([str(path), "unreadable"]); continue
        if not isinstance(data, dict) or not isinstance(data.get("type"), str):
            continue
        count += 1
        ids = result_ids(data)
        if not ids:
            unclassified.append([str(path), "item output not identified"])
        for item in ids:
            mod = item.split(":")[0]
            groups[mod].append((item, path.as_posix(), data))
    args.output.mkdir(parents=True, exist_ok=True)
    summary = ["# Mod別アイテムレシピ一覧（自動抽出）", "",
               "このページはJSONの出力を機械抽出した未検証資料です。JEIの全レシピを保証しません。", "",
               "解析したレシピ: " + str(count), "",
               "| Mod ID | 件数 | 一覧 |", "|---|---:|---|"]
    for mod, rows in sorted(groups.items()):
        name = re.sub(r"[^0-9A-Za-z_.-]", "_", mod) + ".md"
        summary.append("| " + mod + " | " + str(len(rows)) + " | [表示](" + name + ") |")
        lines = ["# " + mod + " — アイテムレシピ", "",
                 "| 完成品 | レシピタイプ | 入力・素材 | 追加条件 | ファイル |",
                 "|---|---|---|---|---|"]
        for item, path, data in sorted(rows):
            ins = "; ".join(k + ": " + flatten(data[k]) for k in
                            ("ingredients", "ingredient", "input", "inputs", "pattern",
                             "key", "catalyst", "reagent", "itemInputs", "fluidInputs")
                            if k in data)
            costs = "; ".join(k + ": " + flatten(data[k]) for k in
                              ("mana", "energy", "EUt", "eut", "duration", "time",
                               "processingTime", "temperature") if k in data)
            lines.append("| " + " | ".join(map(esc, [item, data["type"], ins, costs, path])) + " |")
        (args.output / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (args.output / "unclassified.json").write_text(
        json.dumps(unclassified, ensure_ascii=False, indent=2), encoding="utf-8")
    print("recipes:", count, "mods:", len(groups), "unclassified:", len(unclassified))

if __name__ == "__main__":
    main()
