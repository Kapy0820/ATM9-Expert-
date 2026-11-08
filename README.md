# ATM9 Expert 攻略ナレッジベース（AIエージェント対応）

このリポジトリは、コミュニティのプレイヤーやAIエージェントが、**特定アイテムの製作レシピとその出典**を安全に調べるための資料です。

## AIエージェントの調べ方

1. **[AGENTS.md](AGENTS.md)を必ず読む。** 推測で手順を補完しない。
2. [data/manifest.json](data/manifest.json) で収録範囲・固定コミット・実機検証状態を確認。
3. [data/item_index.json](data/item_index.json) で `modid:item_name` を検索。
4. 該当する [data/recipes](data/recipes) のJSONから、完成品の数量・入力・触媒・必要エネルギー・原典URLを読む。
5. 必要な前提素材を `tools/recipe_query.py` でたどる。未収録の素材やループがあれば**部分手順**として報告する。

## 収録状況

現在は公式KubeJS JSONから直接転記した **24レシピ定義**を機械可読で収録しています。対象はBotaniaのMana Infusion（12件）とPowahのEnergizing（12件）です。分類は**完成品のMod ID**基準なので、例えばPowahで作るAE2アイテムは `data/recipes/ae2.json` に入ります。

**これはATM9 Expert全アイテムの製作レシピ集ではありません。** 元データは公式GitHubの固定コミット `309d0fa357b00d855f3a50739ae64737f7537936`であり、配布版との完全一致やJEI上の有効性は未確認（`source_parsed`）です。レシピが見つからなくても「作れない」という意味ではありません。

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
