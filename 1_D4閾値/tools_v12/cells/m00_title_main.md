# D4 符号 X スタビライザの閾値シミュレーション — v12（メインのシミュレーションコード）

**実行環境: Google Colab の CPU ランタイム（GPU は不要）。** 重い部分は numba で高速化しています。
正当化コードは別ノートブック `D4_v12_validation.ipynb`（GPU 推奨）です。両ノートブックの共通コードは
`tools_v12/cells/` の同じソースから `tools_v12/build_notebooks_v12.py` で生成しているので、必ず同じです。

**Colab での所要時間の目安**（この研究の実測：1 ショットあたり $p=2\%$ の現象論的雑音で $L=3,5,7,9$ がそれぞれ約 0.3, 0.9, 2.2, 6.3 ms。Colab の CPU はこれと同程度〜1.5 倍遅い）

| 実行するもの | 目安 |
|---|---|
| 上から最後まで（既定。長い計算のセルはコメントアウトしてある） | 約 1〜2 分（インストールと定義だけ） |
| `run_experiments()`：1 条件、既定の CFG（$L=3$–9、10 点、$10^5$ ショット/点）、現象論的雑音 | 約 3〜4 時間 |
| 同、動作確認（`CFG["shots"]=2000`） | 約 3〜5 分 |
| `run_production(noise_models=["phenomenological"])`（D4・none・kappa_injection の 3 種）＝統合論文に必要な本番 | 約 10〜15 時間 |
| 同、`"depolarizing"`（符号容量型、1 ラウンド） | 約 1〜3 時間 |
| 同、`"circuit_level"` | 現象論的の数倍（未計測。研究 1 単独の原稿でだけ使う） |

途中で止まっても、同じ設定・同じ `out_dir` で同じセルを実行すれば、完了した点は再計算せずに引き継ぎます。

**出力**（`CFG["out_dir"]`、既定 `d4_v12_results/`。1 条件あたり 5 ファイル。詳しい読み方は `1_D4閾値/README.md`「出力ファイル」）：
`<tag>.csv`（結果の表）、`<tag>.png`（charge・flux・combined の 3 指標を並べた図 1 枚）、`<tag>_crossings.csv`（交点）、
`<tag>_manifest.json`（実行条件と環境）、`<tag>_checkpoint.json`（再開用）。`run_production()` は雑音モデルごとに
D4 と対照実験を重ねた `d4_v12_treatment_comparison_<model>_charge.png` も作ります。`<tag>` は
`d4_v12_X_memory_<model>_twisted_frame[_<treatment>][_<preset>]`。

**v12（2026-11-12）**：物理・乱数・判定は v9〜v11 と同じ。出力を研究に必要なものに絞った（主指標だけの図と 3 指標の図が重複していたので 3 指標の図 1 枚に、PDF は既定で作らない）。同じ出力先に v11・v10 のチェックポイント（`d4_v11_*`・`d4_v10_*_checkpoint.json`）があり、設定が版の表記以外すべて一致するときは、その完了点を引き継ぐ（旧ファイルは変更しない）。全体の記録は `../旧版/v12/利用者向け__v12_改訂の記録と判断.md`。

**それ以前**：v9.1 で正当化ノートに Pauli proxy による $L\le9$ の突き合わせ (E) を加え、回路レベル `uniform` の電荷復号器の事前分布を $\kappa_{\rm dec}=0.1$ にした。v9.2 で再開機能（原子的な JSON チェックポイント）を加え、長時間の計算は既定で実行しないようにした。v10・v11 は版の表記・出力名と、旧版のチェックポイントの引き継ぎ。

**v9 の変更点**（2026-11-02。3 研究の版番号を 9 に統一。詳細は `../旧版/1_D4閾値/実装と未解決事項_v9.md`）:
1. **回路レベル雑音の定義を研究 3 と統一**（`circuit_noise_preset="uniform"`、既定）: k 量子ビットゲートの後に k 量子ビット脱分極 $p$（CX は 15 通り、**ネイティブ CCZ は 63 通りの 3 量子ビット脱分極**）、準備の後・測定の前に反転 $p$、アイドル雑音なし（研究 3 のシナリオ B、Takada et al. App. A2）。v7 の定義（CCZ の 3 量子ビットそれぞれに独立な $\mathcal D_1(p)$ など）は `"legacy_v7"` で同じ乱数列のまま再現できます。
2. **完全測定（符号容量型）では JIT 復号器に未来境界を置かない**（`jit_future_boundary="auto"`）。$L\le9$ では v7 と同じ結果になることを確認済み（全てのフラックスが dressed 測定の前に除かれる）。
3. **診断量の追加**（R1-3）: dressed $X$ 層の直前に残っていたフラックスの数、フラックスが残っていない層での「ランダムな測定結果」の割合（CSV の `flux_faces_before_x_per_round`, `frac_random_outcomes_noflux_rounds` など）。
4. **本番の一括実行** `run_production()`: 3 雑音モデル × D4（exact）と対照実験（none, kappa_injection）を、同じ $L$（既定 3, 5, 7, 9）・同じショット数（既定 $10^5$）・交点付近の $p$ で実行し、対照実験の重ね描きを作ります（R1-2, R1-4, R1-5）。
5. ログの表示を engine・dressing の扱いに合わせた（R1-8）。

物理を計算する中核（twisted-frame エンジン、JIT フラックス復号、終了処理）は v7 と同じです。

使い方: Cell 2 で `noise_model`（`depolarizing` / `phenomenological` / `circuit_level`）を選び、上から順に実行します（最後のセルの `run_experiments()` は 1 条件、`run_production()` は本番の一括実行）。最初は `shots=2000` 程度で動作確認してください。
