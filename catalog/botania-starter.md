# Botania：具体的レシピ（ソース読取）

[ATM9 Expert公式の固定コミット](https://github.com/AllTheMods/atm9-expert/commit/309d0fa357b00d855f3a50739ae64737f7537936) から読み取った定義です。

> 状態：`parsed`。**実ゲームのJEI有効性は未確認**。ここにないレシピが存在しないという意味ではありません。

## Botania — マナ注入

| 出力 | 入力 | 触媒 | マナ | 出典 |
|---|---|---|---:|---|
| 土 ×2 | 土 ×1 | Conjuration Catalyst | 2,000 | [JSON](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data/botania/recipes/mana_infusion/dirt/dirt_dupe.json) |
| エンドストーン ×2 | エンドストーン ×1 | 同上 | 2,000 | [JSON](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data/botania/recipes/mana_infusion/end_stone/end_stone_dupe.json) |
| ネザーラック ×2 | ネザーラック ×1 | 同上 | 2,000 | [JSON](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data/botania/recipes/mana_infusion/netherrack/netherrack_dupe.json) |
| 黒曜石 ×2 | 黒曜石 ×1 | 同上 | 2,000 | [JSON](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/data/botania/recipes/mana_infusion/obsidian/dirt_dupe.json) |

## GregTech側に実装されたBotania連携

| 出力 | 素材 | 装置・条件 |
|---|---|---|
| Overgrown Plating Casing ×2 | Aluminium Frame ×1、Manasteel Plate ×6、Livingrock ×2、Mana Rune ×2、マナ流体 5,000 mB | Assembler、MV、100 ticks |
| Overgrown Conduit Casing ×2 | Aluminium Frame ×1、Elementium Plate ×8、Livingwood ×4、マナ流体 10,000 mB | Assembler、MV、100 ticks |
| Mana Infuser ×1 | IV Machine Hull ×1、IV Electric Pump ×2、IV Electric Piston ×2、IV回路 ×2、Semi Stable Clathrate Plate ×8、マナ流体 9,200 mB | Assembler、IV、600 ticks |

[公式JSレシピ定義](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/Mods/botania.js)

注意：工業レシピで指定されている流体は `#forge:mana` タグであり、通常のマナプールからの移送・変換が可能かは別途検証してください。
