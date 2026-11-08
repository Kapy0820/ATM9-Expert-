# レシピ全件収集の方法と限界

## 1. 対象を固定

- ATM9 Expert 0.7.1 の配布ファイルとMod構成を固定する。
- 公式GitHubのmainは変動するため、実際の配布ファイルと照合する。今回の索引は2026-11-08に参照したmainに基づく。

## 2. ソースから抽出

- KubeJSの追加・変更・削除（shaped / shapeless / custom / gtceu等）を分類する。
- forEachRecipe、ループ、条件分岐、タグ置換を静的に展開できない場合は「動的生成」として記録する。
- データパックJSONを調査する。
- Mod本体の標準レシピとconfigによる変更を別途取得する。

## 3. 実ゲームで最終検証

- 同じバージョンのクライアント／サーバーで起動し、JEI/EMIに表示される有効レシピを照合する。
- 特にGTCEuの流体、回路、電圧、消費時間、非消費触媒、確率出力、タグ素材、研究条件を確認する。
- レシピなし、ドロップ専用、取引専用、入手不可のアイテムも別カテゴリにする。

## 4. 記録形式

mod_id | output_id | output_count | recipe_type | machine | ingredients | fluids | EU/t | duration | conditions | source | verified_version | status

## 5. ステータス

- source-only: ソースへの参照のみ
- parsed: ソースから機械的に抽出、未検証
- verified: 実ゲームで確認済み
- unavailable: レシピなし・無効・入手不可（根拠を記載）

現時点の索引はすべて source-only です。ソースファイル数をアイテム数やレシピ数として扱わないでください。
