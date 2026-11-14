# 研究 3：Kobayashi 方式（D4 code switching）と 15-to-1 蒸留の資源比較 — v13

回路レベル雑音の code switching 全体を Pauli proxy 法（Takada らの Algorithm 2）で厳密に標本化して T 魔法状態の出力誤り $\varepsilon_K$ を求め、15-to-1 蒸留（Litinski の誤り予算モデル）と時空間体積を比べる。シナリオは A（アイドル雑音あり）と B（なし）。

物理回路・雑音・復号器は v9（= v6）と同じ。統計解析は v9.2 の多項分布の方法を引き継ぎ、データによる到達保証の「族」を v10 で改めた（理由は `../旧版/v10/利用者向け__v10_改訂の記録と判断.md` §3）。v11 で表全体の基準での費用下限の列を加え、追加 MC が既存の本番 CSV に追記できない不具合を直した（`../旧版/v11/利用者向け__v11_改訂の記録と判断.md`）。v12 は版の表記・ノートの説明と、物理検証の `QUICK=True` の判定の修正だけ（`../旧版/v12/利用者向け__v12_改訂の記録と判断.md`）。**v13 は図と説明の改訂**：2 枚の図を発表用に描き直し、図を結果の CSV から描く独立したモジュール `figures_v13.py` にした。回路・雑音・復号器・統計・判定は変えておらず、v12 と共通の出力は全て同じ値（`../利用者向け/v13_改訂の記録と判断.md`）。方法の正式な説明は `../論文草稿/研究まとめ_論文草稿_v12.md` の研究 3 の節と統合論文 §5.3。旧版（v5.2, v9, v9.2）は `../旧版/`。

## 1. 実行するもの（Colab での所要時間）

| ノート・スクリプト | 内容 | 所要時間の目安 |
|---|---|---|
| `noisy_cost_comparison.ipynb` | **比較の本体**（CPU、新しい MC なし）。既定 `DATA_MODE='reference'` は `data/` の本番データを使う | 約 30 分（`N_BOOT=200`。大半はモデルのブートストラップ。`N_BOOT=20` なら数分） |
| `run_comparison.py` | 上のノートをコマンドラインで実行（`--output-dir`, `--n-boot`） | 同じ |
| `figures_v13.py` | **図だけを描き直す**（`python figures_v13.py [--results results_v13] [--figures figures_v13] [--pdf]`）。`results_v13/` の CSV を読むだけで、当てはめも判定もしない。`--pdf` でベクター形式の PDF も出す | 数秒 |
| `D4_noisy_simulation.ipynb` | Kobayashi 方式の雑音付き MC と、表面符号の論理誤り率の較正（追加ショットを取るときだけ） | `QUICK=True`（既定、動作確認）約 1〜2 分（この環境の実測 41 秒）。全点の本番（`QUICK=False, RUN='all'`）は CPU 約 80〜90 時間分（Colab の 2 コアで 2 日程度、通常は不要）。1 点に $10^6$ ショット追加で CPU 約 9 時間分（例 B・$p=2\times10^{-4}$・$d=7$） |
| `validation.ipynb` | 物理の検証（適用条件、真の非 Clifford 回路との照合、単一故障の走査など。物理コードを変えたときだけ） | 既定の `QUICK=False` で約 2 時間。`QUICK=True` で約 30〜45 分（この環境の実測 29 分） |
| `statistics_validation_v13.ipynb` | 統計手法の単独検証 | 1 分以内 |
| `build_notebooks_v13.py` | ノートの再生成（物理ライブラリは `../旧版/3_魔法状態蒸留との比較_v9/` のノートからそのまま取り込む） | 数秒 |

MC の見積もりは本番データの記録（1 ショットあたり B で $d=3,5,7,9$ がそれぞれ約 2.5, 9, 31, 108 ms、A は約 1.3〜2 倍）から。

## 2. フォルダのファイル

| ファイル | 内容 |
|---|---|
| 上の表のノートとスクリプト | §1 |
| `analysis_v13.py` | 統計解析の正規ソース（集計の検査、区間、信頼列、多項分布のモデルと当てはめ）。ノートに埋め込まれる。内容は v12 と同じ（版の表記だけ） |
| `figures_v13.py` | 図の正規ソース（配色・記号・注記を含む）。ノートに埋め込まれ、最後のセルが呼ぶ。単独でも実行できる（§1） |
| `cells/decisions.py`, `cells/fit_models.py`, `cells/figures.py`, `cells/statistics_validation.py` | 比較ノートの判定のセル、当てはめのセル、図のセル（曲線の元データを保存して `figures_v13.py` を呼ぶ）、統計検証ノートのセルの正規ソース |
| `data/d4_noisy_mc.csv` | **本番の MC データ**（実行 ID 2 つ、554 万ショット）。1 行 = 1 チャンク。列：`run_id`, `point_id`, `chunk_id`, `seed`, `scenario`（A／B）, `window`（`noisy` 本来のシミュレーション／`quiet` 切り替えの窓を雑音なしにした診断）, `d`, `p`, `p_idle`, `kappa0`・`kappa_in`・`kappa_out`（ラウンド数の倍率）, `R0`・`Rin`・`Rout`（ラウンド数）, `shots`, `sum_infidelity`, `n_fail`（不忠実度 > 0 のショット）, `n_half`（不忠実度 1/2 のショット）, `mean_errors`, `mean_so_cz`, `seconds` |
| `data/surface_code_plog.csv` | 表面符号の較正データ（蒸留側の $p_L$）。列：`scenario`, `d`, `p`, `shots`, `rounds`, `PL_x`・`PL_z`（X・Z の論理誤りの割合）, `pL_per_round`（1 ラウンドあたりの論理誤り率） |
| `data/provenance.json` | 上の 2 つの SHA-256 と来歴 |
| `results_v13/`, `figures_v13/` | 比較ノートの出力（この環境で `N_BOOT=200`、`reference` で実行したもの。§3.1） |
| `results_v13/statistics_validation.json` | 統計検証ノートの出力（§3.4） |
| `results_v13/execution_manifest.json` | `run_comparison.py` の記録（ノートの SHA-256、`N_BOOT`、依存パッケージの版。v13 から `run_comparison.py` が直接ここに書く） |
| `results_v13/verification/` | この環境で実行したときのログ：`comparison_run.log`（比較ノート）、`statistics_validation.log`、`tests_v13.log`（リポジトリの回帰テスト） |

## 3. 出力ファイル

### 3.1 比較ノート `noisy_cost_comparison.ipynb`（`results_v13/`, `figures_v13/`）

| ファイル | 内容 |
|---|---|
| `results_v13/cost_comparison.csv` | **比較の表（主な結果）**。1 行 = 1 条件（シナリオ × $p$ × 目標の出力誤り、40 行）。列の読み方は §4 |
| `results_v13/data_intervals.csv` | 点（シナリオ × 窓 × $d$ × $p$）ごとのデータの集計と区間。列：`shots`, `s`（不忠実度の和）, `n_one`・`n_half`・`n_zero`（不忠実度 1・1/2・0 のショット）, `eps`（推定値）, `stderr`（多項分布の標準誤差）, `lower_decision`・`upper_decision`（判定に使う信頼列の区間。その行の候補サイズ $M=4$ を同時に 95%）, `lower_tablewide`・`upper_tablewide`（表全体 $M=200$）, `lower_fixedN_reference`・`upper_fixedN_reference`（固定ショット数を仮定した参考の区間） |
| `results_v13/aggregated_counts.csv` | MC の全チャンクを点ごとに集計したもの（ラウンド数の倍率を変えた点も含む）。列は上の集計部分と同じ＋`eps_over_p` |
| `results_v13/model_curves.csv` | **図の曲線の元データ**（v13 で追加。中央の当てはめだけで、ブートストラップによらない）。列：`curve`（`vs_p`＝$d=3,5,7,9$ を $p$ の格子 40 点で／`vs_d`＝`P_EVAL` の各 $p$ を $d=3,\dots,59$ で）, `scenario`, `window`, `d`, `p`, `eps_model`, `volume`（そのサイズの時空間体積）, `in_fit_domain`（当てはめた範囲の内側か。`noisy` は $d\ge7$）, `d_extrapolated`（$d>9$）, `p_extrapolated`（quiet の最小の $p$ 未満） |
| `results_v13/model_predictions.csv` | 多項分布のモデルの予測。列：`scenario`, `d`, `p`, `window`, `eps_model`（中央の当てはめ）, `model_025`・`model_975`（ブートストラップ 200 回の 2.5・97.5% 点）, `model_fit_domain`（当てはめた範囲の内側か） |
| `results_v13/fit_diagnostics.json` | 当てはめ 1,608 回（中央＋ブートストラップ × 成分）の記録：成功したか、負の対数尤度、反復回数、境界に張り付いたか、カテゴリ件数 |
| `results_v13/factory_candidates.csv` | 蒸留側の候補（各条件 1,632 構成 × 10 条件）。列：`protocol`, `family`（GoSC 15-to-1／225-to-1／Litinski 1 段／2 段）, `eps`（出力誤り）, `p_success`, `qubits`, `cycles`, `time_steps`, `volume_steps`（体積）, `scenario`, `p` |
| `figures_v13/d4_logical_error.png` | **出力誤りの図（2 × 2 パネル）**。上の段＝本来のシミュレーション（`noisy`）、下の段＝切り替えの窓を雑音なしにした診断（`quiet`）、左右＝シナリオ。横軸 $p$、縦軸 $\varepsilon_K$（両対数）。マーカー＝データ（形と色の濃さが $d$。濃いほど大きい）、縦棒＝**判定に使う 95% の信頼列の区間**（`data_intervals.csv` の `lower_decision`・`upper_decision`。その $p$ の候補サイズ全体で同時）、白抜きの下向き三角＝失敗 0 の点（区間の上端）、曲線＝当てはめたモデル（上の段は当てはめた範囲の $d\ge7$ だけ。窓の項が $d$ によらないので $d=7$ と 9 の曲線はほぼ重なる）、点線＝「誤り＝$p$」の目安。同じ $p$ のマーカーは重ならないよう横に少しずらして描いている（最大 ±8%。表示だけで、値は CSV のとおり）。**読み方**：$d$ を大きくしても点が下がらなければ、そのサイズの範囲では誤りが下げ止まっている。上の段と下の段の差が、切り替えの窓の誤りの寄与 |
| `figures_v13/cost_comparison.png` | **費用の図（2 × 3 パネル）**。行＝シナリオ、列＝$p=10^{-4}, 3\times10^{-4}, 10^{-3}$。横軸＝時空間体積（物理量子ビット × 時間ステップ）、縦軸＝T 状態 1 個の出力誤り（両対数）。**橙の階段**＝蒸留（候補のパレート前線）、**青の丸**＝Kobayashi 方式（D4 code switching）のシミュレーション（上に $d$ を添える。縦棒は上と同じ 95% の区間、白抜きの三角は失敗 0 の点）、**青の破線**＝そのモデルの $d>9$ への外挿（$d\ge7$ に当てはめ）、**灰色の破線**＝窓を雑音なしにした診断のモデル（「窓の誤りが無かったら」で、限界ではない。結果ではないので無彩色）、点線＝「誤り＝$p$」。各パネルの題の下の 2 行は、要求 $10^{-4}$ についての `cost_comparison.csv` の結果（データで保証されたサイズと体積比、または棄却されない最小サイズと体積比の下限）。**読み方**：同じ出力誤り（横線）を達成するのに、左にある方が体積が小さい＝有利 |

図の区間を v12 の ± 標準誤差から判定の区間に変えた理由：失敗が 1〜2 回の点では標準誤差の棒が対数軸の下に突き抜け、また表の判定（`data_certified`／`data_rejected`）と図が対応しなかった。失敗 0 の点（例：B・$p=10^{-4}$・$d=9$）は v12 の費用の図では対数軸に描けず抜けていたので、区間の上端を三角で示すようにした。v12 の図は `../旧版/v12/` にある。

### 3.2 シミュレーションのノート `D4_noisy_simulation.ipynb`（`results_v13/`）

| ファイル | 内容 |
|---|---|
| `d4_noisy_mc.csv`（`QUICK=True` では `d4_noisy_mc_quick.csv`） | MC の記録（列は §2 の `data/d4_noisy_mc.csv` と同じ）。比較ノートの `DATA_MODE='production'`（または `'quick'`）で読む |
| `surface_code_plog.csv`（`_quick`） | 表面符号の較正（列は §2 と同じ）。既にあれば再利用する |
| `d4_noisy_mc_runs.jsonl` | 既存の本番 CSV に追記したときだけ。追加の実行ごとの `run_id` と停止規則（固定ショット数）の記録 |

図はノートの中に表示するだけで保存しない。

### 3.3 物理の検証 `validation.ipynb`（`results_v13/`）

| ファイル | 内容 |
|---|---|
| `validation.json` | 検査項目ごとの状態（`PASS`／`FAIL`／`INFO`）と詳細、検証していない事項の一覧（`not_verified`）。最後に `<PASS 数> PASS, <FAIL 数> FAIL, <INFO 数> INFO` を表示する（完全版の記録は 189 PASS, 0 FAIL, 6 INFO） |

### 3.4 統計検証 `statistics_validation_v13.ipynb`（`results_v13/`）

| ファイル | 内容 |
|---|---|
| `statistics_validation.json` | 検査の結果：`zero_failure_bound`（失敗 0 のときの上限の式）、`exact_fixed_sample_coverage`（固定ショット数の区間の被覆率を分布の全列挙で計算した値、6 通り。0.95 以上なら合格）、`optional_stopping_failure_probabilities`（失敗数で止める逐次停止のもとで、信頼列が真値を外す確率、3 通り。0.05 以下なら合格）、`multinomial_fit`（多項分布の当てはめが既知の値を再現するか）。最後に `STATISTICS VALIDATION PASSED` |

比較の出力は 7 ファイルと図 2 枚。v12 までの 6 ファイルは列も値も変えておらず、v13 で図の曲線の元データ `model_curves.csv` を加えた（図を CSV だけから描き直せるようにするため）。

## 4. `cost_comparison.csv` の列の読み方

* `kobayashi_status`：`data_certified` ＝ 信頼列（旧 MC の停止規則・追加に有効）で、その行の候補サイズ全体を同時に 95% で覆ったときに上端が要求以下。`kobayashi_minimum_resolved` が True なら、より小さいサイズはデータで棄却されている。
* `kobayashi_d_low` と `ratio_kobayashi_low_over_litinski`：データで棄却されない最小のサイズとその体積比（＝データによる体積の下限。シミュレーションしていない $d\ge11$ は「棄却されない」扱い）。
* `kobayashi_tablewide_*`：v9.2 の表全体（最大 200 点）の同時保証。より厳しい感度。`kobayashi_tablewide_d_low`・`kobayashi_tablewide_volume_low`・`ratio_kobayashi_tablewide_low_over_litinski`（v11 で追加）は表全体の基準での費用下限。「全条件で x 倍以上」のように表全体についての主張にはこちらを使う。
* `kobayashi_model_*`：モデルの bootstrap の 95% 以上が要求を満たす最小サイズ（保証ではない）。
* `kobayashi_diag_*`：窓を雑音なしにした診断で同じ判定をしたもの。`kobayashi_W5_*`：窓の成分を $d\ge5$ の点に当てはめたモデル（主モデルは $d\ge7$）。`kobayashi_altW_*`：さらに窓の成分の $d$ 依存を許したモデル。`*_fsc8`：FSC のラウンドを 8 ステップで数えた費用の感度。
* `litinski_*`：蒸留側の最小体積の構成（`litinski_protocol`）と、その出力誤り・量子ビット数・時間・体積。文献の誤り予算の中央値で、同じ統計保証は無い。
* `ratio_*_over_litinski`：Kobayashi 方式の体積 ÷ 蒸留の体積（1 を超えると蒸留が有利）。

## 5. 主な結果（数値は v10 から同じ。v13 でも変わらない）

* データで保証：B（アイドルなし）・$p=10^{-4}$・要求 $10^{-4}$ で $d=5$（$d=3$ は棄却され最小が確定）、体積は Litinski 方式の **2.30 倍**。
* 要求 $10^{-4}$ の全 10 条件で、データで棄却されない最小サイズでも Litinski 方式の **1.59 倍以上**。この下限は表全体の基準（$M=200$）でも同じ（下限サイズが全 10 条件で一致）。
* 要求 $10^{-6}$ 以下：データでもモデルでも Kobayashi 方式の到達は支持されない（$d\le9$ の多くはデータで棄却、$d\ge11$ は未計算）。モデルは $d\le9$ に当てはめた記述モデルの外挿で（主モデルは窓の成分が $d$ によらないと仮定、altW は $d$ 依存を許す）、大きい $d$ での誤りの床を物理的に示したものではない。
* 表全体の同時保証（v9.2 の基準）では、到達の保証は全 40 条件で未確定（費用の下限は付く。40 条件中 39 条件で下限サイズは行ごとの基準と同じ）。

## 6. 追加の計算

既存の本番データへの追加（`RUN='extend'`）は、先に `data/` の 2 つの CSV をシミュレーション側の `results_v13/` にコピーしてから行う。出力を比較ノートの `results_v13/` に置いて `DATA_MODE='production'` で再解析する。手順は `../利用者向け/v13_実行手順.md` §5。既存の本番 CSV（`stopping_rule` 列が無い）にも、その列に合わせて追記する（v11 の修正。回帰テスト `tests/test_notebooks.py`）。
