# 研究 4：連続 T ゲートでの code switching の償却

元の方針（`研究4_方針と理論的考察.md` §1）は「switch-in の後に複数の非 Clifford ゲートをかければ、魔法状態蒸留より有利になる場面があるのではないか」。理論的に検討して、問いを「**同じ論理量子ビットに $T$ ゲートを続けてかけるとき、$T$ 1 個あたりの誤りと体積はどう変わるか**」に改め、研究 3 のシミュレーションを $K$ 回連続のサイクルに拡張した。

## どこを読むか

| 目的 | ファイル |
|---|---|
| 方針をどう改めたか、理論的な結論、シミュレーションの設計 | `研究4_方針と理論的考察.md` |
| 試行計算の結果と、そこから言えること・言えないこと | `研究4_結果.md` |
| Colab で実行する | `研究4_main.ipynb`（本体）、`研究4_validation.ipynb`（正当化） |

## ファイル

| ファイル | 内容 |
|---|---|
| `研究4_main.ipynb` | **本体**。セル 1：インストール、セル 2：パラメータ（変更するのはここだけ）。モンテカルロ → 集計 → 1 サイクルあたりの誤り → 費用の比較 → 図。既定の `RUN_MODE='quick'` は数分。`'analysis_only'` は埋め込みの試行データを解析するだけ |
| `研究4_validation.ipynb` | **正当化**。$K=1$ が研究 3 と同一（V1）、雑音なしで誤り 0（V2）、真の非 Clifford 回路との照合（V3）、負の対照（V4）、その他（V5）。最後に `VALIDATION PASSED` |
| `src/seq_lib.py` | 研究 4 で新しく書いたライブラリ（連続サイクルの回路・復号器・実験・体積の数え上げ）。研究 3 のクラスのサブクラス |
| `src/cells/` | ノートの各セルの正規ソース |
| `src/build_notebooks.py` | ノートの再生成（研究 3 の物理ライブラリを `../3_魔法状態蒸留との比較/D4_noisy_simulation.ipynb` からそのまま取り込む） |
| `results_pilot/` | この環境で実行した試行計算（`study4_mc.csv` が生データ、他は本体ノートの解析結果と図） |
| `検証ログ/` | 正当化ノートの完全版の実行結果 |
| `../tests/test_study4.py` | 回帰テスト（`python -m unittest tests.test_study4 -v`） |

## Colab での実行

1. `研究4_validation.ipynb` を開き、上から全て実行する（既定の `QUICK=True` で約 1 分、`QUICK=False` の完全版で 5〜10 分）。`VALIDATION PASSED` を確認する。
2. `研究4_main.ipynb` を開き、セル 2 の `RUN_MODE` を選んで上から全て実行する。
   * `'quick'`：動作確認（数分）。
   * `'pilot'`：`results_pilot/` と同じ計算。
   * `'production'`：本番（セル 2 の `PLAN['production']`。点とショット数は自由に書き換えてよい）。長時間になるので `USE_GOOGLE_DRIVE=True` にして出力を Drive に置くとよい。途中で切れても、同じ設定で実行し直せば続きから計算する（`RESUME=True`）。
   * `'analysis_only'`：計算せず、`OUT_DIR` の CSV（無ければ埋め込みの試行データ）を解析する。
3. 出力は `OUT_DIR`（既定 `results_study4/`）：`study4_mc.csv`（生データ）、`study4_summary.csv`、`study4_per_cycle.csv`、`study4_gap_effect.csv`、`study4_amortized_cost.csv`、`study4_verdict.txt`、図 2 枚。

ノートは単独で動く（他のファイルを読み込まない）。GPU は不要。`WORKERS` は CPU のコア数に合わせる。

## 研究 3 との関係

* 回路・雑音・復号器・Pauli proxy 法は研究 3 と同じ。研究 3 のコードは変更していない（ノートに埋め込んだライブラリが研究 3 と同一であることを回帰テストが確認する）。
* $K=1$ は研究 3 の回路そのもので、同じ seed なら 1 ショットごとに同じ結果になる。
* 費用の比較は、研究 3 の比較表（`../3_魔法状態蒸留との比較/results_v11/cost_comparison.csv`）に、回路から数えた償却係数を掛けたもの。研究 3 の統計的な判定（データで保証／棄却）はそのまま引き継ぐ。
