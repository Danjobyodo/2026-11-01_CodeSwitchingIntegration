[Cell 2] Setup & Config

各パラメータの意味と、正当化コードのパラメータとの対応は `実装と未解決事項_v9.md` にまとめました。
- `failure_metric="charge"`: X スタビライザ（電荷側）の閾値を求めるための主指標。`combined` は v6 の `logical_error_rate` と同じです。
- `dressing_treatment`: `"exact"` が D4 符号。`"none"`・`"kappa_injection"` は対照実験です（論文の比較図用）。
- `circuit_noise_preset`（v9）: `"uniform"`（研究 3 と同じ雑音の定義、既定）/ `"legacy_v7"`（v7 の本番と同じ）。
- `jit_future_boundary`（v9）: `"auto"`（測定誤り 0 なら未来境界なし、既定）/ `"always"`（v7 と同じ）。
- `depolarizing` は符号容量型（測定誤りなし・雑音 1 ラウンド）です。旧研究の定義（測定誤りあり、R=L）は `depolarizing_meas_scale=1.0, depolarizing_rounds=None` で、phenomenological と同じ物理になります。
- `p_min=None, p_max=None` のときは、ノイズモデル（と回路雑音の定義）ごとの推奨範囲 `RECOMMENDED_P_RANGE` を使います。`run_production()` は `PRODUCTION_P_RANGE` を使います。
