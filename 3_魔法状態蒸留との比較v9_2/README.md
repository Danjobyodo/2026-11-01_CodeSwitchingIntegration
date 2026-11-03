# 研究3 v9.2：カテゴリ統計と到達判定の修正

v9/v6 の物理回路・雑音・復号器を保持し、解析とMCの停止規則を修正した。旧版は `../3_魔法状態蒸留との比較v9/` に残る。v9.2は独立したフォルダで、ノートは共通コードと解析モジュールを埋込み済みのため単独でColabに持ち込める。

## 最初に実行するもの

新規物理Monte Carloより先に **`noisy_cost_comparison.ipynb`** をCPUで実行する。既定 `DATA_MODE='reference'` は `data/` に固定した最新の2 run_id の本番データと同じもの。旧フォルダの `results/` は入力にしない。

- 出力は作業ディレクトリの `results_v9_2/` と `figures_v9_2/`。
- `N_BOOT=200`。最適化の失敗は停止し、成功・境界・反復を全件JSONに保存する。
- `cost_comparison.csv` の `kobayashi_status=data_certified` は、逐次停止と最大200点の選択を保護したデータ上の候補保証。真の最小費用の確定は `minimum_resolved` が別に必要。
- `kobayashi_model_status=model_supported` はモデル条件付きbootstrap支持。保証ではなく、実測点の未確定を上書きしない。モデルの費用・倍率は `_model_` 列。
- Litinski側は文献の中央誤り予算。両方式に同じ統計保証があるとの主張はしない。

ローカルでは以下でも同じ比較ノートを実行できる。

```bash
python 3_魔法状態蒸留との比較v9_2/run_comparison.py --output-dir /path/to/new/run --n-boot 200
```

## 追加ショットが必要な場合

`D4_noisy_simulation.ipynb` は `QUICK=True` が既定。まず動作確認してから、CPUで `QUICK=False` を設定する。v9.2の主な設定：

| 設定 | 内容 |
|---|---|
| `SHOTS_PER_POINT` | 通常実行の各点の累積目標。quickは400、本番既定100000。計算前に決める |
| `RUN='extend'` | `EXTEND` の点へ各 `EXTEND_SHOTS` を追加。新規の点は通常目標まで |
| `EXTEND_SHOTS` | 追加ショット数、既定100000。旧 `EXTEND_SECONDS` は廃止 |
| `RESUME=True` | 同じ物理点の完了chunkを再利用。RUN='extend'では自動True |
| `WORKERS` | CPU数とメモリに合わせる。旧runの再現はライブラリ版も記録 |

失敗件数や壁時計時間で止めず、固定ショット数を使う。実行中断はchunkごとの保存から再開する。RESUME=Falseで既存CSVがあれば上書きせずエラーにする。旧chunkを新しいrun_idに付け替えて複製しても、独立データとして加算してはいけない。解析時に同じ物理点・seedの重複を拒否する。

新しいMC／較正CSVを比較ノートの `results_v9_2/` に配置して `DATA_MODE='production'` を選ぶ。referenceのままでは追加ショットは反映されない。quickの小標本ではモデル同定の検査で停止する場合があり、それは本番解析が通ったことを意味しない。

`validation.ipynb` の物理テストはv9と同一。物理コードを変えていない本改訂で、189 PASSの旧記録をv9.2で新たに全実行した結果とは扱わない。

## 保守と検証

`analysis_v9_2.py` が統計の正規ソース、`cells/` が比較セルのソース。変更後は `python .../build_notebooks_v9_2.py` で3ノートを再生成する。旧ノートを直接書き換えない。原始データの完全なSHA-256は `data/provenance.json`、解析コードSHAは各比較表に記録する。

リポジトリ直下で `python -m unittest discover -s tests_v9_2 -v` を実行する。方法と保証の仮定は `methods_v9_2.md`、この環境の再解析結果は `再解析結果_v9_2.md` を参照。

統計だけをColabで先に確認する場合は `3_魔法状態蒸留との比較v9_2/statistics_validation_v9_2.ipynb`（同フォルダからはファイル名のみ）を実行し、`STATISTICS VALIDATION PASSED` と `results_v9_2/statistics_validation.json` を保存する。物理の全validationを代替するものではない。
