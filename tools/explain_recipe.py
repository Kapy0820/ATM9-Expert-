#!/usr/bin/env python3
"""Print a source-cited Japanese recipe procedure from the local JSON database.

The report is deliberately partial when the dependency graph or provenance is
not verified. Uses recipe_query.plan(); no external service or Mod assumptions.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe_query

ROOT = Path(__file__).resolve().parents[1]
STATUS = {
    "source_parsed": "公式ソースから抽出・実ゲーム未検証",
    "verified": "対象パック版で実機確認済み",
}
REASONS = {
    "recipe_not_in_database_not_proof_of_unobtainability": "入手・クラフト経路がこのDBに未収録（作成不可能という意味ではない）",
    "tag_requires_concrete_item_resolution": "タグに該当する具体的なアイテムは未確定",
    "multiple_recipe_options_choose_one_explicitly": "複数の製法があり、選択を要する",
    "alternative_ingredients_unresolved": "素材の選択肢が未確定",
    "self_referential_recipe_requires_initial_seed_and_sequential_crafts": "同じアイテムを材料に使う増殖レシピで初期素材が必要",
    "cycle_or_self_duplication_requires_seed": "材料に循環があり初期素材が必要",
    "invalid_recipe_choice": "指定されたレシピIDが見つからない",
}

def ingredient_name(choice):
    if "item" in choice:
        return choice["item"]
    if "tag" in choice:
        return "#" + choice["tag"] + "（タグ条件）"
    return json.dumps(choice, ensure_ascii=False)

def ingredient_text(ing):
    options = [ing["choice"]] if "choice" in ing else ing.get("choices", [])
    return " または ".join(ingredient_name(c) for c in options) + " ×" + str(ing["count"])

def source_link(info):
    url = info.get("url", "")
    return "[" + info.get("path", "公式ソース") + "](" + url + ")" if url else "出典未登録"

def render(report, manifest):
    target = report["requested"]
    out = [
        "# 製作手順の調査: " + target["item"] + " ×" + str(target["count"]),
        "",
        "- パック: " + manifest.get("modpack", "不明"),
        "- 対象配布版: " + manifest.get("pack_version", "未検証"),
        "- 公式ソース固定コミット: " + manifest.get("upstream_commit", "不明"),
        "- レシピ網羅性: **部分的**。未収録は作成不可能を意味しません。",
        "- 判定: " + ("**部分手順**（未確認項目あり）" if report["status"] == "partial" else
                    "**記録済みの依存関係を辿った結果**（機械や実ゲームの最終確認は別途必要）"),
        "",
    ]
    if report["steps"]:
        out += ["## 確認できた作業（材料側から順に表示）", ""]
    else:
        out += ["## このDBでは製作手順を確定できません", ""]
    for i, step in enumerate(report["steps"], 1):
        out += ["### " + str(i) + ". " + step["output_item"], "",
                "- レシピID: " + step["recipe_id"],
                "- 製造設備: " + str(step.get("station") or "未確認"),
                "- 生産数: " + (str(step.get("produced_count")) if step.get("produced_count") is not None else "要検証"),
                "- 必要な製作回数: " + (str(step.get("crafts")) if step.get("crafts") is not None else "循環のため未確定"),
                "- 素材: " + (" / ".join(ingredient_text(x) for x in step["consumed_inputs"]) or "なし（要検証）"),
                "- 触媒・使い回し: " + (" / ".join(ingredient_name(x) for x in step.get("reusable_catalysts", [])
                    if "item" in x or "tag" in x) or
                    ", ".join(c.get("block", "特殊触媒") for c in step.get("reusable_catalysts", [])) or "ソースに記載なし"),
                "- コスト（1製作あたり、ソース定義値）: " +
                    (json.dumps(step.get("costs_per_craft"), ensure_ascii=False) if step.get("costs_per_craft") else "記載なし"),
                "- 確認状況: " + STATUS.get(step["verification"].get("status"), "不明"),
                "- 出典: " + source_link(step["source"]),
                ""]
        pattern = step.get("crafting_pattern")
        if pattern:
            out += ["**3×3の配置（上段→下段）**", "", "~~~text", *pattern, "~~~", "",
                    "配置の対応:"]
            for key, val in sorted((step.get("pattern_key") or {}).items()):
                out.append("- " + key + " = " + ingredient_name(val))
            out.append("")
        if step.get("warning"):
            out.append("**注意:** " + step["warning"] + "\n")
    if report.get("provided_by_user"):
        out += ["## 手持ちとして扱った素材", ""]
        for obj in report["provided_by_user"]:
            out.append("- " + obj["item"] + " ×" + str(obj["count"]))
        out.append("")
    if report["unresolved"]:
        out += ["## 未解決・追加調査が必要な項目", ""]
        for missing in report["unresolved"]:
            k = missing.get("item", "#" + missing.get("tag", "不明"))
            line = "- " + k + " ×" + str(missing.get("count", "不明")) + "：" + REASONS.get(
                missing["reason"], missing["reason"])
            out.append(line)
            if missing.get("available"):
                out.append("  候補: " + ", ".join(missing["available"]))
        out.append("")
    out += [
        "## 次に調べる先", "",
        "未解決素材がある場合は [SOURCES.md](../SOURCES.md) に定めた順番で、",
        "既存索引 → 公式recipeRemovals → KubeJS JS → KubeJS JSON → 対象版のMod標準レシピ → JEI/EMI を照合。",
        "[RECOVERY.md](../docs/RECOVERY.md) に従って公式固定リンクとともにPR提出し、",
        "提出・未検証状態を明記してください。",
    ]
    return "\n".join(out).replace("\n 未解決素材", "\n未解決素材") + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("item", help="exact output ID, for example ars_nouveau:apprentice_spell_book")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--choose", action="append", default=[], metavar="ITEM=RECIPE_ID")
    parser.add_argument("--have", action="append", default=[], metavar="ITEM")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be >= 1")
    chosen = {}
    for term in args.choose:
        if "=" not in term:
            parser.error("--choose must be ITEM=RECIPE_ID")
        key, val = term.split("=", 1)
        chosen[key] = val
    report = recipe_query.plan(recipe_query.read_db(args.data), args.item, args.count, chosen, set(args.have))
    manifest = json.loads((args.data / "manifest.json").read_text(encoding="utf-8"))
    print(render(report, manifest))

if __name__ == "__main__":
    main()
