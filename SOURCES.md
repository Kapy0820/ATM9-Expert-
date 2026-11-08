# レシピ取得元一覧・AI向け検索順序（必読）

**取得元の正本:** [AllTheMods/atm9-expert](https://github.com/AllTheMods/atm9-expert)  
**現時点で固定した公式ソースのコミット:** [309d0fa357](https://github.com/AllTheMods/atm9-expert/commit/309d0fa357b00d855f3a50739ae64737f7537936)

このファイルは、人間とAIエージェントの**共通の検索地図**です。機械可読版は [data/source_registry.json](data/source_registry.json)。
注意：現在の固定コミットはパックの**配布版と完全一致することが未検証**です。公式`main`の最新版へ勝手に切り替えないでください。

## 取得元の一覧と「参照する順序」

| 順序 | データベース・資料 | 直接リンク | 何を確認するか |
|---:|---|---|---|
| 1 | パック版と収録範囲 | [manifest](data/manifest.json) | 使用中のパックと固定コミットが一致するか |
| 2 | 完成品ID索引 | [item_index](data/item_index.json) | `namespace:item`が登録済みか |
| 3 | Mod別レシピ本体 | [data/recipes](data/recipes) | 入力・数量・製法・全候補・出典・検証状態 |
| 4 | 公式KubeJSの削除・上書き | [recipeRemovals.js](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/recipeRemovals.js) | 既存レシピの廃止・置換の有無 |
| 5 | 公式KubeJSのJavaScript | [server_scripts](https://github.com/AllTheMods/atm9-expert/tree/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts) | 新規・改変・動的なクラフト/機械レシピ |
| 6 | 公式KubeJSのレシピJSON | [kubejs/data](https://github.com/AllTheMods/atm9-expert/tree/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data) | JSONによるレシピ定義 |
| 7 | 対象Modのjar内部 | 使用中パックの`mods/*.jar` | KubeJSにない標準Modレシピ（**同じModバージョンを必須とする**） |
| 8 | 同じバージョンのMod公式ソース（GTCEu 7.5.3） | [公式GTCEu 7.5.3ソース](https://github.com/GregTechCEu/GregTech-Modern/tree/91a79b8a7a2b62ec6277423e6c0ded4af89a831e) | Javaで生成されるGregTech標準機械レシピとLV素材マッピング。対象Modの同一バージョンに限る |
| 9 | クエスト・進行情報 | [FTB Quests](https://github.com/AllTheMods/atm9-expert/tree/309d0fa357b00d855f3a50739ae64737f7537936/config/ftbquests/quests/chapters) | 技術段階・前提クエストのヒント（レシピの証拠ではない） |
| 10 | 実ゲーム | 同じ配布版のJEI/EMI・製造成功 | レシピが実際に有効か、最終確認 |

**実行順序**と**証拠の信頼性**を混同しないでください。最も信頼できるのは対象の配布版で検証した`verified`情報です。ソースに書かれていてもゲーム内で有効とは限りません。

## 未収録アイテムを検索する具体的な順序

1. **完成品の正確なID**を把握する（`modid:registry_name`）。名称だけで検索すると別Modの同名アイテムを拾いやすい。
2. [item_index.json](data/item_index.json)を検索。登録されていれば`data/recipes/<完成品modid>.json`へ。
3. 未登録なら[recipeRemovals.js](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/recipeRemovals.js)で削除・置換を確認。**レシピID≠アイテムID**に注意。
4. [server_scripts](https://github.com/AllTheMods/atm9-expert/tree/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts)のJSを完成品IDで検索。GregTech連携では`Gregification/Mods/`や`Gregification/`を優先して開く。ただしMod固有のコードが別のディレクトリにあることもある。
5. [kubejs/data](https://github.com/AllTheMods/atm9-expert/tree/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data)内の`<レシピ定義namespace>/recipes/**/*.json`を調べる。**出力アイテムのnamespaceとレシピnamespaceは一致しない場合がある**。
6. それでも見つからなければ**使用中パックのMod jar標準データ**を調べる。対象バージョンが確認できない場合は一致と断言しない。
7. jarの中のJSONがない動的生成標準レシピについては、対象Modの同一タグ（例：[GTCEu 7.5.3](https://github.com/GregTechCEu/GregTech-Modern/tree/91a79b8a7a2b62ec6277423e6c0ded4af89a831e)）のJavaソースも調べる。
8. ゲーム内JEI/EMIとクエストを照合。参照したスクリプトに削除・上書き・条件分岐があれば不確定要素として記録。
9. 出典の固定コミットURLからレシピを回収し、[RECOVERY.md](docs/RECOVERY.md)に従ってGitHub PR提出。提出状況を報告してから、**確認できた部分のみ**の材料→工程→不足部分を説明する。

## 最初に開く公式の具体例

- [Ars Nouveauスペルブック](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/Mods/ars.js#L323-L354)：初級・中級・上級の改変クラフト。
- [GregTech Blank Blueprint](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/miscItems.js#L378-L387)：材料、Assembler、流体インク、LV。
- [Powah Dry Ice](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data/powah/recipes/energizing/dry_ice/2x_dry_ice.json)：エネルギー投入レシピのJSON。
- [Ars Nouveauクエスト](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/config/ftbquests/quests/chapters/ars_nouveau.snbt)：入手・進行状況の参考。

## 回答に最低限必要なもの

**対象:** アイテムIDと必要数 / **製法:** 3×3配置や機械 / **入力:** 個数とタグ / **加工コスト:** マナ・EU・流体・時間（実際に原典が示すものだけ） / **前提:** 作れる・未収録・要入手を区別 / **出典:** 固定リンク / **検証:** source_parsedまたはverified / **提出:** main反映・未マージPR・失敗のどれか

名前や素材が不明な場合は推測で埋めず、**部分手順**として答えます。参照できなかったことと、アイテムが作れないことは別です。
