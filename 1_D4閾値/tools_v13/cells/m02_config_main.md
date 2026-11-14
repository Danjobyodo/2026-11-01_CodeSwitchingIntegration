[Cell 2] Setup & Config

各パラメータの意味は下の CFG のコメントと論文（研究 1 の方法）を参照してください。
- `failure_metric="charge"`: X スタビライザ（電荷側）の閾値を求めるための主指標。`combined` はどちらかの失敗。
- `dressing_treatment`: `"exact"` が D4 符号。`"none"`・`"kappa_injection"` は対照実験です（論文の比較図用）。
- `circuit_noise_preset`: `"uniform"`（研究 3 と同じ雑音の定義、既定）/ `"legacy_v7"`（以前の定義。保存済みの回路レベルの本番データはこれで計算した）。
- `jit_future_boundary`: `"auto"`（測定誤り 0 なら未来境界なし、既定）/ `"always"`（測定誤り 0 でも未来境界を置く、以前の既定）。
- `depolarizing` は符号容量型（測定誤りなし・雑音 1 ラウンド）です。旧研究の定義（測定誤りあり、R=L）は `depolarizing_meas_scale=1.0, depolarizing_rounds=None` で、phenomenological と同じ物理になります。
- `p_min=None, p_max=None` のときは、ノイズモデル（と回路雑音の定義）ごとの推奨範囲 `RECOMMENDED_P_RANGE` を使います。`run_production()` は `PRODUCTION_P_RANGE` を使います。
