# 研究 2（code switching の論理誤り率）v9：方法・厳密性・復号器

作成日：2026-11-02（Claude）。対象コード：`chsc_switch_v9.py`（= `CHSC_switch_v9_main.ipynb`）、`chsc_validation_v9.py`（= `CHSC_switch_v9_validation.ipynb`）。

この文書は、v3 までは作業フォルダにない v2 の README（§3・§4）に委ねていた方法の説明（R2-2）を、v9 のコードとコメントから再構成して独立に読めるようにしたものである。v9 での変更（§4.3）、JIT 復号器の研究 1 との違い（§4.1、R2-5）、$d$ の意味（§1、R2-4）もここにまとめる。使い方と結果の表は `README_v9.md`。

---

## 1. 問題設定

可換な表面符号（folded surface code, FSC）の論理 $|+\rangle$ から出発し、物理誤り率 $p$ の現象論的雑音の下で $\mathbb D_4$ 符号に切り替え（switch-in）、理想的な論理 $T^\dagger$（transversal な $U=WV$）を作用させ、FSC に戻す（switch-out）。最後に「目標の状態 $T^\dagger|+\rangle$ そのものが得られなかった割合」$P_L=1-P(I)$ を、$d$ と $p$ の関数として求め、隣り合う $d$ の曲線の有限サイズ交点を記述的に求める。

* **幾何**（`TriangleCode`）：[KZH] Fig. 4 の正方格子パッチ（$(d+1)\times(d+1)$ 頂点、正方形を対角線で 2 つの三角形に分割）。境界 $\mathcal L_r$（$a_r=0$）、$\mathcal L_b$（$a_b=0$）、$\mathcal L_{rb}$（$a_r+a_b=0$, $a_g=0$）。単一量子ビットの $Z$ 安定化子で固定される量子ビット（上辺の $b$、左辺の $r$、$\mathcal L_{rb}$ の辺の $g$）は理想的な $|0\rangle$ として除く。$\mathcal L_{rb}$ の頂点の $X$ 型生成元は赤と青を組にした `rb` 生成元（CZ dressing を含む）。論理 $Z$ は [KZH] SM Fig. 6 の接合点を持つ形。
* **$d$ の意味（R2-4）**：$d$ は**パッチの 1 辺の正方形の数**である。$\mathbb D_4$ 相を含む switch-in から switch-out までのプロトコル全体の実効的な距離が $d$ であることは、このフォルダの中では確認していない（研究 3 は $\mathbb D_4$ 相の Knill–Laflamme 距離を $L\le5$ で確認しているが、幾何の定義が別）。論文では「$d$ = パッチの大きさ」と定義し、距離の主張は避ける。
* **雑音（現象論的）**：switch-in の各ラウンドの冒頭に全量子ビットへ $\mathcal D_1(p)$、全ての検査結果に反転 $p$。$U$ の後（switch-out の前）に全量子ビットへ $\mathcal D_1(p)$ を 1 回、緑の単発 $Z$ 読み出しに反転 $p$。表面符号の各ラウンドに赤・青へ $\mathcal D_1(p)$ と反転 $p$。$U$、緑の補正 $S^g_X(\lambda)$、初期化、最後の理想ラウンドは雑音なし。
* **ケース**：`in_only`（switch-in のみ、$\mathbb D_4$ 符号として理想的に読み出す。目標 $|+\rangle_{\mathbb D_4}$）、`in_out`（$U$ なし、目標 $|+\rangle$）、`in_T_out`（目標 $T^\dagger|+\rangle$）。

## 2. 1 ショットの手順と `switch_in_boundary`

1. 初期状態：FSC（赤・青）の論理 $|+\rangle$、緑は $|0\rangle$（Pauli 安定化子状態）。
2. **switch-in**（$R_{\rm in}=d$ ラウンド）：データ雑音 → 全ての $Z$ 検査（反転 $p$）→ 赤青と緑の JIT フラックス復号と $X$ 補正 → dressed $X$ 生成元を色層の順（既定 r→g→b）に測定（反転 $p$）。
3. **switch-in の終わり**：
   * `ideal`：$U$ の直前に雑音なしの $Z$ 検査と dressed $X$ 検査を 1 ラウンド置き、その完全なシンドロームでフラックスを閉じ電荷を後始末する。$U$ は（論理誤りを除けば）完全な $\mathbb D_4$ 符号状態に作用する。「switch-in の失敗」と「switch-out 以降の失敗」を $U$ の位置で理想的に切り離した基準（楽観側）であり、残った誤りが $U$ を通る効果は構造的に 0 になる。
   * `noisy`：完全ラウンドを置かない。JIT が保留したフラックス（$X$ 誤り）は補正されないまま $U$ に入り、$W$（CS, $T^\dagger$）を通って S・CZ 型の Clifford 誤りになりうる。緑の電荷は $V$ を通って $e_g\to e_{rgb}$ と広がる。v9 の復号は §4.3。
4. 電荷の後始末：緑は最終シンドロームを推定して空間的に組にし、$Z$ 補正を $U$ の前に当てる。赤・青は `ideal` と v3 の `noisy` では $U$ の前に時空 MWPM で $Z$ 補正を当てる。v9 の `noisy`（`noisy_decoder="joint"`）では赤・青は $U$ の後にまとめて復号する（§4.3）。
5. `in_only` はここで $\mathbb D_4$ 符号の理想読み出し（完全な $Z$ 検査、フラックスの閉鎖、$X$ フレームの生成元による除去、完全な dressed ラウンド、電荷の組、仮想的な論理測定）で評価する。`in_T_out` は $U$ を作用させる。
6. **switch-out**：全量子ビットに $\mathcal D_1(p)$、緑の単発 $Z$ 読み出し、緑のフラックスの復号（v9 の `noisy` では switch-in の保留事象と通しで、§4.3）、補正後の結果 $m'$ から $\lambda$（$\sum_v\lambda_v\,{\rm supp}_v=m'$）を解き、緑の補正 $S^g_X(\lambda)$ を作用させる。
7. 表面符号（赤・青）の $R_{\rm out}=d$ ラウンドの雑音のある測定と 1 回の完全ラウンド、時空 MWPM による $X$・$Z$ 補正。
8. 論理評価：出力を $\{I,X,Y,Z,S,\text{collapsed}\}$（`in_only` ではさらに flux_D4）に分類し、$P_L=1-P(I)$。$P_L$ は入力を $|+\rangle$ に固定した魔法状態準備の失敗率で、任意入力に対する論理ゲートの誤り率とは別の量（平均の不忠実度は `mean_infidelity_excl_fluxD4` 列）。

## 3. シミュレーション方式：Takada–Bartlett–Williamson の Clifford-stabilizer simulation（Pauli proxy）

研究 2 は [Tak] の方法を operator レベル（Algorithm 1）で実装し、Pauli proxy の Clifford 回路を `stim.TableauSimulator` で実行する。研究 3 は同じ方法の回路レベル版（Algorithm 2）である。研究 1 は同じ代数構造を $\mathbb D_4$ 符号に特化した独自の厳密表現（twisted frame）で実装している。

### 3.1 measurement-conjugated picture と誤りフレーム（[Tak] Sec. VII A）

物理状態を $E|\text{frame}\rangle$ と書き、誤りと補正の累積 $E$ を
$$
E=X^{x}\,\mathrm{diag}\!\left(\omega^{\gamma(a)}\right),\qquad
\gamma(a)=\sum_i l_ia_i+4\sum_{i<j}Q_{ij}a_ia_j\pmod 8,\qquad \omega=e^{i\pi/4}
$$
（Pauli $X$ フレームと対角 Clifford の積。$Z$: $l=4$、$S$: $l=2$、$S^\dagger$: $l=6$、CZ: $Q=1$）で古典的に保持する（`ErrorFrame`）。$U$ の前の $E$ は Pauli であり、$X$ 誤りが transversal な $W$ を通るとき、および緑の補正 $S^g_X$ の CZ 部分を通すときに対角 Clifford 成分が現れる。$M$ を $E|\text{frame}\rangle$ で測ることは $E^\dagger ME$ を $|\text{frame}\rangle$ で測ることと同じである（その後 $E$ を戻す）。

### 3.2 Pauli dressing と Pauli proxy（[Tak] Sec. VII B, C）

dressed 生成元 $M=X^s\Delta$（$\Delta$ は CZ dressing）について
$$
E^\dagger ME = X^s\Delta\,\mathrm{diag}\!\left(\omega^{[\delta(a+x)-\delta(a)]+[\gamma(a)-\gamma(a+s)]}\right)
$$
の第 2 因子は Pauli dressing（位相付きの $Z$ 列）である。$\Delta$ をその Pauli proxy（恒等。dressed 生成元の proxy は bare な $X$ 星）で置き換えると Pauli 演算子が得られ、これを Stim の MPP で測る（`ProxyBackend.measure_gens`）。本番経路（`lockstep=False`）は MPP を区間ごとにまとめて実行し、符号ビットを後で反映する。frame の状態は proxy の描像では Pauli 安定化子状態である。

### 3.3 厳密性の十分条件 C1–C3

$C=\mathrm{diag}((-1)^{\phi_0})$（$\phi_0$ は $\mathbb D_4$ 符号状態の位相）とする。

* **(C1)** 全ての dressed 生成元 $G=X^{s_G}\mathrm{CZ}^{\rm pairs}$ と全ての平坦配位 $a$ について $\phi_0(a+s_G)=\phi_0(a)+q_G(a)\pmod2$。すなわち平坦部分空間上で $CX^{s_G}C^\dagger=G$ であり、$G$ の proxy は $X^{s_G}$。$\mathbb D_4$ 符号状態の位相 $\phi_0$ が満たす生成元ごとの恒等式（dressed 生成元が符号状態を安定化することと同値）である。
* **(C2)** $a_g=0$ の全ての平坦配位 $b$ で $\phi_0(b)=0$。すなわち $C$ は FSC の状態（緑が $|0\rangle$）に自明に作用する。初期状態（Pauli 安定化子状態）がそのまま frame になる根拠。
* **(C3)** 平坦部分空間上で $UC=CVT_h$（$T_h=\mathrm{diag}(\omega^{\kappa h})$、$h$ は論理 $\bar Z$ のパリティ、$\kappa=7$ で $T^\dagger$）。すなわち $U$ の proxy は $V$（CNOT 網）で、論理 $T^\dagger$ は $T_h$ として帳簿に残す。[KZH] Theorem 2 の点ごとの形。

この 3 条件の下で、[Tak] の更新則（Theorem、Definition 1, 2）により、誤り・補正・Pauli／Clifford 安定化子の測定の任意の列に対して proxy の Pauli 安定化子群の更新が真の Clifford-stabilizer group の更新と同じ測定統計を与える。

**コードでの確認（実装検査）**：`check_intertwiner_conditions` が各 $d$ でランダムな平坦配位について C1–C3 を検査し、`run_self_checks` が `d_values` の全ての $d$ で違反 0 を確認する（$d=3,5,7$ で違反 0）。これはランダムな配位での**実装検査であって、全配位での恒等式の証明ではない**。証明にあたるのは、C1 が $\phi_0$ の定義（dressed 生成元の固有値 $+1$）から、C3 が [KZH] Theorem 2 から従うという代数的な議論である。

### 3.4 $U$、switch-out、論理評価

* $U$（`apply_U`）：frame 側では CNOT 網 $V$ を Stim で実行し、$E$ を $UEU^\dagger$ に共役する（`conj_U`）。
* switch-out の緑の $Z$ 測定（`measure_green_switch_out`）：frame を $Z^g=+1$ に射影し、真の分岐反転演算子 $S^g_X(\lambda)$ を $E$ に右から掛ける（[Tak] Algorithm 3）。
* 論理評価（`evaluate_class`）：目標状態の Clifford 安定化子の Pauli proxy（誤りフレームで共役し、$T^\dagger$ の場合は $T_h$ の効果を含める）の期待値を Stim で読み、出力状態を類に分類する（[Tak] Sec. VI D の仮想的な Clifford 安定化子測定）。

## 4. 復号器

### 4.1 JIT フラックス復号器（研究 1 との違い：R2-5）

ラウンド $t$ で、補正済みシンドローム（測定値 XOR これまでの補正のフラックス）の変化を検出事象とし、層 $0..t$ の時空グラフ（未来境界の重み $\texttt{offset}\cdot w_t$）を MWPM で復号する。$w_s=\ln[(1-p_X)/p_X]$（$p_X=2p/3$）、$w_t=\ln[(1-p)/p]$。研究 1 の `JITFluxDecoder` と同じ考え方を、空間境界のある平面グラフに一般化したものである。**研究 1 との違い**：(i) 空間境界とのマッチングもその場で補正する、(ii) 未来境界と組になった事象への経路の空間部分も補正し、保留する事象の位置を経路の終点に移す、(iii) 保留コストの計算に使う時刻は同じ検査で保留されていた事象の最も遅い時刻を引き継ぐ。通常は未来境界への経路は同じ検査の時間辺だけなのでほぼ同じ動作になるが、論文では両研究の JIT を同一のものとして書かない。

JIT の不変量（v9 の通し復号で使う）：$(\text{適用した補正のフラックス})\oplus(\text{最後の補正済みシンドローム})=(\text{保留事象の空間的な和})$。したがって、その後の層の最初の検出事象は「測定したフラックス $\oplus$ 保留事象の和」になる。

### 4.2 電荷の復号

* 赤・青：dressed $X$ 検査の記録の時空 MWPM（v3 の `noisy` は最終層に未来境界）。`ideal` では最後の完全ラウンドを含む。
* 緑：最初のラウンドの結果はランダム（ゲージの選択）なので参照にし、最終シンドロームを推定して空間的に組にする。
* switch-out 後の表面符号：$R_{\rm out}$ ラウンドと 1 回の完全ラウンドで時空 MWPM（v3 では switch-in の記録とは別の窓）。

### 4.3 v9：`noisy` で $U$ をまたいで復号を続ける（研究 3 と同じ原理）

研究 3 の復号器は、プロトコルの全ラウンドを 1 つの時空グラフで扱う（フラックスは S0 から最後まで、switch-out の $Z^g$ 読み出しは S1 の緑フラックスと結合、電荷はプロトコル終了後に回路全体の誤りモデルで復号）。v3 の研究 2 は $U$ の位置で復号窓を切っていた（Gemini の指摘 2.2）。v9 の `noisy_decoder="joint"`（既定）では次のように改めた。

1. **赤・青のフラックス**：$U$ の時点で JIT に保留されている事象と、表面符号の $Z$ ラウンド（$R_{\rm out}+1$ 層）を 1 つのグラフで復号する（`jflux_rb`）。$Z^r$, $Z^b$ のプラケットは $V=\prod\mathrm{CNOT}(r\to g)\mathrm{CNOT}(b\to g)$ と可換なので同じ検査が $U$ をまたいで続く。
2. **緑のフラックス**：保留事象と switch-out の $Z^g$ 読み出しの面パリティの層を 1 つのグラフで復号し（`jflux_g`）、補正した $m'$ から $\lambda$ を求める。
3. **赤・青の電荷**：switch-in の dressed 層（$R_{\rm in}$ 層）と表面符号の bare 層（$R_{\rm out}+1$ 層）を 1 つのグラフで復号し（`jchg_rb`）、$U$ の前の硬判定の $Z$ 補正をやめる。$Z^r$, $Z^b$ は $U=WV$（CNOT の制御側、対角な $W$）とも $S^g_X(\lambda)$ とも厳密に可換なので、補正を $U$ の後に回しても物理は同じである。緑の電荷は v3 と同じく $U$ の前に後始末する（残りは $V$ で赤青の電荷になり、3. のグラフで見える）。

`ideal` は変更していない（同じ seed で v3 と全ショット同じ標本・同じ判定になることを確認）。`noisy_decoder="split_v3"`, `n_pre_u=0` で v3 の `noisy` も全ショット同じに再現できる。

**$U$ 直前の $Z$ だけのラウンド（`n_pre_u`）を既定にしなかった理由**：研究 3 は $U$ の直前に $Z$ 検査だけのラウンドを 2 回置き、窓の単一故障の寄与を大きく減らした（回路レベル）。研究 2 にも同じ選択肢を入れて同じ誤りの条件で比べたところ、現象論的雑音では逆に大きく悪化した（下表、`in_T_out`、各 6000 ショット、Agresti–Coull 95% 区間）。現象論的雑音では各ラウンドの冒頭に全量子ビットへ $\mathcal D_1(p)$ が入るので、$Z$ だけのラウンドは「$X$ 検査の情報なしにデータ雑音を増やす」ことになり、特に緑の $Z$ 誤りは $U$ の前に見つける手段がない（研究 3 でも、アイドル雑音のあるシナリオ A の $d=5$ では、残る単一故障の失敗 26 件中 20 件が $U$ 直前の 2 回目の $Z$ ラウンド（アイドル雑音を含む）の故障だった）。研究 3 で効いたのは、回路レベルの CCZ ガジェットの故障と $Z$ 検査の測定誤りに対する保護であり、研究 2 の雑音モデルにはその故障がない。したがって `n_pre_u` は選択肢として残し、既定は 0 とした。

| $d$ | $p$ | v3（split, $n_{\rm pre}=0$） | v9 既定（joint, $n_{\rm pre}=0$） | split, $n_{\rm pre}=2$ | joint, $n_{\rm pre}=2$ |
|---|---|---|---|---|---|
| 3 | 1% | 0.0387 [0.034, 0.044] | **0.0327** [0.028, 0.037] | 0.0883 | 0.0863 |
| 3 | 2% | 0.1662 [0.157, 0.176] | **0.1512** [0.142, 0.160] | 0.2703 | 0.2565 |
| 5 | 1% | 0.0168 [0.014, 0.020] | **0.0138** [0.011, 0.017] | 0.0472 | 0.0432 |

（試行計算。v9 の本番で取り直す。）通しの復号は v3 より $P_L$ を 1–2 割下げ、悪化させる条件は見つからなかった。

## 5. 正当化（`chsc_validation_v9.py`）

本番と同じ `ShotRunner`（同じ操作の列と復号器）を、本番のエンジン（`ProxyBackend`）と参照エンジンに同じ入力（雑音、復号器、ランダムな結果のビット）で同時に与え（ロックステップ）、全ての測定（決定的かランダムか、とその結果）、全ての $Z$ 検査、$\mathbb D_4$ 読み出しの $X$ フレーム、最終的な論理状態の類を比べる。復号器は古典的な処理で参照と共通なので、v9 の通し復号もそのまま検査される。

* 参照 1：総当たりの密な状態ベクトル（$d=2$、全演算子を文字どおり作用）。
* 参照 2：v1 の厳密エンジン（$\mathbb Z_4$ twisted-frame、研究 1 と同系統の独立実装、$d=3,4$）。
* 参照 3：本番経路（`lockstep=False`：MPP の一括実行、符号ビット、Stim 自身の乱数、`measure_many`）の出力を総当たりに再生（$d=2$）。
* (C) $U=WV$ が論理 $T^\dagger$ であることの総当たり確認。
* v9：境界処理 `ideal`、`noisy`（本番の通し復号）、`noisy_preu2`（任意の `n_pre_u=2` の経路）の 3 通りを検査する。

結果は `README_v9.md` §3。

## 6. 前提と限界

* 雑音は現象論的（データの $\mathcal D_1(p)$ と測定結果の反転）だけで、回路レベル雑音（dressed 検査の測定回路）は扱っていない（研究 3 の回路と雑音で研究 2 を行うことは今後の課題）。
* $U$、緑の補正 $S^g_X(\lambda)$、初期化、最終の読み出しは理想、switch-out の $Z^g$ 測定は単発。
* 復号器は最適化していない。緑の電荷の $U$ をまたぐ扱い（$V$ で赤青の電荷に写るためハイパーエッジになる）は、$U$ の前の後始末のまま。
* $P_L$ は入力 $|+\rangle$ の魔法状態準備の失敗率。交点は記述的な有限サイズ交点で、漸近閾値ではない。

## 文献

* [KZH] R. Kobayashi, G. Zhu, P.-S. Hsin, *Clifford Hierarchy Stabilizer Codes: Transversal Non-Clifford Gates and Magic*, arXiv:2511.02900.
* [Tak] Y. Takada, S. D. Bartlett, D. J. Williamson, *Exact efficient simulation of noisy logical magic states using Clifford stabilizers*, arXiv:2609.16929.
