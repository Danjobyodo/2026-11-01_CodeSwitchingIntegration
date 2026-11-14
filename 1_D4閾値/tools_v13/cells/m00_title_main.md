# D4 符号 X スタビライザの閾値シミュレーション — v13（メインのシミュレーションコード）

**実行環境: Google Colab の CPU ランタイム（GPU は不要）。** 重い部分は numba で高速化しています。
正当化コードは別ノートブック `D4_v13_validation.ipynb`（GPU 推奨）です。両ノートブックの共通コードは
`tools_v13/cells/` の同じソースから `tools_v13/build_notebooks_v13.py` で生成しているので、必ず同じです。

**Colab での所要時間の目安**（この研究の実測：1 ショットあたり $p=2\%$ の現象論的雑音で $L=3,5,7,9$ がそれぞれ約 0.3, 0.9, 2.2, 6.3 ms。Colab の CPU はこれと同程度〜1.5 倍遅い）

| 実行するもの | 目安 |
|---|---|
| 上から最後まで（既定。長い計算のセルはコメントアウトしてある） | 約 1〜2 分（インストールと定義だけ） |
| `run_experiments()`：1 条件、既定の CFG（$L=3$–9、10 点、$10^5$ ショット/点）、現象論的雑音 | 約 3〜4 時間 |
| 同、動作確認（`CFG["shots"]=2000`） | 約 3〜5 分 |
| `run_production(noise_models=["phenomenological"])`（D4・none・kappa_injection の 3 種）＝論文の本番 | 約 10〜15 時間 |
| 同、`"depolarizing"`（符号容量型、1 ラウンド） | 約 1〜3 時間 |
| 同、`"circuit_level"` | 現象論的の数倍（未計測。論文の主結果には使わない） |

途中で止まっても、同じ設定・同じ `out_dir` で同じセルを実行すれば、完了した点は再計算せずに引き継ぎます。

**出力**（`CFG["out_dir"]`、既定 `d4_v13_results/`。1 条件あたり 5 ファイル。詳しい読み方は `1_D4閾値/README.md`「出力ファイル」）：
`<tag>.csv`（結果の表）、`<tag>.png`（charge・flux・combined の 3 指標を並べた図 1 枚）、`<tag>_crossings.csv`（交点）、
`<tag>_manifest.json`（実行条件と環境）、`<tag>_checkpoint.json`（再開用）。`run_production()` は雑音モデルごとに
D4 と対照実験を重ねた `d4_v13_treatment_comparison_<model>_charge.png` も作ります。`<tag>` は
`d4_v13_X_memory_<model>_twisted_frame[_<treatment>][_<preset>]`。

物理を計算する中核は、twisted-frame エンジン（Cell 7）、JIT フラックス復号と終了処理（Cell 8）です。`run_experiments()` と `run_production()` は、同じ出力先に同じ設定で計算した以前の版（v10〜v12）のチェックポイントがあれば、その完了点を再計算せずに引き継ぎます。変更履歴はリポジトリの `CHANGELOG.md`。

使い方: Cell 2 で `noise_model`（`depolarizing` / `phenomenological` / `circuit_level`）を選び、上から順に実行します（最後のセルの `run_experiments()` は 1 条件、`run_production()` は本番の一括実行）。最初は `shots=2000` 程度で動作確認してください。
