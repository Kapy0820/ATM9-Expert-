# 動作試験：Ars Nouveau「Apprentice Spell Book」

**対象:** `ars_nouveau:apprentice_spell_book` ×1  
**ソース:** [公式固定コミット](https://github.com/AllTheMods/atm9-expert/commit/309d0fa357b00d855f3a50739ae64737f7537936)  
**検証状態:** `source_parsed`（配布版JEIでの有効性は未確認）。

## 実行したレシピ調査コマンド

```sh
python tools/recipe_query.py lookup ars_nouveau:apprentice_spell_book
python tools/recipe_query.py plan ars_nouveau:apprentice_spell_book --count 1
python tools/explain_recipe.py ars_nouveau:apprentice_spell_book --count 1
python tools/recipe_query.py validate
python -m unittest discover -s tests
```

## AIが出すべき部分手順

1. **Blank Blueprint ×6**：GTCEu Assemblerで1枚ずつ製造する定義。各1枚につき、`#forge:paper` ×4・`#forge:small_dusts/lapis` ×1・`#forge:ink` 144mB、LV、600ticks。6枚なら材料の必要合計は紙タグ24・lapis small dustタグ6・ink 864mB、加工は合計6回（単一装置なら600×6 ticks）。[公式コード](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/miscItems.js#L378-L387)
2. **Novice Spell Book ×1**：3×3`PSP / PBP / PMP`、P=Blank Blueprint、S=Source Gem、B=`#forge:books`、M=Mana Rune。[公式コード](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/Mods/ars.js#L323-L332)
3. **Apprentice Spell Book ×1**：3×3`PSP / PBP / PMP`、P=`#forge:plates/manasteel` ×6、S=Eye of Ender、B=Novice Spell Book、M=`bloodmagic:demonslate`。[公式コード](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/Gregification/Mods/ars.js#L334-L343)

**未解決：** Source Gem・Mana Rune・Ender Eye・Demon Slateの製法/入手手段、paper/lapis/ink/manasteel plate/booksタグの具体化、Assembler自体の製造・電力供給、実機での改変レシピ有効性。すべて**ソースに明示されている範囲だけ**を確定扱いし、残りは[SOURCES.md](../SOURCES.md)から再検索する。

このテストは「データがある工程を提示できるか」を確認するもので、**全素材が揃うまでの完全攻略を保証しない**。

## CIの検証項目

- `source_registry.json` の参照順と公式コミットの固定。
- 出典URL・材料・作業台の配置の正確な表示。
- 素材依存の順序：Blank Blueprint → Novice → Apprentice。
- 未収録素材の明示。
- 候補製法が複数ある場合は勝手に決定しない。
