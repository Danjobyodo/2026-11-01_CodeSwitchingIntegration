# 研究 2：code switching の論理誤り率（現象論的雑音）— v10

方法（Pauli proxy 法、厳密性の条件 C1–C3、復号器）と結果の正式な説明は `../論文草稿/研究まとめ_論文草稿_v10.md`（研究 2 の節）。旧版（v3, v9, v9.2 の再集計）は `../旧版/2_CodeSwitching論理誤り率/`。

| ファイル | 内容 |
|---|---|
| `CHSC_switch_v10_main.ipynb` / `chsc_switch_v10.py` | メイン（Colab CPU）。既定は本番の設定（3 ケース × ideal/noisy、$d=3,5,7$、20,000 ショット/点） |
| `CHSC_switch_v10_validation.ipynb` / `chsc_validation_v10.py` | 正当化（総当たり・独立エンジン・本番経路の再生。CPU で約 2 分。`VALIDATION PASSED`） |
| `make_notebooks_v10.py` | .py から 2 つのノートを生成 |
| `summarize_results_v10.py` | 本番 CSV から $P_L$ と平均不忠実度を再計算（`本番結果/指標の再集計/`） |
| `本番結果/chsc_v9_results/` | 本番の 5 条件（v9 のコード＝v10 と同じ物理、2026-11-02 実行） |
| `本番結果/chsc_v3_results/` | `in_T_out`・ideal の本番（v3 のコード、Colab。v10 と全ショット同じ標本） |
| `検証ログ/` | v9 の正当化の全ログ、復号器の比較（試行）、v10 の正当化のログ |

* v10 の変更は版の表記だけ（物理・復号器・乱数の使い方は v9 と同一）。v9 で計算した CSV にも、同じ条件なら v10 のコードで再開・追記できる（`EQUIVALENT_CODE_VERSIONS`）。
* 288 万ショットの本番は完了しているので、版番号のために取り直す必要はない。$d=9$ の追加や交点付近の統計の追加は任意（別の `out_dir` と seed で）。
