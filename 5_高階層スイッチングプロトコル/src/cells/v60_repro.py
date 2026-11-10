# ==================================================================================================
# V6 再現性：同じ seed なら同じ測定結果と同じ出力になる
# ==================================================================================================
def one(seed):
    sim = StateSim(Lattice(4, (2, 1, 1)))
    rng = np.random.default_rng(seed)
    return [(r['n_charges'], r['n_flux_out'], round(r['fidelity'], 12)) for r in (sim.run_protocol(rng) for _ in range(5))]
a, b, c = one(SEED), one(SEED), one(SEED + 1)
record('V6 再現性', a == b and [x[:2] for x in a] != [x[:2] for x in c], f'seed={SEED}: {a[:3]} ...')
