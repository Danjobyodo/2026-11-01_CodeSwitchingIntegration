# ==================================================================================================
# seq_lib : 研究 4 の拡張ライブラリ（連続サイクルの code switching）
#
# 研究 3 のライブラリ（D4SwitchingCircuit / CompiledProtocol / FluxDecoder / ChargeDecoder / D4Experiment）
# は一切書き換えず、サブクラスとして「K 回連続の switch-in → U → switch-out」を追加する。
#
#   S0 (FSC |+_L> の準備, R0 ラウンド)
#   [ S1 (switch-in, Rin ラウンド + Z だけ n_pre_u ラウンド) → U → SO (switch-out) → S4 (FSC ラウンド) ] × K
#   FIN (評価用の雑音なし FSC 1 ラウンド)
#
# サイクル c = 1..K-1 の後の FSC ラウンド数は Rgap（次のサイクルの前段を兼ねる）、最後のサイクルの後は Rout。
# K = 1, Rgap は無関係 → 研究 3 の回路と同一（乱数の使い方も同一で、同じ seed なら同じ結果になる）。
#
# 理想出力：1 サイクルは FSC の配位 a ごとに位相 omega^{F(a)} を掛ける（研究 3 で検証済み）ので、
# K サイクルの理想出力は D_{K F} |+_L> = (T_L^dagger)^K |+_L>。論理 Clifford 安定化子は Delta -> K * Delta。
# ==================================================================================================


class SeqSwitchingCircuit(D4SwitchingCircuit):
    """K 回連続の code switching の回路（時間ステップの列）。ブロック名の最後の要素がサイクル番号 c。
      ('S0', r) / ('S1', r, 'z', c) / ('S1', r, 'x', c) / ('U', c) / ('SO', c) / ('S4', r, c) / ('FIN',)"""

    def __init__(self, L, R0, Rin, Rgap, Rout, K, n_pre_u=2, fsc_schedule='classes'):
        assert K >= 1 and Rgap >= 1 and Rout >= 1
        self.K, self.Rgap = K, Rgap
        super().__init__(L, R0, Rin, Rout, n_pre_u=n_pre_u, fsc_schedule=fsc_schedule)

    def _logical(self):
        """理想出力 D_{K F}|+_L> の論理 Clifford 安定化子 X^t D_{K Delta}。Delta は F について線形なので
        K 倍するだけ。Pauli proxy の Z 部分（研究 3 では Delta の a_i = 2 の量子ビット）は 1 サイクルごとに
        1 回ずつ掛かるので、K サイクルでは「1 サイクルの集合」を K 回掛けたもの（K が偶数なら消える）。"""
        super()._logical()
        K = self.K
        self.proxy_z = sorted(q for q, a in self.Delta_a.items() if a == 2) if K % 2 else []
        self.Fpoly = {m: (K * v) % 8 for m, v in self.Fpoly.items() if (K * v) % 8}
        self.Delta_c0 = (K * self.Delta_c0) % 8
        self.Delta_a = {q: (K * a) % 4 for q, a in self.Delta_a.items() if (K * a) % 4}
        self.Delta_b = {ij: (K * b) % 2 for ij, b in self.Delta_b.items() if (K * b) % 2}

    def logical_proxy(self, fx, sign=1):
        """X^e H X^e の Pauli proxy：X^t * (proxy の Z 部分) * R_e。R_e = D^dag X^e D X^e（D = D_{K Delta}）は
        研究 3 と同じ式を K 倍した係数で計算する。"""
        n = self.nq
        ps = stim.PauliString(n)
        for q in self.t_log:
            ps[q] = 'X'
        zs = stim.PauliString(n)
        for q in self.proxy_z:
            zs[q] = 'Z'
        R_ = stim.PauliString(n)
        ph = 1
        for q, a in self.Delta_a.items():
            if fx[q] and a % 2 == 1:
                ph *= 1j ** a
                R_ *= _single(n, q, 'Z')
            elif fx[q] and a == 2:
                ph *= -1
        for (i, j), b in self.Delta_b.items():
            if fx[i] and fx[j]:
                ph *= -1
                R_ *= _single(n, i, 'Z') * _single(n, j, 'Z')
            elif fx[i]:
                R_ *= _single(n, j, 'Z')
            elif fx[j]:
                R_ *= _single(n, i, 'Z')
        return ps * zs * R_ * complex(ph * sign)

    def _blocks(self):
        B_ = []
        rb, g, alld = self.data_rb, self.data_g, self.data_all
        for r in range(1, self.R0 + 1):
            pre = [[('RX', q) for q in rb]] if r == 1 else []
            B_.append(dict(name=('S0', r), code='FSC', moms=pre + self.round_moms['FSC'], data=rb))
        for c in range(1, self.K + 1):
            for r in range(1, self.Rin + 1 + self.n_pre_u):
                pre = [[('RZ', q) for q in g]] if r == 1 else []
                B_.append(dict(name=('S1', r, 'z', c), code='D4', moms=pre + self.round_moms['D4z'], data=alld))
                if r <= self.Rin:
                    B_.append(dict(name=('S1', r, 'x', c), code='D4', moms=self.round_moms['D4x'], data=alld))
            B_.append(dict(name=('U', c), code=None, moms=self.U_moms, data=alld))
            B_.append(dict(name=('SO', c), code=None,
                           moms=[[('FLIPX', q) for q in g], list(self.network), [('MZ0', q) for q in g]], data=alld))
            for r in range(1, (self.Rout if c == self.K else self.Rgap) + 1):
                B_.append(dict(name=('S4', r, c), code='FSC', moms=self.round_moms['FSC'], data=rb))
        B_.append(dict(name=('FIN',), code='FSC', moms=self.round_moms['FSC'], data=rb, noiseless=True))
        return B_


class SeqFluxDecoder(FluxDecoder):
    """フラックス復号器（研究 3 と同じ）。違いは 1 点：緑の量子ビットは各サイクルの最初に |0> に初期化
    し直されるので、緑のプラケットの検出事象をサイクルをまたいでつながない。"""

    def _cyc(self, k):
        nm = self.fr[k]['name']
        return nm[-1] if nm[0] in ('S1', 'SO') else None

    @staticmethod
    def _is_g(lab):
        return lab[0] == 'plaq' and lab[2] == 'g'

    def _prev(self, k, lab):
        r = super()._prev(k, lab)
        if r is not None and self._is_g(lab) and self._cyc(r[0]) != self._cyc(k):
            return None
        return r

    def _next(self, k, lab):
        kn = super()._next(k, lab)
        if kn is not None and self._is_g(lab) and self._cyc(kn) != self._cyc(k):
            return None
        return kn

    def new_cycle(self):
        """次のサイクルの switch-in の直前：緑のプラケットの参照値を 0（|0> に初期化した直後の値）に戻す。"""
        for lab in list(self.last):
            if self._is_g(lab):
                del self.last[lab]


class SeqChargeDecoder(ChargeDecoder):
    """電荷復号器（研究 3 と同じ構成）。検出器の定義を K サイクルに一般化しただけ：
      * FSC ラウンド：同じ検査の 1 つ前のラウンドとの差
      * 各サイクルの最初の D4 ラウンド：直前の FSC ラウンド（サイクル 1 は S0、以降は前のサイクルの S4）との差
      * 各サイクルの最初の FSC ラウンド：そのサイクルの最後の D4 ラウンドとの差（研究 3 の aligned / 非 aligned の基底）
    論理観測量には各サイクルの S^g の固有値（Pauli フレーム）を含める。"""

    def __init__(self, comp, dem_noise=None, aligned=True):
        circ = comp.circ
        self.comp, self.circ = comp, circ
        nz = dem_noise or comp.noise
        meas_lab, blk_meas = [], []
        for bi, blk in enumerate(comp.blocks):
            ids = []
            for cm in blk['moms']:
                for q, b in cm.meas:
                    if blk['code']:
                        meas_lab.append((blk['name'], b, circ.lab_of[(blk['code'], q)]))
                    else:
                        meas_lab.append((blk['name'], 'R', q))
                    ids.append(len(meas_lab) - 1)
            blk_meas.append(ids)
        self.n_meas, self.blk_meas = len(meas_lab), blk_meas
        idx = {(bn, lab): i for i, (bn, b, lab) in enumerate(meas_lab)}
        self.meas_idx = idx
        sup = {code: {lab: set(xs) for lab, xs, quad in circ.xgens[code]} for code in ('D4', 'FSC')}
        names = [blk['name'] for blk in comp.blocks]
        fscl = [lab for lab, _, _ in circ.xgens['FSC']]
        d4l = [lab for lab, _, _ in circ.xgens['D4']]
        lat, c = circ.lat, circ.c
        inv = {v: k for k, v in c.items()}

        def span_solve(target, basis_labels, code):
            M = np.zeros((len(basis_labels), circ.nq), dtype=np.uint8)
            for i, l in enumerate(basis_labels):
                M[i, list(sup[code][l])] = 1
            v = np.zeros(circ.nq, dtype=np.uint8)
            v[list(target)] = 1
            sol = f2_solve(M, v)
            return None if sol is None else [basis_labels[i] for i in np.nonzero(sol)[0]]

        dets = []
        S0 = [n for n in names if n[0] == 'S0']
        for j, n in enumerate(S0):
            for lab in fscl:
                dets.append([idx[(n, lab)]] + ([idx[(S0[j - 1], lab)]] if j else []))
        prev_fsc = S0[-1] if S0 else None
        self.last_S1x = {}
        for cyc in range(1, circ.K + 1):
            S1 = [n for n in names if n[0] == 'S1' and n[2] == 'x' and n[3] == cyc]
            S4 = [n for n in names if n[0] == 'S4' and n[2] == cyc] + ([('FIN',)] if cyc == circ.K else [])
            self.last_S1x[cyc] = S1[-1]
            for j, n in enumerate(S1):
                for lab in d4l:
                    if j == 0:
                        if prev_fsc is None:
                            continue
                        combo = span_solve(sup['D4'][lab], fscl, 'FSC')
                        if combo is None:
                            continue                   # S^g：最初の結果はランダム（ゲージング）
                        dets.append([idx[(n, lab)]] + [idx[(prev_fsc, l)] for l in combo])
                    else:
                        dets.append([idx[(n, lab)], idx[(S1[j - 1], lab)]])
            for j, n in enumerate(S4):
                first = {}
                for lab in fscl:
                    if j == 0:
                        tgt = set(sup['FSC'][lab])
                        for q in list(sup['FSC'][lab]):
                            gq = lat.q(inv[q] // 3, G)
                            if gq in c:
                                tgt ^= {c[gq]}
                        combo = span_solve(tgt, d4l, 'D4')
                        assert combo is not None, 'S4 X check not determined by the last D4 round'
                        first[lab] = [idx[(n, lab)]] + [idx[(S1[-1], l)] for l in combo]
                    else:
                        dets.append([idx[(n, lab)], idx[(S4[j - 1], lab)]])
                if j == 0:
                    for lab, d in first.items():
                        v, col = lab[1], lab[2]
                        if aligned and col == 'b' and ('X', v, 'r') in first:
                            dets.append(sorted(set(d) ^ set(first[('X', v, 'r')])))
                        else:
                            dets.append(d)
            prev_fsc = S4[-1]
        self.dets = dets
        tset = set(circ.t_log)
        self.cross = [len(set(fs) & tset) % 2 for fs in circ.frame_strings]
        self.obs_meas = [idx[(self.last_S1x[cyc], lab)] for cyc in range(1, circ.K + 1)
                         for (lab, op), cr in zip(circ.gens_g, self.cross) if cr]
        saved = circ.Delta_a                 # 親クラスの _dem_circuit は「Delta_a == 2 の量子ビット」を proxy の
        circ.Delta_a = {q: 2 for q in circ.proxy_z}      # Z 部分として読むので、その集合だけを一時的に渡す
        try:
            self._dem_circuit(nz)
        finally:
            circ.Delta_a = saved
        self.det_ptr = np.cumsum([0] + [len(d) for d in dets])
        self.det_idx = np.concatenate([np.array(d, dtype=np.int64) for d in dets])

    def flux_erasures(self, flux_events, w_erase=0.1):
        """研究 3 の flux_erasures と同じ規則。flux_events の要素は (量子ビット, ラウンド r, サイクル c)。"""
        circ = self.circ
        if not hasattr(self, '_cz_of'):
            self._cz_of, self._stars = {}, {}
            for lab, xs, quad in circ.xgens['D4']:
                for (i, j) in quad:
                    self._cz_of.setdefault(i, []).append((lab, j))
                    self._cz_of.setdefault(j, []).append((lab, i))
                for q in xs:
                    self._stars.setdefault(q, []).append(lab)
        er = set()
        for q, r, cyc in flux_events:
            blk, nxt = ('S1', r, 'x', cyc), ('S1', r + 1, 'x', cyc)
            for lab, partner in self._cz_of.get(q, []):
                m = self.meas_idx.get((blk, lab))
                if m is None:
                    continue
                dd = tuple(sorted(self.dets_of_meas.get(m, [])))
                if 1 <= len(dd) <= 2 and dd in self.comp_index:
                    er.add(self.comp_index[dd])
                st = self._stars.get(partner, [])
                for rr in (blk, nxt):
                    ds = []
                    for l2 in st:
                        m2 = self.meas_idx.get((rr, l2))
                        if m2 is not None:
                            ds += [j for j in self.dets_of_meas.get(m2, []) if self.dets[j][0] == m2]
                    dd = tuple(sorted(ds))
                    if 1 <= len(dd) <= 2 and dd in self.comp_index:
                        er.add(self.comp_index[dd])
        return er


class SeqExperiment(D4Experiment):
    """K 回連続の code switching ＋復号器。shot() は出力 (T_L^dagger)^K|+_L> に対する不忠実度（0, 1/2, 1）を返す。
    1 サイクルの中の処理（実時間のフラックス復号、U の直前の確定、switch-out、Pauli フレーム）は研究 3 の
    D4Experiment.shot と同じ。違いは、(1) X フレームの初期化はサイクル 1 の直前だけ（以降は追跡を続ける）、
    (2) 次のサイクルの直前に緑の参照値を戻す、(3) Pauli フレームと電荷復号を全サイクルまとめて最後に行う。"""

    def __init__(self, L, R0, Rin, Rgap, Rout, K, noise, delay=0, pre_u_age=0, n_pre_u=2, flux_informed=True,
                 quiet_window=False, fsc_schedule='classes'):
        self.pre_u_age, self.flux_informed = pre_u_age, flux_informed
        self.circ = SeqSwitchingCircuit(L, R0, Rin, Rgap, Rout, K, n_pre_u=n_pre_u, fsc_schedule=fsc_schedule)
        self.comp = CompiledProtocol(self.circ, noise)
        self.noise, self.K = noise, K
        self.flux = SeqFluxDecoder(self.comp, delay=delay)
        self.charges = [SeqChargeDecoder(self.comp, aligned=a) for a in (True, False)]
        self.quiet_window = quiet_window
        win = set()
        for c in range(1, K + 1):                   # 切り替えの窓（研究 3 と同じ定義を各サイクルに）
            win |= {('S1', Rin, 'z', c), ('S1', Rin, 'x', c), ('U', c), ('SO', c), ('S4', 1, c)}
            win |= {('S1', r, 'z', c) for r in range(Rin + 1, Rin + 1 + n_pre_u)}
        self.window = win
        if quiet_window:
            for blk in self.comp.blocks:
                if blk['name'] in win:
                    a, b = blk['moms'][0].loc_slice[0], blk['moms'][-1].loc_slice[1]
                    self.comp.loc_p[a:b] = 0.0
        self.gset = set(self.circ.data_g)
        names = [b['name'] for b in self.comp.blocks]
        self._last_S0 = max([i for i, n in enumerate(names) if n[0] == 'S0'], default=-1)
        self._last_S1 = {max(i for i, n in enumerate(names) if n[0] == 'S1' and n[3] == c) for c in range(1, K + 1)}
        self._last_S1x = {max(i for i, n in enumerate(names) if n[0] == 'S1' and n[2] == 'x' and n[3] == c): c
                          for c in range(1, K + 1)}

    def shot(self, rng, decode=True, forced=None, ts=None, init=None):
        circ, comp, fl = self.circ, self.comp, self.flux
        fstatic = {k: v for k, v in forced.items() if not isinstance(k, tuple)} if forced is not None else None
        fdyn = {k: v for k, v in forced.items() if isinstance(k, tuple)} if forced is not None else None
        sh = FastShot(comp, rng, fstatic)
        if init is not None:
            init(sh)
        lock, outs, flux_events, m_g = [], [], [], {}
        fl.start()
        kfr = 0
        stats = dict(n_err=sh.n_err, n_corr=0, so_cz=0)
        for bi, blk in enumerate(comp.blocks):
            nm = blk['name']
            if nm[0] == 'S1' and nm[1] == 1 and nm[2] == 'z':
                if nm[3] == 1:
                    sh.init_frame(circ.zchecks['FSC'], circ.data_rb)
                else:
                    fl.new_cycle()
            if init is not None and nm[0] == 'S0':
                res = [(q, bb, 0) for cm in comp.blocks[bi]['moms'] for (q, bb) in cm.meas]
            elif ts is None:
                res = sh.run_block(bi)
            else:
                r5 = sh.run_block_lockstep(bi, ts, rng)
                lock += r5
                res = [(q, bb, o) for q, bb, o, pk, pr in r5]
            outs += [o for (_, _, o) in res]
            if bi in self._last_S1x:
                gl = {circ.lab_of[('D4', q)]: o for (q, b, o) in res if b == 'X'}
                m_g[self._last_S1x[bi]] = [gl[lab] for lab, _ in circ.gens_g]
            if nm[0] in ('S0', 'S4', 'FIN') or (nm[0] == 'S1' and nm[2] == 'z'):
                code = blk['code']
                zl = {circ.lab_of[(code, q)]: o for (q, b, o) in res if b == 'Z'}
                fl.push_round(kfr, zl)
                kfr += 1
                if decode:
                    flush = bi == self._last_S0 or bi in self._last_S1 or nm[0] == 'FIN'
                    cc = fl.decode(flush=flush, min_age=self.pre_u_age if bi in self._last_S1 else 0)
                    corr = [q for q, k in cc]
                    if nm[0] == 'S1':
                        flux_events += [(q, nm[1] - 1, nm[3]) for q in corr if nm[1] >= 2]
                    sh.apply_x(corr)
                    if ts is not None:
                        for q in corr:
                            ts.X(q)
                    for q in corr:
                        fl.register_correction(q, code)
                    stats['n_corr'] += len(corr)
            elif nm[0] == 'SO':
                readout = {q: o for (q, b, o) in res}
                fl.push_round(kfr, readout=readout)
                kfr += 1
                a_dec = dict(readout)
                phys = []
                if decode:
                    for q, k in fl.decode(flush=True):
                        if q in self.gset:
                            a_dec[q] ^= 1
                        else:
                            phys.append(q)
                    for q in phys:
                        fl.register_correction(q, 'FSC')
                    stats['n_corr'] += len(phys)
                stats['so_cz'] += self._switch_out(sh, readout, a_dec, phys, rng, fdyn,
                                                   noisy=forced is None and not self.quiet_window, ts=ts)
        for cyc in sorted(m_g):                      # 各サイクルの S^g の固有値の Pauli フレーム
            for v, m in enumerate(m_g[cyc]):
                if m:
                    for q in circ.frame_strings[v]:
                        sh.sim.z(q)
                        if ts is not None:
                            ts.Z(q)
        val = sh.sim.peek_observable_expectation(circ.logical_proxy(sh.fx))
        if ts is not None:
            stats['lockstep'] = lock
            stats['H_true'] = ts.expect_logical(circ)
            stats['H_proxy'] = val
        if decode:
            sols = [ch.predict(outs, ch.flux_erasures(flux_events) if self.flux_informed else None)
                    for ch in self.charges]
            flip = min(sols, key=lambda s: s[1])[0]
        else:
            flip = 0
        val = val * (-1) ** flip
        stats['n_dress'] = sh.n_dress
        return (1 - val) / 2, stats


def seq_counts(d, K=1, Rgap=None, R0=None, Rin=None, Rout=None, n_pre_u=2):
    """回路から数えた量子ビット数・時間ステップ数・時空間体積（研究 3 の kobayashi_counts と同じ数え方：
    FSC のブロックでは赤青のデータと FSC の補助、D4 のブロックでは全データと D4 の補助、U と switch-out では
    全データを「使用中」とする）を段階別に返す。"""
    R0 = d if R0 is None else R0
    Rin = d if Rin is None else Rin
    Rout = d if Rout is None else Rout
    Rgap = d if Rgap is None else Rgap
    circ = SeqSwitchingCircuit(d, R0, Rin, Rgap, Rout, K, n_pre_u=n_pre_u)
    out = dict(d=d, K=K, Rgap=Rgap, qubits=circ.nq, steps={}, volume={})
    for blk in circ.blocks:
        nm = blk['name']
        if nm[0] == 'FIN':
            continue
        if blk['code'] == 'FSC':
            active = len(set(circ.data_rb) | set(circ.anc['FSC']))
        elif blk['code'] == 'D4':
            active = len(set(circ.data_all) | set(circ.anc['D4']))
        else:
            active = len(circ.data_all)
        st = block_steps(circ, blk)
        key = 'S0' if nm[0] == 'S0' else ('gap' if (nm[0] == 'S4' and nm[2] < K) else nm[0])
        out['steps'][key] = out['steps'].get(key, 0) + st
        out['volume'][key] = out['volume'].get(key, 0) + st * active
    out['time_steps'] = sum(out['steps'].values())
    out['volume_total'] = sum(out['volume'].values())
    return out
