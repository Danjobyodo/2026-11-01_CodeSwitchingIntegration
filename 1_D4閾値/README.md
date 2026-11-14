# 研究 1：D4 符号の X スタビライザ（電荷側）の有限サイズ交点 — v13

トーラス上の D4 符号の記憶実験を twisted frame（D4 符号に特化した厳密な表現）で標本化し、X スタビライザ側（電荷側）の失敗率の有限サイズ交点を求める。統合論文には現象論的雑音だけを載せる（符号容量型・回路レベルのコードも残してある）。

方法・結果の正式な説明は `../論文草稿/研究まとめ_論文草稿_v13.md`（研究 1 の節）、統合論文 `../論文草稿/統合論文_v13/main.tex`、研究 1 単独の原稿 `../論文草稿/研究1_原稿_v13/main_v13.tex`。旧版（v7, v8 原稿, v9.1, v9.2）は `../旧版/1_D4閾値/`、v11 で内容を変えたファイルは `../旧版/v11/`。

## 1. 実行するもの（Colab での所要時間）

| ノート | 内容 | 所要時間の目安 |
|---|---|---|
| `D4_v13_main.ipynb` | メイン（CPU）。上から実行すると定義まで（長い計算のセルはコメントアウト） | 上から最後まで約 1〜2 分。`run_production(noise_models=["phenomenological"])`（統合論文に必要な本番、D4・none・kappa_injection の 3 種）で約 10〜15 時間 |
| `D4_v13_validation.ipynb` | 正当化（GPU 推奨）：(A) 幾何、(B) 密な状態ベクトルとのロックステップ、(C) 独立標本の比較、(D) 復号器の事前分布の走査（任意）、(E) Pauli proxy との $L\le9$ の突き合わせ（CPU） | 1 雑音モデルで、論理セクター `r` は約 2〜3 時間、`rgb` はその約 4 倍（T4）。(E) だけなら CPU で約 10 分 |

詳しい内訳は各ノートの冒頭の表。見積もりは、この研究の実測（1 ショットあたり $p=2\%$ の現象論的雑音で $L=3,5,7,9$ がそれぞれ約 0.3, 0.9, 2.2, 6.3 ms）と v7 の正当化の記録から出したもので、Colab の CPU はこれと同程度〜1.5 倍遅い。

* 物理・乱数・判定は v9.1 から同じ。v9.2 で「設定が完全に一致するときだけ完了点を再利用する」再開機能（JSON チェックポイント）が入った。
* v13 の変更は版の表記と出力名だけ（研究 3 の v13 に合わせて全研究の版をそろえた）。v12 の変更は出力の整理（§3 の最後）。同じ出力先に v12・v11・v10 のチェックポイント（`d4_v12_*`・`d4_v11_*`・`d4_v10_*_checkpoint.json`）があり、設定が版の表記以外すべて一致するとき、その完了点を再計算せずに引き継ぐ（旧ファイルは変更しない。回帰テスト `tests/test_v13_resume_legacy.py`）。
* 未実行：現象論的雑音の $10^5$ ショット/点の本番と対照実験（統合論文に必要）、回路レベル（`uniform`）の本番と GPU の正当化（研究 1 単独の原稿用）。手順は `../利用者向け/v13_実行手順.md`。

## 2. フォルダのファイル

| ファイル | 内容 |
|---|---|
| `D4_v13_main.ipynb`, `D4_v13_validation.ipynb` | 上の 2 つのノート（`tools_v13/` から生成したもの。直接編集しない） |
| `解説_twisted_frame/` | twisted frame（メインのシミュレーションの方法）の原理と、研究 1 でこれを使える理由・使うべき理由の解説。専門家以外向け。`twisted_frame解説.md`（日本語）、`twisted_frame_explained.tex`（英語、Overleaf の pdfLaTeX でそのまま組版できる。md と同じ内容に図 3 枚を加えたもの）、`twisted_frame_explained.pdf`（その組版結果） |
| `tools_v13/build_notebooks_v13.py` | ノートの生成（`python tools_v13/build_notebooks_v13.py`、1 秒程度）。`--scripts <出力先>` で同じ内容の .py（`d4_v13_main_script.py`, `d4_v13_val_script.py`）も作る |
| `tools_v13/cells/` | ノートのセルの正規ソース。`c01`〜`c09`：メインと正当化で共通のコード（`c02` 設定、`c03` 幾何、`c04`〜`c06` 旧研究のサロゲートと電荷復号器の事前分布用の Stim 回路、`c07` twisted frame、`c08` プロトコル・復号器・回路レベルの故障表、`c09` 掃引・出力・本番の一括実行）。`v01`〜`v13`：正当化だけのコード（`v10_dense` 密な状態ベクトル、`v11_run` (B)(C)(D)、`v13_proxy` (E)。番号はセルの並び順で版番号ではない）。`m*.md`・`v*.md` は説明のセル |
| `データ_v7本番/メインコード実行結果/9までやった(pheno)/` | **現象論的雑音の本番（v7 のコード＝v13 と同じ標本・同じ判定、$10^4$ ショット/点、$L=3$–9、10 点）**。統合論文の図 2・表 4 の元データ。`*.csv`（結果の表、列は §3.1）、`*_crossings.csv`（交点）、`*_manifest.json`（実行条件）、`D4_v7_main.ipynb`（実行したノートと出力の記録） |
| `データ_v7本番/メインコード実行結果/9までやった(depo)/` | 同じく符号容量型（論文では §2.2 の診断の 1 文だけに使う） |
| `データ_v7本番/メインコード実行結果/9までやった(cl)/` | 回路レベル（旧定義 `legacy_v7`）。現在の定義（`uniform`）とは別で、統合論文では使わない |
| `データ_v7本番/正当化コード結果/` | v7 の正当化（$L=3$）：`d4_v7_validation_L3_<model>.csv`（(C) 密な計算とメインの失敗率）、`_lockstep.csv`（(B)）、`_manifest.json`、セル出力のテキスト（`2026-10-02_セル出力完全版.txt` など、実行の記録）、`正当化結果byClaude.txt`（結果の読み取り）。現象論的雑音の正当化はこれで済んでいる |
| `検証ログ/v9_1_検証ログ/` | v9.1 の確認：`d4_v9_1_proxy_crosscheck_L3-9.csv`（(E) の結果、3 雑音モデル × $L=3$–9）、`proxy_negative_controls.log`（Pauli dressing を外すと不一致になることの確認）、`d4_v9_1_decoder_kappa_scan_<model>.csv` と `decoder_kappa_check_*.csv`・`decoder_kappa_scan.log`（(D) 復号器の事前分布の走査）、`pilot_circuit_level_uniform_kappa0.1_L3-7_4000shots.csv`（回路レベル `uniform` の試行値）、`scripts/`（記録として残した補助スクリプト。`d4_v91_val_gen` などを import するので、そのままでは動かない。同等のモジュールは `--scripts` で生成できる） |
| `検証ログ/v9_試行計算/` | v9 の確認：v7 の再現と診断量（`check_v7_reproduction_and_R1-3_diagnostics.log`）、回路レベルの 2 定義の密な照合（`dense_lockstep_*.log`）、回路レベル `uniform` の試行計算（`pilot_*.csv`）、`scripts/`（照合のスクリプトと、GPU なしで動かすための JAX の代用 `jaxshim/`） |

v12 で、`データ_v7本番/メインコード実行結果/` の直下にあった現象論的雑音の 3 ファイル（$L\le7$ の途中の実行）を削除した。`9までやった(pheno)/` の $L\le7$ の行と完全に同じだったため（git の履歴には残っている）。

## 3. 出力ファイル（ノートを実行すると作られるもの）

### 3.1 メイン：`CFG["out_dir"]`（既定 `d4_v13_results/`）

1 条件（雑音モデル × dressing の扱い）あたり 5 ファイル。`<tag>` = `d4_v13_X_memory_<model>_twisted_frame[_<treatment>][_<preset>]`（`<treatment>` は対照実験 `none`・`kappa_injection` のときだけ、`<preset>` は回路レベルのときだけ付く）。

| ファイル | 内容 |
|---|---|
| `<tag>.csv` | **結果の表**（1 行 = 1 点 $(L,p)$）。主な列：`L`, `p`, `shots`；`ler_charge`（= `n_fail_charge / n_trials_charge`。X スタビライザ側の失敗率。flux 側が成功したショットに条件付け。**閾値はこれで求める**）と `_lower`・`_upper`（95% Agresti–Coull 区間）；`ler_flux`（終了時に非自明な X ループが残った割合）；`ler_combined`（どちらかの失敗）；`frac_random_outcomes`（dressed 測定のうち結果が確率 1/2 だった割合）；`n_fractional_F`（最終忠実度が 0 と 1 の間だったショット数）；`flux_faces_before_x_per_round`・`frac_rounds_flux_before_x`（dressed 層の直前に残っていたフラックス）、`frac_random_outcomes_noflux_rounds`（フラックスが無い層でのランダムな結果の割合。0 でなければ CZ 型の残差による）；`jit_flips_per_shot`、`seed`、`code_version` など |
| `<tag>.png` | **図（1 枚、3 パネル）**。左：$P_{\rm charge}$（flux 成功に条件付けた電荷側の失敗率。研究の主指標）、中：$P_{\rm flux}$、右：$P_{\rm comb}$（どちらかの失敗）。横軸は物理誤り率 $p$、縦軸は失敗率（どちらも対数）、色は $L$、誤差棒は 95% 区間。**読み方**：隣り合う $L$ の曲線が交わる $p$ が有限サイズの交点（閾値の目安）で、それより左（$p$ が小さい側）では $L$ が大きいほど失敗率が低い。交点が $L$ とともに動くなら、漸近閾値はまだ決まっていない |
| `<tag>_crossings.csv` | 隣り合う $L$ の交点。列：`L_a`, `L_b`, `crossings`（点推定。交点が複数あればそのすべて）、`ci68`・`ci95`（失敗数を Jeffreys 事後分布から再標本化したときの交点の分位点）、`unique_draws`・`no_crossing_draws`・`multiple_crossing_draws`（再標本化 400 回のうち、交点が 1 つ・無し・複数だった回数）、`metric`（`charge`・`combined`・`flux`）。区間は交点の位置の標本変動であって、漸近閾値の区間ではない |
| `<tag>_manifest.json` | 実行条件の記録：版、日時、Python と依存パッケージの版、`CFG` の全体、$p$ の格子 |
| `<tag>_checkpoint.json` | 再開用（完了した点の結果と、照合に使う設定）。中断後に同じ設定・同じ出力先で実行すると、ここにある点は再計算しない。CSV はこれから作り直せる派生物 |

`run_production()` は、雑音モデルごとにもう 1 枚作る。

| ファイル | 内容 |
|---|---|
| `d4_v13_treatment_comparison_<model>_charge.png` | **対照実験の図**。D4（実線・丸）、dressing なし `none`（破線・四角）、dressing なし＋旧研究の独立な Z 注入 `kappa_injection`（点線・三角）の $P_{\rm charge}$ を重ねたもの。色は $L$。**読み方**：D4 と none の差が、選んだ dressed／undressed の模型の総合差（非可換性だけの効果ではない）。kappa_injection が D4 の曲線に重ならなければ、独立な雑音の近似では D4 を再現できない |

最後のセルで `out_dir` を zip（`d4_v13_results.zip`）にまとめてダウンロードする。

### 3.2 正当化：`VCFG["out_dir"]`（既定 `d4_v13_validation_results/`）

雑音モデルごとに 4 ファイル。`<vtag>` = `d4_v13_validation_L3_<model>[_<preset>]`。

| ファイル | 内容 |
|---|---|
| `<vtag>_lockstep.csv` | (B) の結果（論理セクター `r`・`rgb` の 2 行）。列：`p`, `shots`（照合した軌道の数）、`max_prob_deviation`（twisted frame と密な計算の測定確率の最大差）、`max_fidelity_deviation`（最終忠実度の最大差）、`random_outcomes_checked`（照合した確率 1/2 の結果の数）、`seconds`。差が $10^{-6}$ 程度以下なら合格（単精度の丸め） |
| `<vtag>_C.csv` | (C) の結果（論理セクター `r` と `rgb` を 1 つの表に）。列：`model`（`exact_dense` 密な計算、`twisted_frame_main` メインと同じ経路、`old_surrogate` 旧研究のサロゲート＝既定では計算しない）、`logical_colors`、`p`, `shots`、`ler_charge`・`ler_combined`・`ler_flux` と区間、`n_fail_*`・`n_trials_*` |
| `<vtag>_C.png` | **(C) の図（1 枚、論理セクターごとのパネル）**。赤の破線・四角＝密な状態ベクトル、青の実線・丸＝メインのエンジン。縦軸は $P_{\rm charge}$。**読み方**：赤と青が誤差棒の範囲で重なれば、メインの失敗率は $L=3$ で厳密計算と一致している。数値の判定は実行時に表示される $\sum z^2$ と上側確率で行う（1 点だけの外れは多重比較で起こりうる） |
| `<vtag>_manifest.json` | 実行条件（`CFG` と `VCFG` の全体、依存パッケージの版） |
| `d4_v13_proxy_crosscheck[_<preset>].csv` | (E) の結果（雑音モデル × $L$ の 1 行ずつ）。列：`max_prob_deviation`・`max_fidelity_deviation`（twisted frame と Pauli proxy の差。0 なら完全に一致）、`shots`（軌道の数）、`random_outcomes_tf`（確率 1/2 の測定の数）、`seconds` |
| `d4_v13_decoder_kappa_scan_<model>.csv` | (D) を実行した場合だけ。$\kappa_{\rm dec}$ と $L$ ごとの $P_{\rm charge}$。最大の $L$ で最小になる値をメインの `tf_decoder_kappa` に使う（物理ではなく復号器の調整） |

### 3.3 v12 で減らしたもの

| v11 まで | v12 |
|---|---|
| メイン：主指標だけの `<tag>.png` と、3 指標を並べた `<tag>_components.png` の 2 枚（前者は後者の左のパネルと同じ） | 3 指標の図 1 枚を `<tag>.png` に |
| メイン・正当化：全ての図の PDF（既定で作成） | 既定で作らない（`CFG["save_pdf"]=True`・`VCFG["save_pdf"]=True` で作る）。論文の図は CSV から `../論文草稿/統合論文_v13/scripts/make_figures.py` で作る |
| 正当化 (C)：論理セクターごとの CSV・PNG（`_C_r.*`, `_C_rgb.*`） | 1 つの CSV と、パネルを並べた 1 枚の図（`_C.csv`, `_C.png`） |
| 正当化 (C)：旧研究のサロゲートを既定で計算して図に重ねる | 既定で計算しない（`VCFG["run_old_surrogate"]=True` で従来どおり）。正当化には不要で、論文でも使わない |

1 条件あたりのファイルはメインで 8 → 5（PDF 2 つを含む）、正当化で 1 雑音モデルあたり 8 → 4。物理・乱数・判定・CSV の列は変えていない。
