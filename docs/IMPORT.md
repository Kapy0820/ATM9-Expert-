# レシピ追加・実機検証

## 追加単位

`data/recipes/<完成品のnamespace>.json` に、1製造方法ごとに1つのレシピオブジェクトを追加します。材料・工程のMod IDではなく、**完成品のMod ID**に分類します。

```json
{
  "recipe_id": "examplemod:my_recipe",
  "recipe_type": "examplemod:machine",
  "output": {"item": "examplemod:output", "count": 2},
  "inputs": [{"choice": {"item": "minecraft:iron_ingot"}, "count": 4}],
  "catalysts": [{"item": "examplemod:mold", "consumed": false}],
  "costs": {"energy": 10000},
  "station": "JEIで確認できた装置名",
  "verification": {"status": "source_parsed", "effective_in_game": false, "pack_version": null},
  "source": {
    "repository": "AllTheMods/atm9-expert",
    "commit": "固定ソースコミット",
    "path": "kubejs/data/examplemod/recipes/my_recipe.json",
    "url": "https://github.com/.../blob/<commit>/..."
  }
}
```

- `inputs`には`choice: {"item":"..."}`か`choice: {"tag":"forge:ingots/iron"}`、または`choices: [{...}, {...}]`を指定できます。タグを勝手に鉄インゴットと確定させないでください。
- 非消費触媒は`catalysts`。流体、電圧、工程時間、確率出力、研究条件などは**検証してから**明示し、表現不能な条件を推測で潰さないでください。
- `source_parsed`はレシピ定義を読んだだけ。**実機JEI/EMIと照合したときのみ**`verified`へ変更し、実機バージョンも記入。
- `data/item_index.json`は手で編集せず、`python tools/recipe_query.py rebuild-index`で再生成します。
- `python tools/recipe_query.py validate`で整合性を確認します。

## 有効レシピを集めるには

配布されたATM9 Expertの**正確なバージョン**を固定し、実ゲームのJEI/EMIやエクスポートされた有効レシピと比較してください。Mod本体のjarにあるJSON、KubeJSのJSONとJavaScript、GregTech等の動的レシピ、削除・上書き後の結果は同一ではありません。

**残る未収録領域:** GregTechの大半、各Modの標準レシピ、KubeJSのループによる生成、特別な流体や研究ゲート、戦利品・交易による入手。数千件に及ぶ可能性があるため、全アイテムの登録完了を宣言しないでください。
