# レシピ検索の高速化：先に索引・直リンクを使う

## 問題（2026-11-08のLV Assemblerテストより）

前回は`gtceu:lv_assembler`が自前DBに未収録だったため、一般的な`assembler`検索を繰り返した。しかし**GregTechの機械レシピはJavaコードで電圧段階ごとに生成される**。完成品IDの文字列がソースファイルに直接書かれていなくても、`GTMachines.ASSEMBLER`で原典を特定できる。加えて下位部品を大量に検索し、PR・テスト・追記を同じ要求に含めたことで余計な往復が生じた。

この問題を避けるための機械可読ルートは [data/search_routes.json](../data/search_routes.json)。確認されたソースのみの「近道」であり、ゲームで有効なレシピである証明ではない。

## 最短の問い合わせ手順

| 段階 | やること | 停止条件 |
|---|---|---|
| 1 | [manifest](../data/manifest.json)で公式ソースコミットを確認し、[item_index](../data/item_index.json)に厳密IDを問い合わせる | 既に登録済みなら原典へ直接 |
| 2 | 未収録なら**既存の未マージPRも一度確認**（同じアイテムを重複調査・提出しない） | 対象の既存PRに確認可能なレシピがあれば新規の広域検索不要 |
| 3 | [search_routes.json](../data/search_routes.json)を検索。対象Mod・アイテム種別ごとの**固定原典リンク**を先に開く | 近道で原典と材料が確定したら広域検索を終了 |
| 4 | パック側の[recipeRemovals](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/recipeRemovals.js)・KubeJS・CraftingComponent変更の影響を確認する | 出典の競合・削除がないか判断 |
| 5 | 直リンクにない場合は固定コミットの正確なパスを特定して読む。汎用コード検索は**具体的な記号名・完成品ID**を使い、広すぎるキーワードを連発しない | 2回の広域検索でも不明なら検索場所自体を変える |
| 6 | 完成品の材料・配置と**直下の部品**をまず答える。必要なら依存を1階層ずつ追加 | 部分手順なら不足を明記 |
| 7 | 未収録の正確な事実をまとめて**1件のPRに一括提出**し、原則1回のCIで確認 | さらに深い枝は別の調査へ。PR未マージを明示 |

**注意**：GitHubの`search`はデフォルトブランチを検索するため、検索結果をそのまま固定コミットの証拠として使わないこと。見つけたファイルは必ず`fetch_file(ref=<固定コミット>)`またはコミット付きrawリンクで再確認する。

## GregTech専用の最短ルート

1. **正確な対象**：例`gtceu:lv_assembler`（「Assemblerで加工するレシピ」ではなく「Assemblerそのもののクラフト」）。
2. **ATM9 ExpertのModバージョン**：[modlist.json](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/config/crash_assistant/modlist.json)で`gtceu-1.20.1-7.5.3.jar`を特定する。これは配布版と同じであるとは未検証。
3. **Mod原典の固定先**：[GTCEu 7.5.3](https://github.com/GregTechCEu/GregTech-Modern/commit/91a79b8a7a2b62ec6277423e6c0ded4af89a831e)。[MetaTileEntityLoader.java（機械レシピ生成）](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/MetaTileEntityLoader.java#L781-L785)の`GTMachines.ASSEMBLER`を開く。
4. **電圧別材料の解決**：[GTCraftingComponents.java](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/GTCraftingComponents.java)の`LV`行だけを読む。必要があれば[ComponentRecipes.java](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/ComponentRecipes.java)の`robot_arm_lv`等へ。
5. **パック側の上書き確認**：[recipeRemovals.js](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/recipeRemovals.js)と[customComponents.js](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/startup_scripts/customComponents.js)を確認。Source-definedの状態ならJEI未検証を明記する。

### 繰り返さない検索例

- **NG**：`assembler`を繰り返し検索し、Assemblerを**使う**レシピを何十件も読む。
- **NG**：`gtceu:lv_assembler`の文字列が見つからないだけで、レシピが存在しないと結論づける。
- **OK**：`gtceu:lv_assembler` → `lv`＋機械種`assembler` → `GTMachines.ASSEMBLER` → `GTCraftingComponents`。
- **OK**：未解決の材料はその場で明記し、依存の無限追跡や、原典が未確認の材料数を回答に混ぜない。

## GitHub提出とユーザー回答を分離する

以前の運用では、**一つのレシピ質問の途中で、最終素材の調査、索引更新、複数回コミット、PR、CIまで必須**に見えた。今後は、**直接レシピの根拠が取れた段階で、まず材料・作り方の部分回答**を提示してよい。その後に提出処理をまとめ、成功したPR/コミットURLを追加して最終報告する。

未収録データの提出はこれまでどおり試みるが、**根拠のある回答を、独立した下位素材が全て登録されるまで不必要に遅らせない**。PRの未マージ状態や実機未検証は必ず表示する。
