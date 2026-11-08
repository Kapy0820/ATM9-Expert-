# ATM9 Expert 攻略ナレッジベース（AIエージェント対応）

このリポジトリは、コミュニティのプレイヤーやAIエージェントが、**特定アイテムの製作レシピとその出典**を安全に調べるための資料です。

## AIエージェントはまずここを開く

1. **[SOURCES.md：公式取得元データベース一覧・調査の優先順序](SOURCES.md)**
2. [data/source_registry.json：機械可読の参照元一覧](data/source_registry.json)
3. [AGENTS.md：調査・提出・回答の規則](AGENTS.md)

## AIエージェントの調べ方

1. **[SOURCES.md](SOURCES.md)→[AGENTS.md](AGENTS.md)を必ず読む。** 推測で手順を補完しない。
2. [data/manifest.json](data/manifest.json) で収録範囲・固定コミット・実機検証状態を確認。
3. [data/item_index.json](data/item_index.json) で `modid:item_name` を検索。
4. 該当する [data/recipes](data/recipes) のJSONから、完成品の数量・入力・触媒・必要エネルギー・原典URLを読む。
5. 必要な前提素材を `tools/recipe_query.py` でたどる。**未収録なら公式ソースから検索・回収し、GitHubへ提出してから回答する。** 未確認の工程は部分手順とする。

## 未収録アイテムを自動で補完する

- [未収録時のAIエージェント手順](docs/RECOVERY.md)：公式コミットを検索→定義を取得→解析→GitHub PRへ提出→出典付きで回答。
- [ソースURLからレシピを回収](tools/recover_recipe.py)：固定GitHub URLを指定してプレビューまたはDBに追加。JSの単純なshapedレシピと一部JSONのみ対応。
- [GitHub Actionsでレシピ追加PRを作成](.github/workflows/recover-recipe.yml)：Actionsの **Run workflow** に原典URL・完成品IDを入力。GitHub設定によりPR作成許可が必要。

**注意：** 自動で何でも作成手順が判明するわけではありません。動的生成・機械加工・Mod標準レシピは別途調査し、未確認なら未確認と明記します。GitHubへの反映には書込権限が必要です。

## 収録状況

現在は公式KubeJSから取得した **28レシピ定義**を機械可読で収録しています。Botania Mana Infusion（12件）、Powah Energizing（12件）、Ars Nouveauの3種スペルブック（3件）、GregTech Blank Blueprint（1件）です。分類は**完成品のMod ID**基準なので、例えばPowahで作るAE2アイテムは `data/recipes/ae2.json` に入ります。

**これはATM9 Expert全アイテムの製作レシピ集ではありません。** 元データは公式GitHubの固定コミット `309d0fa357b00d855f3a50739ae64737f7537936`であり、配布版との完全一致やJEI上の有効性は未確認（`source_parsed`）です。レシピが見つからなくても「作れない」という意味ではありません。

## AIが日本語で手順を返すための最短ルート

```sh
python tools/explain_recipe.py ars_nouveau:apprentice_spell_book
```

3×3の配置、依存素材、設備、根拠リンク、未確認事項を**出典付きのMarkdown**で表示します。これを他AIの回答の下書きとして利用し、未収録の材料は[SOURCES.md](SOURCES.md)の順番で追加調査してください。

## ローカルでの検索（Python 3、外部ライブラリ不要）

```sh
python tools/recipe_query.py lookup powah:dry_ice
python tools/recipe_query.py plan powah:dry_ice --count 4
python tools/recipe_query.py lookup minecraft:dirt
python tools/recipe_query.py plan minecraft:dirt --count 16
python tools/recipe_query.py validate
```

複数の作り方がある場合、勝手に一つを選びません。例：

```sh
python tools/recipe_query.py plan powah:dry_ice --count 4 --choose powah:dry_ice=powah:energizing/dry_ice/2x_dry_ice
```

## コミュニティでのデータ拡張

[docs/IMPORT.md](docs/IMPORT.md) の仕様に従って`data/recipes/<出力Mod>.json`へ追加した後、`python tools/recipe_query.py rebuild-index`で索引を更新してください。変更のたびに`validate`で整合性を確認します。

旧`catalog/`や`recipes/`のソースリンク集・Markdown生成物は、AIが未検証の情報を完成レシピと誤認しないよう整理しました。公式の一次資料は各レシピの `source.url` から参照できます。

## レシピの取り込みを拡張する

[保守的なJSONインポーター](tools/import_json.py)を利用できます。サポートする形式のみを取り込み、特殊なMod形式は`skipped.json`へ理由付きで残します。インポートしたレシピは自動的に`verified`になりません。コマンド例は[追加ガイド](docs/IMPORT.md)を参照してください。
