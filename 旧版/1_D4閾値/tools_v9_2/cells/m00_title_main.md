# D4 符号 X スタビライザの閾値シミュレーション — v9.2（メインのシミュレーションコード）

**実行環境: Google Colab の CPU ランタイムで実行できます（GPU は不要）。** 重い部分は numba で高速化しています。
正当化コードは別ノートブック `D4_v9_2_validation.ipynb`（こちらは GPU 推奨）です。両ノートブックの共通コードは
`tools_v9_2/cells/` の同じソースから `tools_v9_2/build_notebooks_v9_2.py` で生成しているので、必ず同じです。

**v9.2（2026-11-02）**：メインの物理・復号器・乱数は v9 と同じ（同じ設定なら同じ結果）。変更は版の表記と出力名（`d4_v9_2_*`）だけで、正当化ノートに Pauli proxy による $L\le9$ の突き合わせ (E) を加えた。

**v9 の変更点**（2026-11-02。3 研究の版番号を 9 に統一。詳細は `実装と未解決事項_v9.md`）:
1. **回路レベル雑音の定義を研究 3 と統一**（`circuit_noise_preset="uniform"`、既定）: k 量子ビットゲートの後に k 量子ビット脱分極 $p$（CX は 15 通り、**ネイティブ CCZ は 63 通りの 3 量子ビット脱分極**）、準備の後・測定の前に反転 $p$、アイドル雑音なし（研究 3 のシナリオ B、Takada et al. App. A2）。v7 の定義（CCZ の 3 量子ビットそれぞれに独立な $\mathcal D_1(p)$ など）は `"legacy_v7"` で同じ乱数列のまま再現できます。
2. **完全測定（符号容量型）では JIT 復号器に未来境界を置かない**（`jit_future_boundary="auto"`）。$L\le9$ では v7 と同じ結果になることを確認済み（全てのフラックスが dressed 測定の前に除かれる）。
3. **診断量の追加**（R1-3）: dressed $X$ 層の直前に残っていたフラックスの数、フラックスが残っていない層での「ランダムな測定結果」の割合（CSV の `flux_faces_before_x_per_round`, `frac_random_outcomes_noflux_rounds` など）。
4. **本番の一括実行** `run_production()`: 3 雑音モデル × D4（exact）と対照実験（none, kappa_injection）を、同じ $L$（既定 3, 5, 7, 9）・同じショット数（既定 $10^5$）・交点付近の $p$ で実行し、対照実験の重ね描き（論文の Fig. 4）を作ります（R1-2, R1-4, R1-5）。
5. ログの表示を engine・dressing の扱いに合わせた（R1-8）。出力は `out_dir`（既定 `d4_v9_2_results/`）にまとめます。

物理を計算する中核（twisted-frame エンジン、JIT フラックス復号、終了処理）は v7 と同じです。

使い方: Cell 2 で `noise_model`（`depolarizing` / `phenomenological` / `circuit_level`）を選び、上から順に実行します（最後のセルの `run_experiments()` は 1 条件、`run_production()` は本番の一括実行）。最初は `shots=2000` 程度で動作確認してください。
