# 未収録レシピの公式ソース調査・GitHub提出

**目的:** ユーザーが未収録アイテムを質問したら、公式ソースを調べ、確認できた直接レシピを先に部分回答し、データをGitHubへ提出した結果を最終回答で報告する。

**前提:** GitHubに書き込む権限が必要。PRが作れた時点では**mainに登録済みではない**ため、「PR提出済み」と「マージ済み」を区別する。

## AIエージェントの実行手順

1. 対象の厳密なアイテムID（例：`ars_nouveau:novice_spell_book`）を確定。
2. `data/item_index.json` と `data/recipes/<namespace>.json` を検索する。
3. 未収録なら、`data/manifest.json` 内の公式`upstream_repository`と固定`upstream_commit`を用いてGitHub検索する。`kubejs/server_scripts/**/*.js`、`kubejs/data/**/recipes/*.json`、`recipeRemovals.js`、関連設定を調べる。**元のMod標準レシピが削除されている場合、置換レシピを使う**。
4. 固定出典から材料、数、3×3配置、設備、流体・EU、バージョンの条件を読む。単なる検索結果ではなく、必ず原典ファイルを確認。**元データのJavaScriptを実行してはならない**。
5. `source_parsed`（実機未検証）としてDBに記録。保存先は完成品のMod IDに対応する`data/recipes/<namespace>.json`。`source.url`には**固定コミットURL**を記録。
6. `data/item_index.json`を再構築し、`data/manifest.json`の件数・収録範囲を更新。`python tools/recipe_query.py validate` と `python -m unittest discover -s tests`を実行。
7. GitHubに書き込む権限があれば**専用ブランチのPull Requestとして提出する**。PR本文に出典・未検証状態・重要な不明条件を記入。提出に失敗した場合は正直に報告する。PRのマージ前はmain未収録。
8. **根拠が確認できた直接レシピから部分回答してよい。** PR提出や下位素材の全面追跡を待つ必要はない。最終回答ではレシピID、出典、素材、3×3配置、前提素材の作り方と不明点、PRまたはコミットのURL（失敗時は理由）を報告。依存素材も未収録なら、同じ調査手順を可能な範囲で繰り返す。回答を推測で完成させない。

## 公式ソースURLからの取り込み

次のツールは**URL先の内容を検索せずに実行するツールではありません**。AIがまず公式固定コミットのソースを発見し、正しいファイルへのリンクを選ぶ必要があります。

### 方法A：ローカルのPythonツール

次のようにプレビューを取得できます。

```sh
python tools/recover_recipe.py --source-url "https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/Mods/ars.js" --item ars_nouveau:novice_spell_book
```

正常に解析されたことを確認して、作業ブランチでローカルDBへ追加します。

```sh
git switch -c "recipe/recover-my-item"
python tools/recover_recipe.py --source-url "公式の固定コミットURL" --item "namespace:item" --apply
python tools/recipe_query.py validate
python -m unittest discover -s tests
git add data/
git commit -m "data: recover official recipe source"
git push -u origin recipe/recover-my-item
gh pr create --base main --head recipe/recover-my-item --title "Add recovered recipe" --body "Fixed official source; source_parsed, JEI unverified."
```

※ コマンド内の「公式の固定コミットURL」と「namespace:item」は実際の値に差し替えます。既存登録を検出した場合は変更しません。

### 方法B：GitHub Actions（フォームからPR作成）

GitHub Actionsの **Recover missing recipe from official source** を開いて**Run workflow**を選び、`source_url`（公式固定コミットのレシピファイルURL）と`item_id`（完成品ID）を入力します。

対応形式であればレシピを読み取り、DB・索引・件数を更新してテストし、成功時に専用ブランチとPRを作ります。**GitHub ActionsによるPR作成をリポジトリ設定で許可している必要があります**。対応していない定義は安全のため失敗して追加しません。

### 方法C：GitHubアプリを使えるAIエージェント

- GitHubの`search`や`fetch`で、まず公式固定ソースのレシピを検証する。
- `create_branch`で専用ブランチを作り、`create_file`・`update_file`でMod別データ、索引、manifestを更新する。
- CIの結果を確認し、`create_pull_request`で提出する。
- PR URLをユーザーに提示し、**未マージの状態を登録完了と偽らない**。
- 書込み権限がない場合は、必要な権限と提出可能な変更案を示す。回答できる確定した工程は出典とともに伝える。

## 自動解析の対応範囲

`tools/recover_recipe.py` が自動解析できるのは単純なKubeJS `allthemods.shaped('...', [...], {...}).id('...')` の**固定リテラル**と、`tools/import_json.py`が対応する一部JSONのみです。変数、条件分岐、ループ、GregTechの機械レシピなどは手動で解釈・検証してください。

公式ソースにアイテムが見つからない場合は、同じATM9 Expertバージョンに含まれるModのjar内 `data/<modid>/recipes` 等まで調査します。他のModpackのレシピをATM9 Expertに転用してはいけません。

このデータベースは**部分的な収録**です。データがない＝作れない、ではありません。公式ソースの記述があっても実際のゲームで有効なレシピである保証はなく、最終確認はJEI/EMIで行います。
