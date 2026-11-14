from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import stim
except ImportError:
    stim = None

try:
    import tsim
except ImportError:
    tsim = None

try:
    import pymatching
except ImportError:
    pymatching = None

try:
    from scipy.stats import norm

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

CODE_VERSION = "d4_v13"

CFG = dict(
    resume=True,              # v9.2: same configuration only; completed points are not rerun

    # ===== 計算の方式 =====
    engine="twisted_frame",        # "twisted_frame"（dressed X チェックを厳密に扱う。非可換性込み）/ "stim_surrogate"（旧研究のサロゲート: bare MPP + r=κcp）
    dressing_treatment="exact",    # v7: "exact"（D4 符号）/ "none"（dressing なし = 3 枚の Z2 トーリック符号）/ "kappa_injection"（dressing なし + 旧研究の r=κcp 注入）
    failure_metric="charge",       # v7: 図・交点推定の主指標。"charge"（X スタビライザ側。flux 成功ショットに条件付け）/ "combined" / "flux"
    seed=20260927,                 # 乱数の基準 seed（各点の seed はこれと (L, p) から決定論的に作る）
    batch_size=20000,              # twisted_frame エンジンの 1 バッチのショット数（メモリ節約用）
    save_manifest=True,            # v7: 実行条件（CFG 全体・版・日時・環境）を JSON に保存
    # ===== プロトコルと復号器 =====
    logical_colors="rgb",    # 論理状態: x 方向ホロノミーのセクターを重ね合わせる色（"rgb" で 3 論理量、"r" で 1 論理量）
    x_check_order="rgb",     # 1 ラウンド内の dressed X チェックの測定順（色レイヤ）。非可換性はこの順序に依存する
    jit_boundary_offset=1.0, # JIT フラックス復号: 未解決事象が「未来境界」と組むコスト = w_t*(t - t_e + offset)
    # 電荷デコーダ事前分布に入れる r=κcp の κ（ノイズモデルごと。物理の標本化には入らない）。
    # 値は試行計算で最大の L の LER が最小になるものを選んだ（正当化コード (D) で再調整できる）
    # v9.1: 回路レベルは雑音の定義ごと。"circuit_level" は legacy_v7（v7 の調整値）、"circuit_level/uniform" は v9.1 の
    #       正当化 (D) の走査（L=3,5,7, p=0.2% と L=7,9, p=0.15%, 0.25%、本番と別の seed）で最大の L の LER が最小の値
    tf_decoder_kappa={"depolarizing": 0.5, "phenomenological": 0.0, "circuit_level": 0.0, "circuit_level/uniform": 0.1},
    cl_decoder_prior="calibrated",  # v7: CL の電荷デコーダ事前分布。"calibrated"（実回路の故障表から較正）/ "legacy"（v6 と同じ旧 CL サロゲート）
    # v9: 回路レベル雑音の定義。"uniform"（研究 3 のシナリオ B と同じ = Takada et al. App. A2: k 量子ビットゲートの後に
    #     k 量子ビット脱分極 p（CX は 15 通り、ネイティブ CCZ は 63 通り）、準備の後と測定の前に反転 p、アイドル雑音なし、
    #     JIT の X 補正は雑音なし）/ "legacy_v7"（v7 の本番と同じ: 下の circuit_*_scale を使う。CCZ は 3 量子ビットそれぞれ
    #     独立に DEPOLARIZE1、アイドル 0.4p をラウンド冒頭に 1 回）。研究 3 と同じ p の意味で比べるには "uniform"
    circuit_noise_preset="uniform",
    # v9: JIT 復号器の「未来境界」。"auto"（測定誤り率が 0 のときは未来境界を置かない = 全てのフラックスを
    #     その場で空間的に組にする。R1-3）/ "always"（v7 と同じ。測定誤り 0 でも重み _llr(0)=30 の未来境界を置く）
    jit_future_boundary="auto",
    decoder_meas_floor_scale=0.5,   # 電荷デコーダ事前分布の測定反転確率の下限（×p, depolarizing/phenomenological）。測定誤り 0 でも時間方向の辺を確保
    depolarizing_rounds=1,   # depolarizing（符号容量型）の雑音ラウンド数（None なら rounds/L = 旧研究の定義）
    # ===== 旧研究のコードから引き継いだキー =====
    noise_model="phenomenological", #depolarizing, phenomenological, circuit_level
    L_values=[3, 5, 7, 9],   # v9: 本番は L=9 まで（L=11 は 1 点あたりの時間が約 2 倍）
    rounds=None,             # None -> L（depolarizing は depolarizing_rounds が優先）
    shots=100000,            # 研究用（v9 の本番は 1e5 / 点。R1-2, R1-4, R1-5）。動作確認は 2000 程度で
    p_min=None,              # None ならノイズモデル（と回路雑音の定義）ごとの推奨範囲 RECOMMENDED_P_RANGE を使う
    p_max=None,
    p_n=10,
    out_dir="d4_v13_results", # 出力はこのフォルダにまとめる（ファイルの一覧と読み方は 1_D4閾値/README.md「出力ファイル」）
    # ===== v9: 本番の一括実行（run_production）=====
    production_noise_models=["depolarizing", "phenomenological", "circuit_level"],
    production_dressing_treatments=["exact", "none", "kappa_injection"],  # 対照実験も同じ設定で（R1-2）
    confidence_level=0.95,
    out_csv=None,            # None なら "d4_v13_X_memory_<model>_<engine>[_<treatment>].csv"
    out_png=None,            # None なら同じ名前の .png（twisted_frame では 3 指標を並べた 1 枚）
    save_pdf=False,          # v12: 既定では PDF を作らない（論文の図は CSV から 論文草稿/統合論文_v13/scripts/make_figures.py で作る）。
                             #      True にすると各 PNG と同じ名前の PDF も保存する。再開時の設定の照合には含まれない
    print_geometry_summary=True,
    run_self_checks=True,    # twisted_frame では幾何（平坦部分空間での可換性）と p=0 の無失敗を確認
    self_check_shots=300,
    depolarizing_data_scale=1.0,
    depolarizing_meas_scale=0.0,     # 符号容量型（測定は完全）。旧研究の定義（= phenomenological と同じ物理）は 1.0 かつ depolarizing_rounds=None
    depolarizing_dressing_scale=0.5, # 旧研究のサロゲートの κ_depol（stim_surrogate と kappa_injection で使用）
    depolarizing_dressing_mode="pairwise_graphlike",
    phenomenological_data_scale=1.0,
    phenomenological_meas_scale=1.0,
    phenomenological_kickback_scale=0.25,  # 旧研究のサロゲートの κ_pheno
    # ----- 以下の circuit_*_scale は circuit_noise_preset="legacy_v7"（と旧研究のサロゲート）のときだけ使う -----
    circuit_init_scale=0.60,
    circuit_1q_scale=0.35,
    circuit_2q_scale=1.00,
    circuit_noncliff_scale=1.00,     # twisted_frame: ネイティブ CCZ ゲート直後に 3 量子ビットそれぞれ DEPOLARIZE1(この値×p)
    circuit_idle_scale=0.40,
    circuit_meas_scale=1.00,
    circuit_kickback_scale=0.6,      # 旧研究のサロゲートの κ_circ
)

# ノイズモデルごとの推奨 p 範囲。v9: v7 の本番（1e4 ショット）の交点の付近に絞った（R1-4, R1-5）。
#   circuit_level は回路雑音の定義ごと（"uniform" の範囲は v9 の試行計算 L=3,5,7・3000 ショットで、
#   charge の交点が 0.20–0.22% 付近にあることを確かめて決めた）。
RECOMMENDED_P_RANGE = {
    "depolarizing": (8.5e-2, 1.1e-1),
    "phenomenological": (1.7e-2, 2.6e-2),
    "circuit_level": (1.6e-3, 2.6e-3),           # legacy_v7 の交点（0.19–0.24%）付近
    "circuit_level/uniform": (1.2e-3, 3.0e-3),   # v9.1 の uniform（kappa_dec=0.1。試行で交点 0.16%(L3-5), 0.21%(L5-7)）
}
# 対照実験を含む本番（run_production）の範囲: (noise_model, dressing_treatment) -> (p_min, p_max)。
#   v7 の試行計算（none, kappa_injection）と v9 の試行計算（circuit_level/uniform の none: 交点 約 0.6%、
#   kappa_injection: 約 0.3–0.4%）から決めた。交点が範囲の外に出たら（crossings の CSV が空なら）範囲を広げて取り直す。
#   circuit_level の値は "uniform" のもの（"legacy_v7" で exact を計算する場合は RECOMMENDED_P_RANGE を使う）。
PRODUCTION_P_RANGE = {
    ("depolarizing", "exact"): (8.0e-2, 1.15e-1),
    ("depolarizing", "none"): (8.0e-2, 1.2e-1),
    ("depolarizing", "kappa_injection"): (5.0e-2, 1.4e-1),
    ("phenomenological", "exact"): (1.7e-2, 2.6e-2),
    ("phenomenological", "none"): (2.2e-2, 3.4e-2),
    ("phenomenological", "kappa_injection"): (1.7e-2, 2.8e-2),
    ("circuit_level", "exact"): (1.2e-3, 3.0e-3),
    ("circuit_level", "none"): (3.5e-3, 1.0e-2),
    ("circuit_level", "kappa_injection"): (2.0e-3, 6.0e-3),
}
