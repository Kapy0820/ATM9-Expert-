# レシピの具体的な記載とMod別自動生成

このリポジトリの既存 `RECIPE_INDEX.md` は公式KubeJSの**ソースファイル索引**であり、素材・完成個数を列挙した全アイテムレシピ一覧ではありません。

## 実際のレシピ表

- [Botaniaの確実に読み取れる定義の例](catalog/botania-starter.md)
- [ソースファイル索引](RECIPE_INDEX.md)

## JSONをMod別のレシピ表に変換

1. 対象のATM9 Expertバージョンを固定する（公式GitHubのmainは更新される）。
2. 実ゲームのレシピJSONをエクスポートしてフォルダに保存する。KubeJSの `/kubejs export` は導入バージョンによって操作が異なる可能性があるため、コマンド補完と生成先を確認する。
3. 次をPython 3で実行する。

       python tools/recipe_catalog.py "エクスポートしたJSONのフォルダ" --output generated-recipes

4. `generated-recipes/README.md` を開くと完成品のMod IDごとに分類される。

**重要:** このスクリプトはエクスポートされたJSONを整形するだけであり、KubeJS JavaScriptの実行やレシピの有効性検査は行わない。Mod本体のJSONだけではKubeJSによる削除・上書き後の最終レシピはわからない。GregTech特殊レシピ、JEIの仮想レシピ、クラフト不可能なアイテム、タグ解決、流体の入力・確率出力は別途検証する。

## 記入項目

完成品ID、完成個数、素材ID、素材数、流体、機械・設備、EU/t、時間、研究・次元などの条件、出典、確認バージョン。

`source-only`（リンクのみ）、`parsed`（定義抽出）、`verified`（JEIで実機確認）を混同しない。
