#!/usr/bin/env python3
"""Recover one explicitly requested recipe from a pinned, trusted upstream GitHub URL.

Supports simple KubeJS .shaped('item', [...], {...}).id('...') and a small
set of JSON recipe types recognized by import_json.py. No JavaScript execution.
By default it ONLY prints a preview; --apply writes to the local checkout.
Submission to GitHub is handled by the calling agent/gh CLI, not silently done.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from import_json import parse as parse_json, Unsupported
from recipe_query import read_db, index_from_db, checks

REPO_ROOT = HERE.parent
GITHUB_PATH = re.compile(r"^/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/blob/([0-9a-fA-F]{40})/(.+)$")
ITEM_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
STRING = r"'([^'\\\n]*)'"
SHAPED = re.compile(
    r"allthemods\.shaped\(\s*'(?P<out>[^'\\\n]+)'\s*,"
    r"\s*\[(?P<grid>(?:\s*'[^'\\\n]*'\s*,?){1,3})\s*\]\s*,"
    r"\s*\{(?P<keys>(?:\s*[A-Za-z]:\s*'[^'\\\n]+'\s*,?)+)\s*\}\s*\)"
    r"\s*\.id\(\s*'(?P<rid>[^'\\\n]+)'\s*\)",
    re.DOTALL
)
KEY = re.compile(r"([A-Za-z]):\s*'([^'\\\n]+)'")
ROW = re.compile(r"'([^'\\\n]*)'")

def parse_url(url, manifest):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise ValueError("Only HTTPS github.com source blob URLs are allowed")
    m = GITHUB_PATH.fullmatch(parsed.path)
    if not m:
        raise ValueError("Expected https://github.com/OWNER/REPO/blob/<40-character commit>/PATH")
    owner, name, commit, path = m.groups()
    repo = f"{owner}/{name}"
    if repo != manifest["upstream_repository"]:
        raise ValueError("The URL must refer to the official upstream repository in manifest")
    if commit.lower() != manifest["upstream_commit"].lower():
        raise ValueError("Source commit does not match data/manifest.json; review version before updating")
    if (path.startswith("/") or ".." in path.split("/") or
            not (path.startswith("kubejs/data/") or path.startswith("kubejs/server_scripts/"))):
        raise ValueError("Unsupported or unsafe source path")
    if not (path.endswith(".json") or path.endswith(".js")):
        raise ValueError("Only recipe JSON and KubeJS JavaScript supported")
    return repo, commit, path

def safe_fetch(repo, commit, path):
    owner, name = repo.split("/")
    raw = f"https://raw.githubusercontent.com/{owner}/{name}/{commit}/{path}"
    request = urllib.request.Request(raw, headers={"User-Agent": "ATM9-Expert-Recipe-Collector/1"})
    with urllib.request.urlopen(request, timeout=20) as stream:
        content = stream.read(2_000_001)
    if len(content) > 2_000_000:
        raise ValueError("Source too large")
    return content.decode("utf-8")

def atom(value):
    if value.startswith("#"):
        return {"tag": value[1:]}
    if not ITEM_ID.fullmatch(value):
        raise ValueError("Unsupported literal recipe ingredient: " + value)
    return {"item": value}

def parse_shaped_js(source):
    recipes = []
    for m in SHAPED.finditer(source):
        output, rid = m.group("out"), m.group("rid")
        if not ITEM_ID.fullmatch(output) or not ITEM_ID.fullmatch(rid):
            continue
        rows = ROW.findall(m.group("grid"))
        if not 1 <= len(rows) <= 3 or any(len(row) != 3 for row in rows):
            continue
        keys = dict(KEY.findall(m.group("keys")))
        if not keys:
            continue
        symbols = Counter("".join(rows).replace(" ", ""))
        if any(c not in keys for c in symbols):
            continue
        inputs = []
        for symbol, count in sorted(symbols.items()):
            try:
                choice = atom(keys[symbol])
            except ValueError:
                inputs = []
                break
            inputs.append({"choice": choice, "count": count})
        if not inputs:
            continue
        recipes.append((
            m.start(),
            m.end(),
            {
                "recipe_id": rid,
                "recipe_type": "minecraft:crafting_shaped",
                "output": {"item": output, "count": 1},
                "inputs": inputs,
                "catalysts": [],
                "costs": {},
                "station": "Crafting Table (3x3)",
                "crafting_pattern": rows,
                "pattern_key": {k: atom(v) for k, v in keys.items()},
            }
        ))
    return recipes

def extract(source, item, repo, commit, path):
    if not ITEM_ID.fullmatch(item):
        raise ValueError("Use a full item ID such as ars_nouveau:novice_spell_book")
    if path.endswith(".js"):
        candidates = parse_shaped_js(source)
        selected = []
        for start, end, r in candidates:
            if r["output"]["item"] != item:
                continue
            first = source.count("\n", 0, start) + 1
            last = source.count("\n", 0, end) + 1
            selected.append((r, first, last))
    else:
        raw = json.loads(source)
        r = parse_json(raw)
        if r["output"]["item"] != item:
            raise ValueError("The JSON output does not match the requested item")
        if "/recipes/" not in path:
            raise ValueError("Not an upstream recipe JSON path")
        ns = path.split("/recipes/")[0].split("/")[-1]
        recipe_path = path.split("/recipes/", 1)[1]
        r["recipe_id"] = ns + ":" + recipe_path[:-5]
        selected = [(r, None, None)]
    if not selected:
        raise ValueError("No safely parseable recipe for this item at that source URL")
    records = []
    for r, first, last in selected:
        source_info = {
            "repository": repo,
            "commit": commit,
            "path": path,
            "url": f"https://github.com/{repo}/blob/{commit}/{path}"
        }
        if first is not None:
            source_info["url"] += f"#L{first}-L{last}"
            source_info["line_start"] = first
            source_info["line_end"] = last
        r["source"] = source_info
        r["verification"] = {
            "status": "source_parsed", "effective_in_game": False, "pack_version": None
        }
        records.append(r)
    return records

def apply(records, checkout):
    dbdir = checkout / "data"
    db = read_db(dbdir)
    by_mod = {}
    added = []
    for r in records:
        target = r["output"]["item"]
        # Check for duplicated IDs anywhere, so merging multiple sources is safe.
        for rs in db.values():
            for old in rs:
                if old["recipe_id"] == r["recipe_id"]:
                    if old["output"]["item"] != target:
                        raise ValueError("Conflicting recipe ID found: " + r["recipe_id"])
                    if old == r:
                        continue
                    raise ValueError("Recipe already exists and differs: inspect manually: " + r["recipe_id"])
        if any(old["recipe_id"] == r["recipe_id"] for old in db.get(target, [])):
            continue
        db[target].append(r)
        by_mod.setdefault(target.split(":")[0], []).append(r)
        added.append(r["recipe_id"])
    if not added:
        return []
    # Write only the output mods affected; other records stay byte-for-byte semantically intact.
    for mod in sorted(by_mod):
        contents = []
        for output, rs in db.items():
            if output.startswith(mod + ":"):
                contents.extend(rs)
        contents.sort(key=lambda x: x["recipe_id"])
        outfile = dbdir / "recipes" / f"{mod}.json"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(
            json.dumps({"schema_version": 1, "output_mod": mod, "recipes": contents},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dbdir / "item_index.json").write_text(
        json.dumps(index_from_db(db), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = dbdir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["recipe_count"] = sum(map(len, db.values()))
    manifest["unique_output_items"] = len(db)
    manifest["coverage"] = "PARTIAL: source-parsed recipe definitions; NOT complete"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    problems = checks(read_db(dbdir), dbdir)
    if problems:
        raise ValueError("Post-import validation failed; inspect working tree: " + "; ".join(problems))
    return added

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", required=True, help="pinned official GitHub file URL")
    parser.add_argument("--item", required=True, help="exact output namespace:item")
    parser.add_argument("--source-file", type=Path, help="local copy for offline/tests; must match linked source")
    parser.add_argument("--apply", action="store_true", help="write local checkout; default preview only")
    parser.add_argument("--checkout", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    manifest = json.loads((args.checkout / "data" / "manifest.json").read_text(encoding="utf-8"))
    repo, commit, path = parse_url(args.source_url, manifest)
    source = args.source_file.read_text(encoding="utf-8") if args.source_file else safe_fetch(repo, commit, path)
    records = extract(source, args.item, repo, commit, path)
    if args.apply:
        print(json.dumps({"added": apply(records, args.checkout), "unverified": True}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"preview": records, "not_saved": True, "unverified": True}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
