# LV Assembler（GTCEu Modern 7.5.3）公式ソースに基づく製作候補

> **source_parsed / ゲーム内未検証**。ATM9 Expertの固定ソース [309d0fa35](https://github.com/AllTheMods/atm9-expert/commit/309d0fa357b00d855f3a50739ae64737f7537936) に付属するmodlistはGTCEu 7.5.3を示す。ただし配布版との完全一致は未検証。

## LV Assemblerの直接レシピ

完成品：`gtceu:lv_assembler` ×1、設備：作業台。

```text
A C A
V M V
W C W
```

| 記号 | 素材 | 数 |
|---|---|---:|
| A | `gtceu:lv_robot_arm` | 2 |
| C | `#gtceu:circuits/lv` (LV級回路タグ) | 2 |
| V | `gtceu:lv_conveyor_module` | 2 |
| M | `gtceu:lv_machine_hull` | 1 |
| W | `gtceu:tin_single_cable` | 2 |

原典：[Machine Recipe Loader](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/MetaTileEntityLoader.java#L781-L785)、[LV段階のCraftingComponent割り当て](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/GTCraftingComponents.java#L80-L85)。

## 作成順

1. **LV Machine Casing**：Steel Plate ×8 と中央のWrench（GregTech craftingToolWrench）を使う作業台製法。`PPP / PwP / PPP`。[原典](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/MetaTileEntityLoader.java#L39-L42)
2. **LV Machine Hull**：Wrought Iron Plate ×2、Steel Plate ×1、Tin Single Cable ×2、LV Machine Casing ×1。配置 `PLP / CHC`。[原典](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/MetaTileEntityLoader.java#L60-L62)
3. **LV Robot Arm ×2**：1個につきTin Single Cable ×3、Steel Rod ×2、LV Electric Motor ×2、LV Electric Piston ×1、LV回路 ×1。配置 `CCC / MRM / PXR`。[原典](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/ComponentRecipes.java#L666-L670)
4. **LV Conveyor Module ×2**：ゴム板を使う場合、1個につきRubber Plate ×6、LV Electric Motor ×2、Tin Single Cable ×1。配置 `RRR / MCM / RRR`。原典には別のゴム素材による派生レシピもある。[原典](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/ComponentRecipes.java#L156-L170)
5. **LV Assembler ×1**：冒頭の3×3に必要部品を配置。

6. **LV Electric Motor**：作業台でTin Single Cable ×2、Copper Single Wire ×4、Iron Rod ×2 + Magnetic Iron Rod ×1、またはSteel Rod ×2 + Magnetic Steel Rod ×1。配置 `CWR / WMW / RWC`。原典：[モーターの2製法](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/ComponentRecipes.java#L29-L36)。
7. **LV Electric Piston**：Steel Plate ×3、Tin Single Cable ×2、Steel Rod ×2、Small Steel Gear ×1、LV Electric Motor ×1。配置 `PPP / CRR / CMG`。原典：[ピストン](https://github.com/GregTechCEu/GregTech-Modern/blob/91a79b8a7a2b62ec6277423e6c0ded4af89a831e/src/main/java/com/gregtechceu/gtceu/data/recipe/misc/ComponentRecipes.java#L542-L545)。

**注意点**：AssemblerでMachine Hullを作る別レシピもあるが、**初号機を作る場合は作業台製のHullを使う**。Robot Arm等の下位素材（素材板、回路、工具、ケーブルの製造）までは全件未収録。この文書は完全な素材入手経路を保証しない。

### ATM9 Expert側の改変チェック

- [KubeJSの削除指定](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/server_scripts/recipeRemovals.js) に `lv_assembler` の直接削除指定を確認できなかった。
- [CraftingComponent変更スクリプト](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/kubejs/startup_scripts/customComponents.js) は主にUHV以上の段階を変更しており、LV素材の明示的な置換は確認できなかった。
- [クエスト](https://github.com/AllTheMods/atm9-expert/blob/309d0fa357b00d855f3a50739ae64737f7537936/config/ftbquests/quests/chapters/low_voltage.snbt)にはLV Assemblerの入手タスクがある。

**未確認**：他のKubeJS生成処理、実機JEI表示の全候補、導入パックの配布版、下位素材レシピの完全展開。GitHubにある標準レシピは現時点では**有力な製作候補**である。
