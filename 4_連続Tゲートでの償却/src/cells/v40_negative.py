# V4：負の対照。実装をわざと 1 箇所だけ間違えると V3 の照合が不一致を検出することを確かめる
#     （検出できない検査は検査になっていない）。
class _WrongLogical(SeqExperiment):          # 論理安定化子を K 倍しない（1 サイクル用のまま）
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        c1 = D4SwitchingCircuit(self.circ.L, self.circ.R0, self.circ.Rin, self.circ.Rout)
        self.circ.Delta_c0, self.circ.Delta_a, self.circ.Delta_b = c1.Delta_c0, c1.Delta_a, c1.Delta_b


def _count_mismatch(make, ntr, seed):
    rng = np.random.default_rng(seed)
    ex = make()
    return sum(not lockstep_full(2, 1, 1, NoiseModel(0.03), rng, ex=ex)['agree'] for _ in range(ntr))


n1 = _count_mismatch(lambda: _WrongLogical(2, 1, 1, 1, 1, 2, NoiseModel(0.03)), V4_TRIALS, SEED + 1)
record('V4a 負の対照：論理安定化子を K 倍しないと不一致が出る', n1 > 0, f'{n1} / {V4_TRIALS} 軌道で不一致')
_saved = dressing
try:
    dressing = lambda name, e: []            # ドレッシングを空にする
    n2 = _count_mismatch(lambda: SeqExperiment(2, 1, 1, 1, 1, 2, NoiseModel(0.03)), V4_TRIALS, SEED + 2)
finally:
    dressing = _saved
record('V4b 負の対照：ドレッシングを外すと不一致が出る', n2 > 0, f'{n2} / {V4_TRIALS} 軌道で不一致')
