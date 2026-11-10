# ==================================================================================================
# V1 W の式を支える恒等式（群コチェイン。格子を使わない）
#   bulk          : delta alpha_N = ねじれの変化  (mod 2 pi)
#   level k->k+1  : alpha_{N-k} を部分群（b_1 = 他の色の和）に制限したもの = (1/2) delta alpha_{N-k-1}  (mod 2^(k+1) pi)
#   exact         : 上の式が有理数の等式として（mod を取らずに）成り立つこと。理論ノート 付録 A の命題
# ==================================================================================================
rows = []
for N in range(2, V1_N_MAX + 1):
    rows += group_cochain_checks(N, max_points=MAX_POINTS, seed=SEED)
V1 = pd.DataFrame(rows)
display(V1)
record('V1a 群コチェインの恒等式（bulk と層の列）', (V1.violations == 0).all(),
       f'N = 2..{V1_N_MAX}、{len(V1)} 個の式、全点を調べた式 {int(V1.exhaustive.sum())} 個')

rng = np.random.default_rng(SEED)
bad, info = 0, []
for n in range(2, V1_N_MAX + 1):                       # n = 生きている色の数。alpha_{n+1} の式
    H, ex = _points(n - 1, n, MAX_POINTS, rng)
    par = np.zeros(H.shape, dtype=np.int64)
    for b in range(n - 1):
        par ^= (H >> b) & 1
    big = (H & 1) | (par << 1) | ((H >> 1) << 2)
    diff = 2 * _alpha_points(big, 0) - _delta_points(lambda X: _alpha_points(X, 0), H)     # mod を取らない
    bad += int(np.count_nonzero(diff)); info.append(f'm={n + 1}:{"全点" if ex else "標本"}')
record('V1b 層の式は有理数の等式として厳密（mod なし）', bad == 0, ', '.join(info))
