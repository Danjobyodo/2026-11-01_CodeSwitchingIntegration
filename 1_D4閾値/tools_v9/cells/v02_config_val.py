# ===== 正当化専用の設定 =====
VCFG = dict(
    noise_models=["depolarizing", "phenomenological", "circuit_level"],  # 順に実行（1 つだけでも可）
    L=3,                     # 正当化は L=3 で行う（L=2 は辺の同一視が起きるため不可、L=5 は密な計算が不可能）
    logical_colors="r",      # 内部で使用（(C) は ler_logical_colors を順に代入）
    ler_logical_colors=["r", "rgb"],  # v9: (C) を行う論理セクター（R1-6）。"r": k=25 (2^25 振幅, 約 130 MB/配列)、
                                      #     "rgb": k=27（4 倍。メインの本番と同じセクター。T4 で可）
    compare_metric="charge", # (C) の図の指標（"charge" / "combined"）。数値の比較は両方を表示する
    # 比較する p（L=3、各モデルの交点付近を含む）
    p_values={
        "depolarizing": [0.04, 0.06, 0.08, 0.10, 0.12, 0.14],
        "phenomenological": [0.010, 0.015, 0.020, 0.025, 0.030, 0.040],
        "circuit_level": [0.0005, 0.001, 0.0015, 0.002, 0.003, 0.004],
    },
    shots_exact=2000,        # 密な厳密計算のショット数 / 点（GPU: 1 ショット 0.1–1 秒程度）
    shots_tf=50000,          # メインと同じ twisted-frame 経路のショット数 / 点
    shots_surrogate=20000,   # 旧研究のサロゲートのショット数 / 点 / κ
    # 旧研究のサロゲートで掃引する κ（旧研究の値を含む。0 は dressing 注入なし）
    old_kappa_sweep={
        "depolarizing": [0.0, 0.5, 1.0],
        "phenomenological": [0.0, 0.25, 0.5],
        "circuit_level": [0.0, 0.6, 1.2],
    },
    run_lockstep_test=True,  # (B) ロックステップ厳密性テスト
    lockstep_logical_colors=["r", "rgb"],          # v7: メインの本計算と同じ "rgb" でも検査する
    lockstep_shots={"r": 30, "rgb": 10},
    lockstep_p={"depolarizing": 0.10, "phenomenological": 0.04, "circuit_level": 0.005},  # 故障が多く出る高めの p
    lockstep_tol=1e-3,       # 確率の許容差（float32 の丸め誤差は ~1e-7）
    # (D, 任意) 電荷デコーダ事前分布 κ_dec の調整（正当化ではなく復号器の調整。L=3 以外も使う）
    run_decoder_kappa_scan=False,
    decoder_scan_L=[3, 5, 7],
    decoder_scan_shots=20000,
    decoder_scan_logical_colors="rgb",   # メインと同じ論理量で評価
    decoder_scan_p={"depolarizing": 0.095, "phenomenological": 0.021, "circuit_level": 0.002},  # 交点付近
    decoder_scan_kappas={"depolarizing": [0.0, 0.25, 0.5, 1.0], "phenomenological": [0.0, 0.1, 0.25],
                         "circuit_level": [0.0, 0.1, 0.25, 0.5]},
    out_dir="d4_v9_validation_results",  # v9: 出力先（d4_v9_validation_L3_<model>[_<preset>]_*.csv / png / json）
    run_old_surrogate=True,  # (C) で旧研究のサロゲートも参考として評価する
    save_pdf=True,
    noise_model=None,        # 内部で使用（noise_models を順に代入）
)