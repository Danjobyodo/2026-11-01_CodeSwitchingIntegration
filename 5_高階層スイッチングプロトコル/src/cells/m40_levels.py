# ==================================================================================================
# §4 各操作が Clifford 階層のどの階層にあるか（式から決まる。格子の大きさによらない）
#   階層 1 = Pauli、2 = Clifford、3 = T や CCZ、4 = sqrt(T) や CCCZ、...
#   C^q Z（制御 q 個）は階層 q+1、制御 q 個で角度 pi/2^j の位相ゲートは階層 q+j+1。
# ==================================================================================================
rows = []
for N in range(2, 8):
    lat = Lattice(N, (1,) * (N - 1))
    inv = gate_inventory(lat)
    names = []
    for g in inv:
        q, den = g['qubits_per_gate'], g['angle_denominator']
        names.append(f"{q} 量子ビット・角度 pi/{den}")
    rows.append({'N': N, '空間次元': N - 1, '論理ゲート': f'R_{N} = diag(1, e^(2 pi i/{2 ** N}))',
                 '安定化子の修飾': f'C^{N - 2}Z（階層 {N - 1}）' if N > 2 else 'Z（階層 1）',
                 '検査の測定に要るゲート': f'C^{N - 1}Z（階層 {N}）' if N > 2 else 'CZ（階層 2）',
                 'W のゲート': '; '.join(names), 'W のゲートの階層': sorted({g['hierarchy_level'] for g in inv}),
                 'switch-out の補正': f'C^{N - 2}Z（階層 {N - 1}）' if N > 2 else 'Z（階層 1）',
                 '補正を Pauli フレームで追えるか': '追える' if N <= 2 else ('Clifford（物理ゲートでかける）' if N == 3 else '追えない（非 Clifford の物理ゲートが要る）')})
LEVELS = pd.DataFrame(rows)
LEVELS.to_csv(os.path.join(OUT_DIR, 'study5_levels.csv'), index=False)
display(LEVELS)
