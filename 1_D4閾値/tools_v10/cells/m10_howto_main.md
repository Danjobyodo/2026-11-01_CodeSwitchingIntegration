# v9 の解釈と実行手順

**GPU 不要（CPU ランタイム）。** 所要時間の目安（手元の CPU）: 1 ショットあたり L=7 で 1–4 ms、L=9 で 2–6 ms 程度です（ノイズモデルにより異なる）。`run_production()` の全条件（3 モデル × 3 扱い × L=3–9 × 10 点 × $10^5$ ショット）は合計で数十時間かかるので、Colab ではモデルごとに分けて（`run_production(noise_models=["phenomenological"])` など）実行し、終わるたびに `out_dir` を保存してください。

- 出力（`CFG["out_dir"]`、既定 `d4_v10_results/`）: `d4_v10_X_memory_<model>_<engine>[_<treatment>][_<preset>].csv / .png / .pdf`、3 指標を並べた `..._components.png`、指標ごとの交点 `..._crossings.csv`、実行条件 `..._manifest.json`、対照実験の重ね描き `d4_v10_treatment_comparison_<model>_<metric>.png`。CSV は 1 点ごとに上書き保存されます。
- CSV の主な列:
  - `ler_charge`（= `n_fail_charge / n_trials_charge`）: X スタビライザ側の論理エラー率。flux 側が成功したショットに条件付けた値（分母 = shots − n_fail_flux）。**X スタビライザの閾値はこの指標で求めます。**
  - `ler_flux`: 終了時に非自明な X ループが残った割合（Z スタビライザ側）。`ler_combined`: どちらかの失敗（v6 の `logical_error_rate`）。
  - `logical_error_rate`, `n_failures`, `n_trials`: `failure_metric` で選んだ主指標。
  - `mean_infidelity_flux_ok`、`n_fractional_F`、`frac_random_outcomes`（dressed X チェック測定のうち結果が確率 1/2 になった割合）、`jit_flips_per_shot`。
  - v9 の診断: `flux_faces_before_x_per_round`（dressed X 層の直前に残っていたフラックスの面の数の平均）、`frac_rounds_flux_before_x`（フラックスが残っていたラウンドの割合）、`frac_random_outcomes_noflux_rounds`・`frac_rerandomized_ii_noflux_rounds`（フラックスが残っていない層でのランダムな結果の割合。0 でなければ、補正で閉じた $X$ ループが bare な星の積になったときの CZ 型の残差による）、`jit_future_boundary`、`circuit_noise_preset`、`code_version`。
- 交点の推定は、隣り合う L の曲線を log–log で線形補間した記述的なものです（有限サイズスケーリングではありません）。L=3 は復号器の設定の影響を強く受けるため、閾値の評価には大きい L の組（5–7, 7–9）を重視してください。
- 対照実験: `dressing_treatment="none"`（dressing なし）と `"kappa_injection"`（dressing なし + 旧研究の $r=\kappa c p$ 注入）を D4 と同じ設定で実行すると、非可換性（dressing）の効果と、旧研究の近似がそれをどこまで表せるかを比較できます（`run_production()` が自動で行います）。回路レベルの `none` は CCZ ゲートそのものを除くので、差は「非可換性のコスト」ではなく「dressed 測定回路とそれを除いた回路の差」です。
- 回路レベルの交点が `PRODUCTION_P_RANGE` の外に出た場合（`_crossings.csv` が空、または端に近い）は、範囲を広げて取り直してください。
