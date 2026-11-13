# 研究 2：code switching の論理誤り率（現象論的雑音）— v12

折り畳み表面符号（FSC）→ D4 符号 → 理想的な論理 $T^\dagger$ → FSC の切り替え全体を、Pauli proxy 法（Takada らの Clifford-stabilizer simulation、Algorithm 1）で厳密に標本化し、論理誤り率 $P_L$ を求める。

方法（Pauli proxy 法、厳密性の条件 C1–C3、復号器）と結果の正式な説明は `../論文草稿/研究まとめ_論文草稿_v12.md`（研究 2 の節）と統合論文 `../論文草稿/統合論文_v12/main.tex` §5.2。旧版（v3, v9, v9.2 の再集計）は `../旧版/2_CodeSwitching論理誤り率/`、v11 で内容を変えたファイルは `../旧版/v11/`。

## 1. 実行するもの（Colab での所要時間）

| コード | 内容 | 所要時間の目安 |
|---|---|---|
| `CHSC_switch_v12_main.ipynb`（＝`chsc_switch_v12.py`） | メイン（CPU）。既定の設定は本番と同じ（3 ケース × ideal/noisy、$d=3,5,7$、8 点、20,000 ショット/点） | 既定のまま全部で約 9〜13 時間（1 条件あたり約 1.5〜2.5 時間）。`shots=2000` の動作確認で全部で約 1 時間。本番の CSV を出力先に置けば、図と表を作るだけなので 1〜2 分 |
| `CHSC_switch_v12_validation.ipynb`（＝`chsc_validation_v12.py`） | 正当化（総当たり・独立エンジン・本番経路の再生） | CPU で約 3〜5 分（`VALIDATION PASSED`） |
| `summarize_results_v12.py` | 保存した本番 CSV から指標・交点・図を作り直す（新しい MC はしない） | 約 10 秒 |
| `make_notebooks_v12.py` | 2 つの .py から 2 つのノートを生成 | 1 秒程度 |

見積もりは本番の記録（1 ショットあたり $d=3,5,7$ でそれぞれ約 2, 7, 20 ms、1 プロセス）から。Colab の CPU はこれと同程度〜1.5 倍遅い。

* 物理・復号器・乱数の使い方は v9 から同一（v10 は版の表記、v11 は再開の修正、v12 は出力の整理）。
* 288 万ショットの本番は完了している（`本番結果/`）。版番号のために取り直す必要はない。$d=9$ の追加は任意（既存の本番と同じ乱数の系列で続ける手順は `../利用者向け/v13_実行手順.md` §4。独立な標本を足すなら別の `out_dir` と seed）。
* 再開：`chsc_v12_*.csv` が無いとき、同じ出力先の `chsc_v11_*`・`chsc_v10_*`・`chsc_v9_*.csv` を探し、条件が同じなら既存の点を引き継いで `chsc_v12_*.csv` に書く（元のファイルは変更しない。旧名が 2 つある・条件が違うときはエラー。v11 で入れた修正。回帰テスト `tests/test_v12_resume_legacy.py`）。

## 2. フォルダのファイル

| ファイル | 内容 |
|---|---|
| `chsc_switch_v12.py` | メインのコードの正規ソース（`# %% [Cell n]` でノートのセルに分かれる）。`python chsc_switch_v12.py` で既定の CFG（本番）を実行する |
| `chsc_validation_v12.py` | 正当化のコードの正規ソース（`chsc_switch_v12.py` を import する） |
| `CHSC_switch_v12_main.ipynb`, `CHSC_switch_v12_validation.ipynb` | 上の 2 つから生成した Colab 用ノート（直接編集しない） |
| `make_notebooks_v12.py`, `summarize_results_v12.py` | §1 の表のとおり |
| `本番結果/chsc_v9_results/chsc_v9_<case>_<boundary>.csv` | **本番の 5 条件の結果**（v9 のコード＝v12 と同じ物理、2026-11-02 実行。各 24 点）。列は §3.1 の CSV と同じ |
| `本番結果/chsc_v9_results/*_crossings.csv`, `*_manifest.json` | 本番の時点で書いた交点（列は §3.1 の交点の表から `case`・`switch_in_boundary` を除いたもの）と実行条件 |
| `本番結果/chsc_v9_results/run_logs.txt`, `summary_tables.md` | 本番の実行ログと、$P_L$ の表・交点・論理状態の内訳の要約 |
| `本番結果/chsc_v3_results/` | `in_T_out`・ideal の本番（v3 のコード、Colab。v12 と全ショット同じ標本）。CSV・交点・実行条件。条件の書式が v9 以降と違うので、再開の引き継ぎの対象にはならない |
| `本番結果/指標の再集計/` | `summarize_results_v12.py` の出力（§3.3） |
| `検証ログ/v9_検証ログ/` | v9 の正当化：`validation_log_v9.txt`（全ログ）、`chsc_v9_validation.csv`（照合した点ごとの行、列は §3.2）、`pilot_noisy_decoder_comparison.csv`（noisy 境界の復号器の試行比較。列 `n_pre_u`・`dec`＝U 直前の Z ラウンド数と復号器、`P_L`・`lo`・`hi`＝失敗率と区間、`S`・`col`・`Z`＝類の割合、`ms`＝1 ショットの時間） |
| `検証ログ/v10/`, `検証ログ/v11/` | v10・v11 の正当化のログ（`VALIDATION PASSED`）と、v10 の照合の表 |

v12 で、`本番結果/chsc_v9_results/` の図 18 枚（条件ごとの $P_L$ の PNG・PDF、論理状態の内訳 `_frames.png`、ケース比較 `all_cases_*.png`、`ideal_vs_noisy.png`）を削除した。どれも CSV から作れる図で、v12 の 1 枚の図（`本番結果/指標の再集計/chsc_v12_P_L.png`）に置き換えた（git の履歴には残っている）。

## 3. 出力ファイル

### 3.1 メイン：`CFG["out_dir"]`（既定 `chsc_v12_results/`）

条件（ケース × 境界）ごとに 2 ファイル、出力先全体で 2 ファイル。

| ファイル | 内容 |
|---|---|
| `chsc_v12_<case>_<boundary>.csv` | **結果の表**（1 行 = 1 点 $(d,p)$）。`<case>` は `in_only`（switch-in だけ、D4 符号のまま理想的に読み出す）・`in_out`（U なしで戻る）・`in_T_out`（論理 $T^\dagger$ を入れた本番）、`<boundary>` は `ideal`（U の直前に雑音なしの完全な 1 ラウンド）・`noisy`（置かない）。主な列：`d`, `p`, `shots`；`P_L`（$=1-P(I)$、目標の論理状態と一致しなかった割合）と `P_L_lower`・`P_L_upper`（95% Agresti–Coull 区間）；`n_I, n_X, n_Y, n_Z, n_S, n_collapsed, n_flux_D4` と `P_*`（最終状態の論理的な類の内訳。`collapsed` は論理状態が壊れて重ね合わせでなくなったもの、`flux_D4` は `in_only` で D4 符号のフラックス側が失敗したもの）；`mean_infidelity_excl_fluxD4`（平均不忠実度。$X,Y,S$, collapsed は 1/2 と数える）；`sec_per_shot`、`seed`、`conditions`（再開の照合に使う条件の文字列）、`code_version` |
| `chsc_v12_<case>_<boundary>_manifest.json` | 実行条件（版、日時、依存パッケージの版、CFG、$p$ の格子） |
| `chsc_v12_crossings.csv` | **交点の表**（出力先にある全ての結果 CSV から作り直す）。列：`case`, `switch_in_boundary`, `d_a`, `d_b`, `crossings`（隣り合う $d$ の $P_L$ の曲線の交点。log–log 補間）、`ci95`（失敗数を Jeffreys 事後分布から再標本化したときの交点の 2.5–97.5% 点）、`unique_draws`（交点がちょうど 1 つだった再標本化の回数、300 回中） |
| `chsc_v12_P_L.png` | **図（1 枚）**：$P_L$ vs $p$。パネルはケース（左から `in_only`・`in_out`・`in_T_out`）、色は $d$、実線＋塗りつぶしの印は ideal 境界、破線＋白抜きの印は noisy 境界、誤差棒は 95% 区間、両軸とも対数。**読み方**：隣り合う $d$ の曲線の交点が有限サイズの閾値の目安で、それより左では $d$ が大きいほど $P_L$ が小さい。同じケースで実線と破線の差が、U の直前を理想化したかどうかの差（`in_T_out` で大きく、`in_out` で小さければ、U の時点で残った誤りが増幅されている） |

最後のセルで `out_dir` を zip（`chsc_v12_results.zip`）にまとめてダウンロードする。

### 3.2 正当化：作業ディレクトリ

| ファイル | 内容 |
|---|---|
| `chsc_v12_validation.csv` | 照合した点ごとの行。列：`reference`（`bf` 総当たりの状態ベクトル $d=2$、`tf` 独立な厳密エンジン $d=3,4$、`bf_replay` 本番経路の再生 $d=2$）、`boundary`, `case`, `d`, `p`, `shots`、`compared_outputs`（比較した出力の数：全ての測定の決定的／ランダムの別と結果、Z 検査、X フレーム、最終の類）、`mismatches`（**不一致の数。全行 0 で合格**）、`random_outcomes`・`frac_random`（確率 1/2 の測定）、類の件数、`seconds` |

### 3.3 再集計：`本番結果/指標の再集計/`（`summarize_results_v12.py`）

| ファイル | 内容 |
|---|---|
| `chsc_metrics_v12.csv` | 本番 6 条件・144 点の全ての行に、類の件数から計算し直した `P_L_recomputed` と `infidelity_excl_fluxD4_recomputed`、`evaluated_shots`、`source_file` を加えたもの（保存値と一致しないと止まる） |
| `provenance.json` | 元の CSV 6 つの SHA-256 と行数 |
| `chsc_v12_crossings.csv` | 本番 6 条件の交点（列は §3.1 と同じ）。統合論文の表 5 の交点の値 |
| `chsc_v12_P_L.png` | 本番 6 条件の $P_L$ の図（描き方は §3.1 と同じ）。統合論文の図 3 と同じデータ |

### 3.4 v12 で減らしたもの

| v11 まで（条件ごと） | v12 |
|---|---|
| `<prefix>.png`・`.pdf`（$P_L$ の図）、`_frames.png`（論理状態の内訳の図）、`_crossings.csv` | 作らない。交点は出力先全体の `chsc_v12_crossings.csv` に、図は `chsc_v12_P_L.png` にまとめた。内訳は CSV の `n_*` 列にある（図が要るときは `plot_frames(df, case, path)` を手で呼べる） |
| ケースごとの比較図 `all_cases_<boundary>.png`、境界の比較図 `ideal_vs_noisy.png` | `chsc_v12_P_L.png` 1 枚（誤差棒付き）に統合 |

6 条件で 39 ファイル → 14 ファイル。物理・乱数・判定・CSV の列は変えていない。
