# ==================================================================================================
# モンテカルロ本体
#   1 点 = (シナリオ, p, d, K, gap, 窓)。1 点のショットをチャンクに分け、チャンクごとに CSV に 1 行を追記する。
#   ショット数は固定（失敗数や時間では止めない）。seed は (BASE_SEED, 点, チャンク番号) だけで決まる。
# ==================================================================================================
import time, zlib, uuid, datetime, multiprocessing as _mp

MC_CSV = f'{OUT_DIR}/study4_mc.csv'
MC_COLUMNS = ['run_id', 'point_id', 'chunk_id', 'seed_key', 'scenario', 'window', 'd', 'p', 'p_idle', 'K', 'gap',
              'R0', 'Rin', 'Rgap', 'Rout', 'n_pre_u', 'shots', 'n0', 'n_half', 'n_one', 'sum_infidelity',
              'mean_errors', 'mean_so_cz', 'seconds']


def gap_rounds(gap, d):
    return d if gap == 'd' else int(np.ceil(d / 2)) if gap == 'half' else int(gap)


def make_points(plan):
    pts = []
    for scen, p, d, shots in plan:
        for quiet in ([False, True] if QUIET_WINDOW else [False]):
            for K in K_LIST:
                for gap in (GAP_LIST if K > 1 else GAP_LIST[:1]):       # K = 1 には間のラウンドが無い
                    rg = gap_rounds(gap, d)
                    pid = f"{scen}|{'quiet' if quiet else 'noisy'}|d{d}|p{p:g}|K{K}|g{rg if K > 1 else 0}"
                    if any(q['point_id'] == pid for q in pts):
                        continue
                    pts.append(dict(point_id=pid, scenario=scen, p=p, p_idle=SCENARIOS[scen] * p, d=d, K=K,
                                    Rgap=rg, quiet=quiet, shots=shots))
    return pts


def chunk_size(d, K):
    return max(50, int({3: 4000, 5: 1000, 7: 250}.get(d, 100) / K))


_EX = {}


def _experiment(pt):
    if pt['point_id'] not in _EX:
        d = pt['d']
        R0, Rin, Rout = [max(1, int(np.ceil(k * d))) for k in KAPPA]
        _EX.clear()                                     # 1 プロセスが同時に持つ実験は 1 つ（メモリ節約）
        _EX[pt['point_id']] = SeqExperiment(d, R0, Rin, pt['Rgap'], Rout, pt['K'],
                                            NoiseModel(pt['p'], p_idle=pt['p_idle']), n_pre_u=N_PRE_U,
                                            quiet_window=pt['quiet'])
    return _EX[pt['point_id']]


def run_chunk(task):
    pt, chunk_id, n = task
    t0 = time.time()
    ex = _experiment(pt)
    key = (int(BASE_SEED), zlib.crc32(pt['point_id'].encode()), int(chunk_id))
    rng = np.random.default_rng(np.random.SeedSequence(key))
    inf, st = ex.run(n, rng)
    c = ex.circ
    return dict(point_id=pt['point_id'], chunk_id=chunk_id, seed_key='-'.join(map(str, key)), scenario=pt['scenario'],
                window='quiet' if pt['quiet'] else 'noisy', d=pt['d'], p=pt['p'], p_idle=pt['p_idle'], K=pt['K'],
                gap=pt['Rgap'] if pt['K'] > 1 else 0, R0=c.R0, Rin=c.Rin, Rgap=c.Rgap, Rout=c.Rout, n_pre_u=c.n_pre_u,
                shots=n, n0=int((inf == 0).sum()), n_half=int((inf == 0.5).sum()), n_one=int((inf == 1).sum()),
                sum_infidelity=float(inf.sum()), mean_errors=float(np.mean([s['n_err'] for s in st])),
                mean_so_cz=float(np.mean([s['so_cz'] for s in st])), seconds=time.time() - t0)


def run_monte_carlo(plan):
    os.makedirs(OUT_DIR, exist_ok=True)
    run_id = RUN_MODE + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]
    done = {}
    if os.path.exists(MC_CSV):
        if not RESUME:
            raise FileExistsError(f'{MC_CSV} が既にあります。RESUME=True にするか OUT_DIR を変えてください')
        old = pd.read_csv(MC_CSV)
        assert list(old.columns) == MC_COLUMNS, '既存の CSV の列がこのノートと違います'
        done = {(r.point_id, int(r.chunk_id)): int(r.shots) for r in old.itertuples()}
    tasks = []
    for pt in make_points(plan):
        cs = chunk_size(pt['d'], pt['K'])
        for k in range(int(np.ceil(pt['shots'] / cs))):       # ショット数はチャンクの倍数に切り上げる
            if (pt['point_id'], k) in done:                   # （後からショット数を増やしても既存のチャンクと整合する）
                assert done[(pt['point_id'], k)] == cs, f"{pt['point_id']} のチャンクの大きさが既存の CSV と違います"
                continue
            tasks.append((pt, k, cs))
    # 軽い点から順に（途中で止めても軽い点は揃う）。同じ点のチャンクは連続させる（回路の作り直しを減らす）
    order = {pt['point_id']: i for i, pt in enumerate(make_points(plan))}
    tasks.sort(key=lambda t: (order[t[0]['point_id']], t[1]))
    print(f'run_id = {run_id} | 残り {len(tasks)} チャンク / {sum(t[2] for t in tasks)} ショット | 出力 {MC_CSV}')
    if not tasks:
        return
    t0, n_done = time.time(), 0
    total = sum(t[2] for t in tasks)

    def save(row):
        nonlocal n_done
        row = dict(run_id=run_id, **row)
        pd.DataFrame([row])[MC_COLUMNS].to_csv(MC_CSV, mode='a', header=not os.path.exists(MC_CSV), index=False)
        n_done += row['shots']
    last = time.time()
    if WORKERS > 1:
        with _mp.get_context('fork').Pool(WORKERS) as pool:
            for row in pool.imap(run_chunk, tasks, chunksize=1):
                save(row)
                if time.time() - last > 60:
                    last = time.time()
                    print(f'  {n_done}/{total} ショット, {time.time() - t0:.0f} 秒, 現在 {row["point_id"]}', flush=True)
    else:
        for task in tasks:
            save(run_chunk(task))
    print(f'完了：{n_done} ショット, {time.time() - t0:.0f} 秒')
