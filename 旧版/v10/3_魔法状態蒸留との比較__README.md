# 研究 3：Kobayashi 方式（D4 code switching）と 15-to-1 蒸留の資源比較 — v10

物理回路・雑音・復号器は v9（= v6）と同じ。統計解析は v9.2 の多項分布の方法を引き継ぎ、データによる到達保証の「族」だけを v10 で改めた（理由は `../利用者向け/v10_改訂の記録と判断.md` §3）。方法の正式な説明は `../論文草稿/研究まとめ_論文草稿_v10.md` の研究 3 の節。旧版（v5.2, v9, v9.2）は `../旧版/`。

## ファイル

| ファイル | 内容 |
|---|---|
| `noisy_cost_comparison.ipynb` | **比較の本体**（CPU、追加 MC なし、`N_BOOT=200` で約 30 分）。既定 `DATA_MODE='reference'` は `data/` の本番データ |
| `D4_noisy_simulation.ipynb` | Kobayashi 方式の雑音付き MC と表面符号の較正（追加ショットを取るときだけ） |
| `validation.ipynb` | 物理の検証（v9 と同じ内容。物理コードを変えたときだけ再実行） |
| `statistics_validation_v10.ipynb` | 統計手法の単独検証（`STATISTICS VALIDATION PASSED`） |
| `analysis_v10.py`, `cells/` | 統計解析の正規ソース（ノートに埋め込まれる） |
| `build_notebooks_v10.py` | ノートの再生成（物理ライブラリは `../旧版/3_魔法状態蒸留との比較_v9/` のノートからそのまま取り込む） |
| `run_comparison.py` | 比較ノートをコマンドラインで実行（`--output-dir`, `--n-boot`） |
| `data/` | 本番データ（実行 ID 2 つ、554 万ショット）と較正データ、SHA-256（`provenance.json`） |
| `results_v10/`, `figures_v10/` | v10 の解析結果（2026-11-03、この環境で `N_BOOT=200` で実行） |

## 結果の列の読み方（`results_v10/cost_comparison.csv`）

* `kobayashi_status`：`data_certified` ＝ 信頼列（旧 MC の停止規則・追加に有効）で、その行の候補サイズ全体を同時に 95% で覆ったときに上端が要求以下。`kobayashi_minimum_resolved` が True なら、より小さいサイズはデータで棄却されている。
* `kobayashi_d_low` と `ratio_kobayashi_low_over_litinski`：データで棄却されない最小のサイズとその体積比（＝データによる体積の下限。シミュレーションしていない $d\ge11$ は「棄却されない」扱い）。
* `kobayashi_tablewide_*`：v9.2 の表全体（最大 200 点）の同時保証。より厳しい感度。
* `kobayashi_model_*`：モデルの bootstrap の 95% 以上が要求を満たす最小サイズ（保証ではない）。
* Litinski 側は文献の誤り予算の中央値（同じ統計保証は無い）。

## 主な結果（v10）

* データで保証：B（アイドルなし）・$p=10^{-4}$・要求 $10^{-4}$ で $d=5$（$d=3$ は棄却され最小が確定）、体積は Litinski 方式の **2.30 倍**。
* 要求 $10^{-4}$ の全 10 条件で、データで棄却されない最小サイズでも Litinski 方式の **1.59 倍以上**。
* 要求 $10^{-6}$ 以下：データでもモデルでも Kobayashi 方式の到達は支持されない（$d\le9$ の多くはデータで棄却、$d\ge11$ は未計算）。
* 表全体の同時保証（v9.2 の基準）では全 40 条件が未確定。

## 追加の計算

`D4_noisy_simulation.ipynb` を `QUICK=False`、`RUN='extend'`、固定の `EXTEND_SHOTS` で実行し、出力を比較ノートの `results_v10/` に置いて `DATA_MODE='production'` で再解析する。手順は `../利用者向け/v10_実行手順.md`。
