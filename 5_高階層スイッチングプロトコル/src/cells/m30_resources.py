# ==================================================================================================
# §3 資源の数え上げ（立方体の格子 L^(N-1)。本研究の Kuhn 三角形分割での値）
#   qubits                : 物理量子ビット数（データ。境界条件で固定されるものを除く）。うち qubits_pauli は Pauli 符号の分
#   X の重み / 修飾ゲート  : switch-in で測る安定化子 S^s_v の X の数と、付随する C^(N-2)Z の数（最大値）
#   W のゲート            : 論理ゲートを構成する多体位相ゲートの総数、1 量子ビットが関わる数の最大値
#   X 誤りの広がり         : 1 個の X 誤りが U を通った後に関わりうる量子ビット数の上界（W で同じゲートに入る量子ビット）
#   d_X, d_Z              : Pauli 符号の距離（整数計画法。* は時間切れで上界）
# ==================================================================================================
rows = []
for N, L in CASES['resources']:
    lat = Lattice(N, (L,) * (N - 1))
    r = resource_row(lat)
    rows.append(dict(N=N, L=L, 頂点=r['vertices'], 辺=r['edges'], qubits=r['qubits'], qubits_pauli=r['qubits_pauli_code'],
                     switch_in_検査数=r['n_switch_in_checks'], Xの重み=r['switch_in_check_X_weight_max'],
                     修飾ゲート=r['switch_in_check_dressing_gates_max'], 修飾ゲートの量子ビット=r['dressing_gate_qubits'],
                     W_ゲート総数=r['W_gates_total'], W_1量子ビットあたり最大=r['W_gates_per_qubit_max'],
                     X誤りの広がり_最大=r['X_error_spread_max'], X誤りの広がり_平均=round(r['X_error_spread_mean'], 2)))
RES = pd.DataFrame(rows)
dist = []
for N, L in CASES['distances']:
    d = pauli_code_distances(Lattice(N, (L,) * (N - 1)), time_limit=DISTANCE_TIME_LIMIT)
    dist.append(dict(N=N, L=L, d_X=f"{d['d_X']}{'' if d['d_X_optimal'] else '*'}", d_Z=f"{d['d_Z']}{'' if d['d_Z_optimal'] else '*'}"))
DIST = pd.DataFrame(dist)
RES = RES.merge(DIST, on=['N', 'L'], how='left')
RES.to_csv(os.path.join(OUT_DIR, 'study5_resources.csv'), index=False)
display(RES)

# 量子ビット数の L 依存性（最小二乗で qubits = c * L^(N-1) の主要項を確かめる）
for N in sorted(RES.N.unique()):
    sub = RES[(RES.N == N) & (RES.L >= 2)]
    if len(sub) >= 2:
        slope, icpt = np.polyfit(np.log(sub.L), np.log(sub.qubits), 1)
        print(f'N={N}: qubits ~ {math.exp(icpt):.1f} * L^{slope:.2f}（L>=2 の {len(sub)} 点。空間次元は {N - 1}）')
