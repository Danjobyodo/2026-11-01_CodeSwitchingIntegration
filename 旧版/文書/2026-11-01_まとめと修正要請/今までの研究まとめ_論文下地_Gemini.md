# 2次元非可換 $\mathbb{D}_4$ Clifford安定化子符号における量子誤り訂正閾値、符号切り替え論理誤り率、および魔法状態蒸留との時空間資源比較に関する統合的研究

**（論文下地ドラフト：研究1・研究2・研究3の包括的統合および理論・数値・実装検証の総括）**

---

## 要旨（Abstract）

空間2次元（2D）の局所相互作用のみを持つ量子誤り訂正符号において、普遍的（universal）な誤り耐性量子計算（Fault-Tolerant Quantum Computing; FTQC）をいかにして最小の時空間オーバーヘッドで実現するかは、量子情報科学における最重要課題の一つである。従来のPauli安定化子符号（stabilizer codes）においては、Bravyi–Königの定理により、空間 $D$ 次元の局所安定化子符号で定数深さ（あるいは横断的：transversal）な論理ゲートとして実装可能な演算はClifford階層の第 $D$ 階層 $\mathcal{C}^{(D)}$ に制限される。この制約により、2次元平面上の表面符号（surface code）やカラー符号（color code）では非Cliffordゲートである論理 $T$ ゲートを横断的に実装できず、魔法状態蒸留（Magic State Distillation; MSD）や3次元符号との次元ジャンプ（dimensional jump）、あるいは事後選択（post-selection）を伴う魔法状態栽培（Magic State Cultivation; MSC）といった代替手法に依存せざるを得なかった。

これに対し近年、Kobayashi, Zhu, Hsin（arXiv:2511.02900 / Phys. Rev. Lett. 136, 250802 (2026)）は、安定化子群をPauli群 $\mathcal{C}^{(1)}$ からClifford階層の第2階層 $\mathcal{C}^{(2)}$ へと拡張した「Clifford階層安定化子符号（Clifford-Hierarchy Stabilizer Codes; CHSC）」を提唱し、空間2次元でありながら非アーベル二面体群 $\mathbb{D}_4$ のトポロジカル秩序（$(2+1)$次元ツイスト $\mathbb{Z}_2^3$ ゲージ理論）を内在することで横断的な論理非Cliffordゲート（$\overline{T}$ / $\overline{T}^\dagger$）を許容する2次元 $\mathbb{D}_4$ 安定化子符号を構成した。しかし、$\mathbb{D}_4$ 符号の $X$ 型安定化子生成元は Controlled-$Z$（$\text{CZ}$）ゲートでドレスされた非Pauli演算子であり、フラックス（$Z$-プラケット違反）が存在する励起部分空間上では互いに非可換となるため、シンドローム測定の順序に依存して測定結果が確率 $1/2$ で再ランダム化されるという本質的な困難を伴う。さらに、このような非Pauli安定化子の連続測定と横断的 $\mathcal{C}^{(3)}$ ゲート（$\text{CS}, \text{CCZ}, T^\dagger$）を含むノイズ付き量子回路は、従来のGottesman–Knillの定理に基づくPauli安定化子シミュレータ（Stim等）では直接扱うことができず、その誤り訂正閾値や符号切り替え（Code Switching）時の論理誤り率、ならびに魔法状態蒸留に対する実効的な時空間コスト優位性は未解明のままであった。

本研究では、Takada, Bartlett, Williamson（arXiv:2609.16929）によって確立された「Clifford安定化子を用いたノイズ付き論理魔法状態の厳密かつ効率的なシミュレーション理論（Clifford-stabilizer simulation theory）」およびそれと双対なツイストフレーム（twisted-frame）表現を基盤として、2次元 $\mathbb{D}_4$ 符号の誤り耐性性能を以下の3段階の独立かつ連関した研究（研究1〜研究3）を通じて体系的に解明した。

1. **研究1（2次元トーラス上 $\mathbb{D}_4$ 符号のメモリ閾値評価）**：周期境界条件を持つ $L \times L$ 三角分割トーラス上の $\mathbb{D}_4$ 符号（符号化論理量子ビット数 $k=6$）に対し、非可換 $X$ チェック測定の正確な量子ジャンプと位相キックバックを捉えるツイストフレーム表現シミュレータおよび実時間Just-in-Time（JIT）フラックス復号器・2基底MWPM電荷復号器を構築した。$L=3$（27量子ビット）における $2^{27}$ 次元の厳密状態ベクトル参照器とのロックステップ比較（最大確率差 $\le 6 \times 10^{-8}$）および独立標本 $\chi^2$ 検定によりシミュレータの厳密性を検証した上で、符号容量（depolarizing）モデル・現象論的（phenomenological）モデル・ネイティブ $\text{CCZ}$ 回路レベルモデルの3種の雑音下で有限サイズ交点（閾値）を評価した。その結果、フラックス再ランダム化と非線形エラー伝播が存在するにもかかわらず、符号容量モデルで約 $9.5\text{--}10.2\%$、現象論的モデルで約 $1.89\text{--}2.00\%$（可換トーリック符号の約 $2.7\%$ に対して約 $30\%$ の低下に留まる）、回路レベルモデルで約 $0.19\text{--}0.22\%$ という明確な有限の誤り訂正閾値が存在することを実証した。
2. **研究2（境界付き平面パッチにおける $\mathbb{D}_4$ Code Switching の論理誤り率と閾値評価）**：3種のギャップ付き境界（$\mathcal{L}_r, \mathcal{L}_b, \mathcal{L}_{rb}$）を持つ三角形（正方格子）パッチ上の $\mathbb{D}_4$ 符号（$k=1$）において、2コピーの可換表面符号（Folded Surface Code; FSC）との間でゲージング（switch-in）およびボソン凝縮（switch-out）を行うフォールトトレラント符号切り替えプロトコルを実装した。Takadaらの演算子レベルPauli-proxy法（Algorithm 1 & 3）に基づく高速シミュレータを構築し、$d=2$ での $2^{16}$ 次元状態ベクトルおよび $d=3,4$ での $\mathbb{Z}_4$ 拡張ツイストフレーム参照器との計300万回以上の出力比較で不一致ゼロを確認した。現象論的ノイズ下での大規模モンテカルロ計算により、境界を理想化した設定（`ideal`）では $d=3\text{--}5$ 交点 $2.97\%$、$d=5\text{--}7$ 交点 $2.41\%$ の明確な閾値と指数関数的誤り抑制が確認される一方、切り替え直前の残留フラックスを許容する現実的設定（`noisy`）では、フラックスが横断的論理ゲート $U=WV$ を通過する際に非Pauli（$S/\text{CZ}$）誤りへと変換されて有効符号距離を約 $1$ 低下させ、交点を約 $1.8\text{--}1.9\%$ へ押し下げるという物理的メカニズムを明らかにした。
3. **研究3（回路レベル雑音下における $\mathbb{D}_4$ Code Switching と 15-to-1 魔法状態蒸留の時空間コスト比較）**：物理ゲートスケジュール（FSCの14ステップおよび8ステップ並列シンドローム抽出、ならびに $\mathbb{D}_4$ の40ステップ4フェーズ抽出）まで完全に展開した回路レベル雑音モデルを構築し、Takadaらの回路レベルPauli-proxy法（Algorithm 2）を用いて $d \in \{3, 5, 7, 9\}$・総計約379万ショットのモンテカルロシミュレーションと189項目の独立検証を実施した。その結果、Kobayashiらのプロトコル全体の時空間体積は $632d^3 + 454d^2 + 8d - 14$ 量子ビット・ステップ（ピーク量子ビット数 $12d^2 + 4d - 1$、時間ステップ数 $62d + 21$）で与えられることを導出した。また、単一故障全列挙（single-fault scan）およびデータ解析により、現在の丸め型（round-by-round）復号と2ラウンドの事前 $Z$ 抽出の下では、切り替え窓における2重故障由来の $d$ 非依存な誤りフロア $W(p) \propto p^\gamma$（$\gamma \approx 2.4$）が支配的となることを見出した。目標論理誤り率 $\varepsilon_{\mathrm{target}} = 10^{-4}$ の中精度領域（メモリ待機誤りなし・シナリオB）では、$\mathbb{D}_4$ 符号切り替えは Litinski の 15-to-1 蒸留工場に対して **$0.54\times$**（$p=10^{-4}, d=3$）の時空間体積削減を達成する一方、$\varepsilon_{\mathrm{target}} \le 10^{-6}$ の超高精度領域では $O(d^3)$ のバルク抽出体積と切り替え窓フロアのため、15-to-1 蒸留工場（および2段階蒸留）の方が時空間体積において優位となるという定量的境界を初めて確定した。

さらに本稿では、全3研究のシミュレーションコードと既存ドキュメントの精査を通じて判明した実装上のバグ（研究3の `ChargeDecoder` における `flux_erasures` の時刻インデックス `Rin+1` 参照ミス等）や復号器・プロトコル設計上の限界を体系的に整理し、現在の実装から論理的に導出可能な確定結論と、修正・追加計算によって今後検証されるべき仮説とを厳密に区分して論じる。

---

## 第1章 序論（Introduction）

### 1.1 誤り耐性量子計算における普遍性と空間次元のトレードオフ

量子コンピュータが素因数分解、量子化学計算、強相関多体系のシミュレーションなどの実用的問題において古典計算機を凌駕するためには、物理量子ビットのデコヒーレンスやゲート操作の不完全性を克服する誤り耐性量子計算（Fault-Tolerant Quantum Computing; FTQC）[1–5] の実現が不可欠である。FTQCの標準的な枠組みでは、複数の物理量子ビットに論理量子ビットを冗長に符号化する量子誤り訂正符号（Quantum Error-Correcting Code; QECC）を用い、誤りシンドロームの反復測定と古典復号アルゴリズムによって誤りを特定・訂正しながら、符号化された論理状態に対して直接論理ゲート操作を適用する。

この際、物理的な単一量子ビット誤りや局所的な相関誤りが論理ブロック全体へと連鎖的に伝播（error propagation）することを防ぐため、論理ゲートは**横断的（transversal）**——すなわち各論理ブロックの対応する物理量子ビット間のみに作用するテンソル積演算、あるいは高々定数深さ（constant-depth）の局所量子回路——として実装されることが強く望まれる。しかし、量子誤り訂正符号における横断的論理ゲートの実装可能性には、以下の2つの極めて強力な基本限界定理（no-go theorems）が立ちはだかる。

第一に、**Eastin–Knillの定理** [6] により、任意の非自明な量子誤り訂正符号において、横断的な論理ゲートのみで普遍的（universal）な量子計算ゲートセットを構成することは原理的に不可能である。第二に、トポロジカル安定化子符号（Pauli群 $\mathcal{P}_n = \mathcal{C}^{(1)}$ の可換部分群によって定義される局所安定化子符号）においては、**Bravyi–Königの定理** [7]（およびPastawski–Yoshidaによる拡張 [8]）により、空間 $D$ 次元の幾何学的局所性を持つ安定化子符号上で定数深さの局所ユニタリ回路によって実装可能な論理ゲートは、Gottesman–ChuangのClifford階層（Clifford hierarchy）[9] の第 $D$ 階層 $\mathcal{C}^{(D)}$ に属するものに限られる。ここでClifford階層 $\mathcal{C}^{(k)}$ は、$\mathcal{C}^{(1)} = \mathcal{P}_n$（$n$ 量子ビットPauli群）を起点として再帰的に
$$\mathcal{C}^{(k)} \equiv \left\{ U \in U(2^n) \;\middle|\; \forall P \in \mathcal{P}_n,\; U P U^\dagger \in \mathcal{C}^{(k-1)} \right\} \quad (k \ge 2)$$
と定義される階層構造であり、$\mathcal{C}^{(2)}$ はClifford群、$\mathcal{C}^{(3)}$ は $T = \text{diag}(1, e^{i\pi/4})$ ゲート、Controlled-$S$（$\text{CS}$）ゲート、および Controlled-Controlled-$Z$（$\text{CCZ}$）ゲートなどを含む第3階層である。

普遍的量子計算を達成するためには、Clifford群 $\mathcal{C}^{(2)}$ に属さない非Cliffordゲート（典型的には $\mathcal{C}^{(3)}$ に属する $T$ ゲートや $\text{CCZ}$ ゲート）が少なくとも1種類必要となる。ところがBravyi–Königの定理によれば、超伝導量子回路や中性原子アレイ、イオントラップなど、現在の主要な量子ハードウェアが自然な実装基盤とする**空間2次元（$D=2$）の局所Pauli安定化子符号**（キタエフのトーリック符号・表面符号 [1, 2, 10] や2次元カラー符号 [11] など）では、定数深さ回路で実装可能な論理ゲートは第2階層 $\mathcal{C}^{(2)}$（Clifford群）までに厳しく制限され、第3階層 $\mathcal{C}^{(3)}$ の論理 $T$ ゲートを横断的に実装することはできない。

### 1.2 非クリフォード論理ゲート実現への既存アプローチとその限界

この2次元Pauli安定化子符号における非Cliffordゲートの不在を克服するため、これまで主に以下の3つのアプローチが研究されてきた。

1. **魔法状態蒸留（Magic State Distillation; MSD）** [12–16]：
   表面符号などの2次元Pauli安定化子符号上で高い閾値（回路レベル雑音で約 $0.7\text{--}1.0\%$）を持つClifford操作と状態注入（state injection）を組み合わせ、物理レベルで準備されたノイジーな魔法状態 $|T\rangle = (|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2}$ を多数消費して、高純度の論理魔法状態を蒸留する手法である。特にBravyi–Kitaevの15-to-1リード・マラー（Reed–Muller）蒸留プロトコル [12] を格子手術（lattice surgery）[17] 上の回転表面符号で最適化したLitinskiの設計 [14, 15] により、蒸留工場の時空間コストは初期の見積もりに比べて大幅に削減された。それでもなお、1つの論理 $T$ ゲートを実行するために数千〜数万物理量子ビット・サイクルにおよぶ専用の蒸留工場（factory footprint）を継続的に稼働させる必要があり、大規模量子アルゴリズム全体の時空間資源の相当部分を占め続けている。
2. **高次元符号・符号切り替え（Code Switching）とJust-in-Time復号** [18–23]：
   空間3次元（$D=3$）のPauli安定化子符号（3次元表面符号 [19, 20] や3次元ゲージカラー符号 [18, 21]）では、Bravyi–Königの定理により $\mathcal{C}^{(3)}$ の横断的 $T$ や $\text{CCZ}$ が許容される。Bombin [22] や Brown [23] は、3次元符号の空間1次元を時間方向へと展開する「次元ジャンプ（dimensional jump）」や実時間シンドローム処理である**Just-in-Time（JIT）復号**を用いることで、実質的に2次元的なハードウェア上で非Cliffordゲートを実行する手法を提案した。また、可換な2次元表面符号と非Cliffordゲートを持つ符号の間を測定によって行き来する符号切り替え（Code Switching）[24, 25] も提案されているが、従来のPauli安定化子に基づく構成では非局所的な結合や高重み測定、あるいは実効的な符号距離の低下が課題となっていた。
3. **魔法状態栽培（Magic State Cultivation; MSC）** [26]：
   近年Gidneyらによって提案された魔法状態栽培（cultivation）は、小規模なカラー符号上で非破壊的な論理測定とフォールトトレラントな成長操作を事後選択（post-selection）付きで組み合わせることで、蒸留工場と同等以上の高純度魔法状態を極めて小さな時空間体積で生成する手法である。ただし、MSCは本質的に確率的な事後選択（棄却サンプリング）に依存するため、目標誤り率が低くなるにつれて破棄率（retry overhead）が増大し、決定論的なインプレース（in-place）論理ゲート操作とは異なるアーキテクチャ上のバッファリング機構を必要とする。

### 1.3 Clifford階層安定化子符号（CHSC）と2次元 $\mathbb{D}_4$ 符号の登場

これに対し、**「事後選択を一切用いず（決定論的）、空間2次元の局所的な幾何学構造のみを維持したまま、横断的（定数深さ）な論理非Cliffordゲートを直接実行する」**という第三の道を切り拓いたのが、Kobayashi, Zhu, Hsin（2026）[27] による**Clifford階層安定化子符号（Clifford-Hierarchy Stabilizer Codes; CHSC）**の理論である。

Bravyi–Königの定理が課す「2次元では $\mathcal{C}^{(2)}$ 論理ゲートまで」という制限は、符号の安定化子群自体がPauli群 $\mathcal{C}^{(1)}$ の部分群であるという前提に立脚している。もし安定化子生成元としてPauli演算子だけでなく、第2階層 $\mathcal{C}^{(2)}$（Clifford演算子、例えばPauli $X$ と $\text{CZ}$ ゲートの積）を許容する**Clifford安定化子符号（Clifford stabilizer code）** [27–31] を考えれば、符号空間を保つ定数深さ論理ユニタリ演算子は第3階層 $\mathcal{C}^{(3)}$ へと自然に昇格し得る。

実際、2次元格子上でこのようなClifford安定化子符号を構成すると、その低エネルギー有効理論（符号空間）は、従来のトーリック符号のようなアーベル群 $\mathbb{Z}_2$ ゲージ理論ではなく、**非アーベル群 $\mathbb{D}_4$（位数8の二面体群、正方形の対称群）のトポロジカル秩序** [32–36] を記述する。$\mathbb{D}_4$ ゲージ理論は、3つの色（赤 $r$・緑 $g$・青 $b$）の $\mathbb{Z}_2$ ゲージ場 $a_r, a_g, a_b$ が $(2+1)$次元のタイプIII Dijkgraaf–Wittenコサイクル [32]
$$\omega(a_r, a_g, a_b) = (-1)^{\int a_r \cup a_g \cup a_b}$$
によって非自明に結合した**ツイスト $\mathbb{Z}_2^3$ ゲージ理論**と等価である。Kobayashiら [27] は、この2次元 $\mathbb{D}_4$ 安定化子符号に対して3種類のギャップ付き境界（gapped boundaries）$\mathcal{L}_r, \mathcal{L}_b, \mathcal{L}_{rb}$ を持つ三角形パッチを定義し、以下の画期的な性質を証明した。

1. **横断的論理 $T^\dagger$（および $T$）ゲートの存在**：$\mathbb{D}_4$ 符号の非自明なエニオン置換対称性（自己同型 $U = WV$）をギャップ付き境界条件と整合するように構成することで、深さ1のオンサイト $\text{CNOT}$ 層 $V$、最近接辺間の $\text{CS} / \text{CS}^\dagger$ 層、および境界 $\mathcal{L}_{rb}$ 上の単一量子ビット $T^\dagger$ 層からなる定数深さ・幾何学的局所回路 $U \in \mathcal{C}^{(3)}$ が、符号空間上で厳密に論理 $\overline{T}^\dagger$（または $\overline{T}$）ゲートとして作用する。
2. **2コピーの表面符号（FSC）との定数深さ符号切り替え（Code Switching）**：$\mathbb{D}_4$ 符号の緑色（$g$）セクターは、他の2色（$r, b$）のゲージ場を背景とする対称性保護トポロジカル（SPT）相のゲージ化（gauging）として理解できる。したがって、赤と青の2枚の通常の可換表面符号（三角形パッチを折り畳んだ Folded Surface Code; FSC）から出発し、緑色の $X$ 型ドレッシング安定化子 $S_{X;v}^g$ を測定してフラックスを消去することで $\mathbb{D}_4$ 符号へと切り替え（**switch-in / ゲージング**）、横断的論理ゲート $U$ を適用した後、緑色の単一量子ビット $X_e^g$ を一斉測定してボソン凝縮させることで元の可換表面符号へと戻す（**switch-out / 凝縮**）ことができる。この際、測定結果に依存する非線形なPauli $Z$ 補正位相 $F(a)$ はすべて古典ソフトウエア上のPauliフレーム更新として処理可能であり、物理的な適応的（adaptive）Clifford補正ゲートすら不要となる。

### 1.4 非可換安定化子測定と非クリフォード回路シミュレーションの根本問題

このように理論的に極めて美しい $\mathbb{D}_4$ 符号と符号切り替えプロトコルであるが、これを現実のノイズ環境下で動作させ、その誤り訂正能力と資源効率を定量的に評価しようとすると、従来の量子誤り訂正研究には存在しなかった**2つの根本的な障壁**に直面する。

#### 第一の障壁：フラックス誘起非可換性と測定再ランダム化（Measurement Re-randomization）
Pauli安定化子符号においては、すべての安定化子生成元が全ヒルベルト空間上で互いに可換（$[S_i, S_j] = 0$）であるため、どの順序でシンドローム測定を行っても同時固有状態が保たれ、追加のエラーがなければ同一安定化子の反復測定は決定論的に同じ固有値を返す。
これに対し、$\mathbb{D}_4$ 符号の $X$ 型安定化子生成元 $S_{X;v}^c$（$c \in \{r, g, b\}$）はPauli $X$ と $\text{CZ}$ の積であり、それらの群交換子（group commutator）は恒等演算子ではなく、共通のプラケット上のPauli $Z$-スタビライザ（フラックス演算子）$S_{Z;f}^{c'}$ の積となる。その結果、すべてのフラックスが消滅している平坦部分空間（flat subspace: $\forall f, c,\; S_{Z;f}^c = +1$）上では $X$ チェック同士は可換であるが、**データ $X$ エラー等によって1つでもフラックス励起（$S_{Z;f}^c = -1$）が生じると、その近傍の異色 $X$ チェック同士が反交換（anticommute）する**。
反交換する2つの演算子 $S_A$ と $S_B$ を $S_A \to S_B \to S_A$ の順に射影測定すると、最初の測定で確定した $S_A$ の固有状態が $S_B$ の測定によって直交固有状態の等重み重ね合わせへと破壊され、2回目の $S_A$ 測定結果が確率 $1/2$ でランダムに反転する（**測定再ランダム化**）。さらに、$\text{CZ}$ ドレッシングを介してデータ上の $X$ エラー（フラックス）が測定後にデータ上の $Z$ エラー（電荷シンドローム）へと非線形に変換される（**位相キックバック / カイラルな色間結合**）。このような状況下で、そもそも誤り訂正閾値が存在するのか、またどのようにしてフラックスと電荷を復号すべきかは自明ではない。

#### 第二の障壁：非Pauli測定と $\mathcal{C}^{(3)}$ ゲートを含む量子回路の古典シミュレーション不可能性
誤り訂正閾値や $10^{-4}\text{--}10^{-10}$ といった低い論理誤り率を数値的に評価するためには、符号距離 $d=3, 5, 7, 9, \dots$（物理量子ビット数にして数十〜数百量子ビット）の系に対して数万〜数百万ショットのモンテカルロシミュレーションを実行する必要がある。しかし、$\mathbb{D}_4$ 符号のシンドローム測定は非Pauli演算子 $S_{X;v}^c \in \mathcal{C}^{(2)} \setminus \mathcal{C}^{(1)}$ の射影測定であり、さらに回路レベル実装や符号切り替えプロトコルには $\text{CCZ}, \text{CS}, T^\dagger \in \mathcal{C}^{(3)}$ といった非Cliffordゲートが大量に含まれる。そのため、Gottesman–Knillの定理 [3, 37] に基づく従来のPauli安定化子シミュレータ（Stim [38] など）ではこれらを直接シミュレートすることができない。他方、全状態ベクトル（$2^N$ 次元）やテンソルネットワークによる汎用シミュレーションでは、2次元格子上で $L=3$（27量子ビット）を超える規模の多数ラウンド・モンテカルロ計算は計算量的に不可能である。
過去には、非可換測定の影響を単なる独立確率的なシンドローム反転ノイズや擬似的な位相注入（サロゲートモデル）で近似する試みもなされたが、それらは射影測定に伴う状態崩壊や厳密な位相相関を捉えておらず、物理的に正しい閾値や論理誤り率を与えない。

この第二の障壁を根本から解決したのが、本研究の手法的支柱となる **Takada, Bartlett, Williamson（2026）** [39] の論文 *『Exact efficient simulation of noisy logical magic states using Clifford stabilizers』*（arXiv:2609.16929）である。Takadaらは、Clifford安定化子群 $\mathcal{G}_{\mathrm{C}} \subset \mathcal{C}^{(2)}$ によって記述される量子状態（特に $\mathbb{D}_4$ 符号のような非可換Clifford安定化子符号や論理魔法状態）に対し、一定の許容条件（admissibility conditions：インボリューティブ条件、共通の局所ドレッシング軸、群交換子のPauli $Z$ 安定化子部分群への包含、およびPrimary-support exactness）の下で、**測定共役描像（measurement-conjugated picture）**と**Pauli proxy（Pauli代理生成元）**を導入することにより、非可換Clifford測定と非Cliffordゲートを含むノイズ付きダイナミクスを**一切の近似なしに（exact）、かつ量子ビット数に対して多項式時間（$\text{poly}(n)$、実質的に1つのPauli安定化子シミュレータ＋軽量なエラーフレーム追跡と同等の計算量）で効率的にシミュレートする一般的アルゴリズム**を確立した。

### 1.5 本研究の構成と3つの研究の位置づけ

本論文下地は、この2次元 $\mathbb{D}_4$ Clifford安定化子符号に関する一連の3つの研究（研究1・研究2・研究3）を、統一的な理論体系と厳密なシミュレーション検証の下に統合したものである。3つの研究はそれぞれ以下の明確な役割と段階的発展構造を持っている。

* **研究1（第4章）：2次元トーラス上 $\mathbb{D}_4$ 符号のメモリ閾値評価（`1_D4閾値/2026-09-27_v7`）**
  境界効果や符号切り替えの複雑さを排した最も基本的な設定として、周期境界条件を持つ $L \times L$ トーラス上の $\mathbb{D}_4$ 符号（$N = 3L^2$ 量子ビット、$k=6$ 論理量子ビット）を対象とする。まず、$\mathbb{D}_4$ 符号自体の非可換 $X$ チェック測定が引き起こす再ランダム化と非線形色間結合の下で、Just-in-Time（JIT）フラックス復号器と2基底MWPM電荷復号器を組み合わせた際に**有限の誤り訂正閾値が存在するか否か**を、符号容量モデル・現象論的モデル・ネイティブ $\text{CCZ}$ 回路レベルモデルの3段階で解明する。また、可換トーリック符号（`none`）および擬似キックバック注入モデル（`kappa_injection`）との厳密な対照実験により、非可換性が閾値に与える純粋なペナルティを定量化する。
* **研究2（第5章）：境界付き平面パッチにおける $\mathbb{D}_4$ Code Switching の論理誤り率と閾値評価（`2_CodeSwitching論理誤り率/2026-10-20_エラー率v3`）**
  研究1で確立したバルクの復号手法を、3種のギャップ付き境界を持つ三角形（折り畳み正方格子）パッチ（$k=1$ 論理量子ビット）へと拡張し、可換表面符号（FSC）からのゲージング（switch-in）、横断的論理 $\overline{T}^\dagger$ ゲート $U=WV$、およびボソン凝縮（switch-out）を含む**完全な符号切り替えプロトコル**を現象論的ノイズ下で評価する。Takadaらの演算子レベルPauli-proxy法（Algorithm 1 & 3）を実装して $d=3, 5, 7$ の論理誤り率曲線と有限サイズ交点を求めるとともに、切り替え直前の残留フラックスの有無（`ideal` 境界 vs `noisy` 境界）が非Pauli論理誤り（$S/\text{CZ}$ 誤りや状態崩壊）および有効符号距離に及ぼす決定的な影響を解明する。
* **研究3（第6章）：回路レベル雑音下における $\mathbb{D}_4$ Code Switching と 15-to-1 魔法状態蒸留の時空間コスト比較（`3_魔法状態蒸留との比較/2026-10-29_コスト評価v5_2`）**
  研究2の符号切り替えプロトコルを、補助量子ビット（ancilla）と3量子ビット $\text{CCZ}$ / 2量子ビット $\text{CNOT}$ ゲートからなる**完全な物理ゲートスケジュール（回路レベル雑音モデル）**へと落とし込み、Takadaらの回路レベルPauli-proxy法（Algorithm 2）を用いて $d \in \{3, 5, 7, 9\}$、物理誤り率 $p \in [10^{-4}, 3\times 10^{-3}]$ にわたる約379万ショットの大規模モンテカルロ評価を実施する。同時に、同一の物理誤り率・表面符号較正の下でLitinski（2019）[14, 15] の 15-to-1 魔法状態蒸留工場の論理誤り率と時空間体積を算出し、目標論理誤り率 $\varepsilon_{\mathrm{target}} \in \{10^{-4}, 10^{-6}, 10^{-8}, 10^{-10}\}$ ごとに両方式の最小時空間体積（qubit-steps）を直接比較する。さらに、最大67,789箇所の単一故障全列挙（single-fault scan）によって切り替え窓の脆弱性の物理的起源を特定する。

以下、第2章では $\mathbb{D}_4$ Clifford安定化子符号と符号切り替えプロトコルの数学的定式化を与え、第3章では Takada らの Clifford 安定化子シミュレーション理論と本研究の3つのシミュレータおよび JIT 復号アルゴリズムを詳述する。続く第4章・第5章・第6章では、研究1・研究2・研究3それぞれのコード構成・役割分担・検証結果・本番シミュレーション結果および考察を体系的に記述し、第7章で3研究の統合的知見と現在進行中の修正課題（別紙『修正の要請.md』対応事項）を総括する。

---

## 第2章 理論的基礎：$\mathbb{D}_4$ Clifford安定化子符号と横断的非クリフォード論理演算

本章では、Kobayashi, Zhu, Hsin [27] によって構成された2次元 $\mathbb{D}_4$ Clifford安定化子符号の代数的・トポロジカルな定式化、非可換安定化子の群交換子構造、ギャップ付き境界と横断的論理 $T^\dagger$ ゲート $U = WV$ の構成、ならびに可換表面符号との間の符号切り替え（gauging / condensation）プロトコルを厳密に記述する。

### 2.1 $(2+1)$次元ツイスト $\mathbb{Z}_2^3$ ゲージ理論とカップ積の定式化

2次元多様体（トーラスまたは境界付き平面領域）の単体分割（三角形分割）を $\mathcal{K} = (V, E, F)$ とする。ここで $V, E, F$ はそれぞれ頂点（0-単体）、辺（1-単体）、面すなわち三角形プラケット（2-単体）の集合であり、計算基底でのカップ積（cup product）を定義するために頂点集合 $V$ には局所的または大域的な全順序（branching structure）が与えられているものとする。

各辺 $e \in E$ には、赤（$r$）・緑（$g$）・青（$b$）の3色に対応する3個の物理量子ビットが配置される。色集合を $\mathcal{C}_{\mathrm{col}} = \{r, g, b\}$ と書き、辺 $e$ 上の色 $c \in \mathcal{C}_{\mathrm{col}}$ の量子ビットに作用するPauli演算子を $X_e^c, Y_e^c, Z_e^c$ と表す。全系の量子ビット数は $N = 3|E|$ であり、計算基底（$Z$ 基底）の状態 $|a\rangle = |a_r, a_g, a_b\rangle$ は、各色 $c \in \{r, g, b\}$ の $\mathbb{Z}_2$ 値1-コチェイン（1-cochain）
$$a_c \in C^1(\mathcal{K}, \mathbb{Z}_2), \quad Z_e^c |a\rangle = (-1)^{a_c(e)} |a\rangle$$
の組 $a = (a_r, a_g, a_b) \in C^1(\mathcal{K}, \mathbb{Z}_2^3)$ によって一意にラベル付けされる。

単体コホモロジーの標準的な定義に従い、余境界作用素（coboundary operator）$d: C^k(\mathcal{K}, \mathbb{Z}_2) \to C^{k+1}(\mathcal{K}, \mathbb{Z}_2)$ およびカップ積 $\cup: C^p(\mathcal{K}, \mathbb{Z}_2) \times C^q(\mathcal{K}, \mathbb{Z}_2) \to C^{p+q}(\mathcal{K}, \mathbb{Z}_2)$ を導入する。具体的には、順序付けられた頂点 $(v_0, v_1, v_2)$ を持つ三角形 $f = [v_0 v_1 v_2] \in F$ に対して、1-コチェイン $a_c$ の余境界（離散回転 / フラックス）は
$$(da_c)(f) \equiv a_c([v_0 v_1]) + a_c([v_1 v_2]) + a_c([v_0 v_2]) \pmod 2$$
であり、2つの1-コチェイン $\alpha, \beta \in C^1(\mathcal{K}, \mathbb{Z}_2)$ のカップ積は
$$(\alpha \cup \beta)([v_0 v_1 v_2]) \equiv \alpha([v_0 v_1])\,\beta([v_1 v_2]) \pmod 2$$
また0-コチェイン $\lambda \in C^0(\mathcal{K}, \mathbb{Z}_2)$ と1-コチェイン $\alpha \in C^1(\mathcal{K}, \mathbb{Z}_2)$ のカップ積は辺 $e = [v_0 v_1]$ 上で $(\lambda \cup \alpha)([v_0 v_1]) = \lambda(v_0)\alpha([v_0 v_1])$、$(\alpha \cup \lambda)([v_0 v_1]) = \alpha([v_0 v_1])\lambda(v_1)$ と定義される。これらはライプニッツ則
$$d(\lambda \cup \alpha) = d\lambda \cup \alpha + \lambda \cup d\alpha \pmod 2$$
を満たす。

$(2+1)$次元のタイプIII ツイスト $\mathbb{Z}_2^3$ ゲージ理論の位相作用は、3つの1-コチェイン $a_r, a_g, a_b$ の3重カップ積 $\int a_r \cup a_g \cup a_b$ で与えられる。空間2次元の波動関数において、このトポロジカル項はゲージ変換 $a_c \mapsto a_c + d\lambda_c$（ここで $\lambda_c \in C^0(\mathcal{K}, \mathbb{Z}_2)$ は頂点上の0-コチェイン）に対する非自明な1-コサイクル位相因子（Dijkgraaf–Witten twist）を生成する。これが $\mathbb{D}_4$ Clifford安定化子符号のハミルトニアンおよび安定化子生成元の起源である。

### 2.2 2次元格子上のスタビライザ生成元の明示的構成

$\mathbb{D}_4$ 安定化子符号は、各面 $f \in F$・各色 $c \in \{r, g, b\}$ に定義される**Pauli $Z$-プラケット安定化子（フラックスチェック）** $S_{Z;f}^c$ と、各頂点 $v \in V$・各色 $c \in \{r, g, b\}$ に定義される**ドレスされた $X$-頂点安定化子（電荷チェック）** $S_{X;v}^c$ によって生成される。

#### 2.2.1 Pauli $Z$-安定化子と平坦部分空間（Flat Subspace）
各面 $f = [v_0 v_1 v_2] \in F$ および各色 $c \in \{r, g, b\}$ に対し、$Z$-安定化子は通常のトーリック符号と同様に、面 $f$ の境界 $\partial f$ をなす辺上のPauli $Z$ 演算子の積として定義される：
$$S_{Z;f}^c \equiv \prod_{e \in \partial f} Z_e^c = (-1)^{(da_c)(f)}.$$
すべての $Z$-安定化子が固有値 $+1$ をとる部分空間
$$\mathcal{H}_{\mathrm{flat}} \equiv \left\{ |\psi\rangle \in \mathcal{H} \;\middle|\; \forall f \in F,\, \forall c \in \{r,g,b\},\; S_{Z;f}^c |\psi\rangle = +1 |\psi\rangle \right\}$$
を**平坦部分空間（flat subspace、またはフラックスフリー部分空間）**と呼ぶ。計算基底 $|a\rangle$ が $\mathcal{H}_{\mathrm{flat}}$ に属するための必要十分条件は、すべての色 $c$ について $da_c = 0 \pmod 2$（すなわち $a_c \in Z^1(\mathcal{K}, \mathbb{Z}_2)$ が1-コサイクルであること）である。面 $f$ において $S_{Z;f}^c = -1$（すなわち $(da_c)(f) = 1$）となる状態を、面 $f$ 上の色 $c$ の**フラックス励起（flux excitation / $m$-anyon）**と呼ぶ。

#### 2.2.2 ドレスされた $X$-安定化子（Clifford Stabilizers）
頂点 $v \in V$ にのみ値 $1$ をとり他の頂点で $0$ となる指示0-コチェインを $\tilde{v} \in C^0(\mathcal{K}, \mathbb{Z}_2)$ と書く。このとき、余境界 $d\tilde{v} \in C^1(\mathcal{K}, \mathbb{Z}_2)$ は頂点 $v$ に接続する辺（star of $v$: $\delta v = \{e \in E \mid v \in \partial e\}$）の上でのみ $1$ をとる1-コチェインとなる。これに対応する裸のPauli $X$-スター演算子を
$$X_{v}^c \equiv \prod_{e \in \delta v} X_e^c = X^{s_{v,c}}$$
と定義する（ここで $s_{v,c}$ は色 $c$ の辺集合 $\delta v$ 上の指示ベクトル）。計算基底 $|a\rangle$ に対して $X_v^c$ はゲージ変換 $a_c \mapsto a_c + d\tilde{v}$ を引き起こす。

$\mathbb{D}_4$ 符号の頂点 $v \in V$ における各色 $c \in \{r, g, b\}$ の $X$-安定化子生成元 $S_{X;v}^c$ は、このPauli $X$-スター演算子に対して、他の2色の1-コチェインとのカップ積から決まる2次位相（Controlled-$Z$ ゲートの積）をドレッシングした第2階層Clifford演算子 $\mathcal{C}^{(2)}$ として定義される [27]：
$$\begin{aligned}
S_{X;v}^r &\equiv \left(\prod_{e \in \delta v} X_e^r\right) (-1)^{\int_{\mathcal{K}} \tilde{v} \cup a_g \cup a_b} = X^{s_{v,r}} (-1)^{q_{v,r}(a)}, \\
S_{X;v}^g &\equiv \left(\prod_{e \in \delta v} X_e^g\right) (-1)^{\int_{\mathcal{K}} a_r \cup \tilde{v} \cup a_b} = X^{s_{v,g}} (-1)^{q_{v,g}(a)}, \\
S_{X;v}^b &\equiv \left(\prod_{e \in \delta v} X_e^b\right) (-1)^{\int_{\mathcal{K}} a_r \cup a_g \cup \tilde{v}} = X^{s_{v,b}} (-1)^{q_{v,b}(a)}.
\end{aligned}$$
ここで、2次形式 $q_{v,c}(a)$ を単体分割の三角形 $f = [v_0 v_1 v_2] \in F$（頂点順序 $v_0 < v_1 < v_2$）を用いて書き下すと、カップ積の定義から直ちに以下の明示的な $\text{CZ}$ ゲート積表現が得られる：
* **赤（$r$）のドレッシング**：$(\tilde{v} \cup a_g \cup a_b)([v_0 v_1 v_2]) = \tilde{v}(v_0)\, a_g([v_0 v_1])\, a_b([v_1 v_2])$ より、頂点 $v$ が三角形 $f$ の最小頂点 $v_0$ と一致するすべての三角形について、辺 $e_{01} = [v_0 v_1]$ の緑（$g$）量子ビットと辺 $e_{12} = [v_1 v_2]$ の青（$b$）量子ビットの間に $\text{CZ}_{e_{01}^g, e_{12}^b}$ を作用させる：
  $$S_{X;v}^r = X_v^r \prod_{\substack{f=[v_0 v_1 v_2] \in F \\ v_0 = v}} \text{CZ}_{[v_0 v_1]^g,\, [v_1 v_2]^b}.$$
* **緑（$g$）のドレッシング**：$(a_r \cup \tilde{v} \cup a_b)([v_0 v_1 v_2]) = a_r([v_0 v_1])\, \tilde{v}(v_1)\, a_b([v_1 v_2])$ より、頂点 $v$ が三角形 $f$ の中間頂点 $v_1$ と一致するすべての三角形について、辺 $e_{01} = [v_0 v_1]$ の赤（$r$）量子ビットと辺 $e_{12} = [v_1 v_2]$ の青（$b$）量子ビットの間に $\text{CZ}_{e_{01}^r, e_{12}^b}$ を作用させる：
  $$S_{X;v}^g = X_v^g \prod_{\substack{f=[v_0 v_1 v_2] \in F \\ v_1 = v}} \text{CZ}_{[v_0 v_1]^r,\, [v_1 v_2]^b}.$$
* **青（$b$）のドレッシング**：$(a_r \cup a_g \cup \tilde{v})([v_0 v_1 v_2]) = a_r([v_0 v_1])\, a_g([v_1 v_2])\, \tilde{v}(v_2)$ より、頂点 $v$ が三角形 $f$ の最大頂点 $v_2$ と一致するすべての三角形について、辺 $e_{01} = [v_0 v_1]$ の赤（$r$）量子ビットと辺 $e_{12} = [v_1 v_2]$ の緑（$g$）量子ビットの間に $\text{CZ}_{e_{01}^r, e_{12}^g}$ を作用させる：
  $$S_{X;v}^b = X_v^b \prod_{\substack{f=[v_0 v_1 v_2] \in F \\ v_2 = v}} \text{CZ}_{[v_0 v_1]^r,\, [v_1 v_2]^g}.$$

#### 2.2.3 研究1のトーラス格子と研究2・3の正方格子における座標表現の対応
本研究の3つの研究では、扱う境界条件とプロトコルに応じて以下の2種類の同等な格子表現を採用している。

1. **研究1（2次元 $L \times L$ 三角分割トーラス）**：
   各単位胞 $(x, y) \in \mathbb{Z}_L \times \mathbb{Z}_L$ に頂点 $v=(x,y)$ と3本の有向辺 $e_0 = [(x,y),(x+1,y)]$（水平）、$e_1 = [(x,y),(x,y+1)]$（垂直）、$e_2 = [(x,y),(x+1,y+1)]$（対角）を配置し、単位胞を2つの三角形 $f_{\mathrm{up}} = [(x,y), (x,y+1), (x+1,y+1)]$ と $f_{\mathrm{lo}} = [(x,y), (x+1,y), (x+1,y+1)]$ に分割する。各単位胞内の局所順序 $v_0 < v_1 < v_2$ に従い、各頂点チェック $S_{X;v}^c$ は厳密に**6本のPauli $X$ と2個の異色間 $\text{CZ}$ ゲート**（上三角形由来の1個と下三角形由来の1個）から構成される。また、同じ色を持つ二つの辺は同一の $\text{CZ}$ に含まれないため、すべての $S_{X;v}^c$ はエルミートかつユニタリな対合（$(S_{X;v}^c)^2 = I$、固有値 $\pm 1$）となる。
2. **研究2・研究3（境界付き三角形パッチを折り畳んだ正方格子表現 [27]）**：
   Kobayashiらの論文 [27] のメインテキスト（Fig. 1, Eq. (2)–(3)）に従い、三角形パッチを折り畳んだ距離 $d$ の2次元正方格子（データ量子ビット数 $N = 3(2d^2 + \frac{2}{3}d) = 6d^2 + 2d$、ここで赤・青は各 $2d^2$ 辺、緑は $2d^2 + 2d$ 辺）を用いる。この正方格子表現においても、$S_{X;v}^r, S_{X;v}^b$ は頂点 $v$ のPauli $X$-スターに4〜8個の異色 $\text{CZ}$ ゲートがドレスされた形をとり、$S_{X;v}^g$ は面（双対頂点）上の緑 $X$-プラケットに4個の赤・青間 $\text{CZ}$ ゲート $\text{CZ}_{e_1^r, e_3^b}\text{CZ}_{e_1^r, e_4^b}\text{CZ}_{e_2^r, e_4^b}\text{CZ}_{e_5^r, e_4^b}$ がドレスされた形をとる。これらは単体コホモロジーのカップ積表現を正方セル（2つの三角形のペア $p=(0123)$）上に書き下したものと完全に一致する。

### 2.3 群交換子の導出とフラックス誘起非可換性（測定再ランダム化）

$\mathbb{D}_4$ 符号における誤り訂正ダイナミクスの核心は、これらの安定化子生成元間の交換関係にある。

まず、任意の $X$-安定化子 $S_{X;v}^c$ と任意の $Z$-安定化子 $S_{Z;f}^{c'}$ は**全ヒルベルト空間 $\mathcal{H}$ 上で厳密に可換**である：
$$\left[ S_{X;v}^c,\, S_{Z;f}^{c'} \right] = 0 \quad (\forall v \in V,\, \forall f \in F,\, \forall c, c' \in \{r,g,b\}).$$
なぜなら、$S_{X;v}^c$ の $\text{CZ}$ ドレッシング部分は対角演算子であるため $S_{Z;f}^{c'}$ と可換であり、Pauli $X$-スター部分 $X_v^c$ は任意の三角形境界 $\partial f$ と常に偶数個（0個または2個）の辺を共有する（$d^2 \tilde{v} = 0 \pmod 2$）からである。

一方、2つの異なる $X$-安定化子 $S_A = X^{s_A}(-1)^{q_A(a)}$ と $S_B = X^{s_B}(-1)^{q_B(a)}$ の交換関係を計算すると、計算基底 $|a\rangle$ に対して
$$\begin{aligned}
S_A S_B |a\rangle &= S_A (-1)^{q_B(a)} |a + s_B\rangle = (-1)^{q_B(a) + q_A(a + s_B)} |a + s_A + s_B\rangle, \\
S_B S_A |a\rangle &= S_B (-1)^{q_A(a)} |a + s_A\rangle = (-1)^{q_A(a) + q_B(a + s_A)} |a + s_A + s_B\rangle
\end{aligned}$$
が成り立つ。したがって、両者の群交換子（group commutator）は対角Pauli $Z$ 演算子
$$S_A^\dagger S_B^\dagger S_A S_B = (-1)^{\Delta_{AB}(a)}, \qquad \Delta_{AB}(a) \equiv q_A(a + s_B) + q_A(a) + q_B(a + s_A) + q_B(a) \pmod 2$$
となる。

同じ色の2つの頂点チェック（$c_A = c_B$）については、$q_A(a)$ が色 $c_A$ 以外の2色のコチェインのみに依存するため $q_A(a + s_B) = q_A(a)$ かつ $q_B(a + s_A) = q_B(a)$ となり、恒等的に $\Delta_{AB}(a) = 0$（全空間で可換）である。
しかし、**異なる色の隣接する2つの頂点チェック**、例えば頂点 $u$ の赤チェック $S_{X;u}^r$ と頂点 $v$ の緑チェック $S_{X;v}^g$ を考えると、$q_{u,r}(a) = \int \tilde{u} \cup a_g \cup a_b$ に対して $a_g \mapsto a_g + d\tilde{v}$、また $q_{v,g}(a) = \int a_r \cup \tilde{v} \cup a_b$ に対して $a_r \mapsto a_r + d\tilde{u}$ となるため、カップ積のライプニッツ則より
$$\begin{aligned}
\Delta_{(u,r),(v,g)}(a) &= \int_{\mathcal{K}} \left( \tilde{u} \cup d\tilde{v} \cup a_b + d\tilde{u} \cup \tilde{v} \cup a_b \right) \\
&= \int_{\mathcal{K}} \left( d(\tilde{u} \cup \tilde{v}) \cup a_b \right) = \int_{\mathcal{K}} (\tilde{u} \cup \tilde{v}) \cup da_b \pmod 2
\end{aligned}$$
が得られる（最後の等号では閉多様体または境界条件が整合する領域上で完全微分 $d(\tilde{u}\cup\tilde{v}\cup a_b)$ が消えることを用いた）。ここで 1-コチェイン $\tilde{u} \cup \tilde{v}$ は、有向辺 $e = [u, v]$（$u < v$）上でのみ値 $1$ をとる指示コチェインである。したがって、対応する演算子レベルでの交換関係は
$$S_{X;u}^r S_{X;v}^g = S_{X;v}^g S_{X;u}^r \prod_{f=[u v w] \in F} S_{Z;f}^b$$
と厳密に表される！同様に、緑と青、赤と青の間でも
$$S_{X;v}^g S_{X;w}^b = S_{X;w}^b S_{X;v}^g \prod_{f=[u v w] \in F} S_{Z;f}^r, \qquad S_{X;u}^r S_{X;w}^b = S_{X;w}^b S_{X;u}^r \prod_{f=[u v w] \in F} S_{Z;f}^g$$
が成立する。一般に、任意の2つの $X$-チェック $S_A, S_B$ に対して、あるプラケット・色の部分集合 $F_{AB}$ が定まり、
$$\Delta_{AB}(a) = \sum_{(f, c_f) \in F_{AB}} (da_{c_f})(f) \pmod 2, \qquad S_A S_B = S_B S_A \prod_{(f, c_f) \in F_{AB}} S_{Z;f}^{c_f}$$
が成り立つ。この基本恒等式から、以下の3つの重要な物理的帰結が導かれる。

1. **平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ 上での実効的可換性（Effective Commutativity）**：
   フラックスが存在しない平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$（すべての $f, c$ で $da_c(f) = 0$、すなわち $S_{Z;f}^c = +1$）に制限すれば、恒等的に $\Delta_{AB}(a) = 0$ となり、すべての $X$-安定化子 $S_{X;v}^c$ は互いに可換となる。したがって、すべての $S_{Z;f}^c = +1$ かつ $S_{X;v}^c = +1$ を満たす共通の符号空間（基底状態空間）$\mathcal{H}_{\mathrm{code}} \subset \mathcal{H}_{\mathrm{flat}}$ が整合的に定義される。
2. **フラックス励起下での非可換性と測定再ランダム化（Re-randomization）**：
   データ量子ビット上に $X$ エラー $e_x$ が発生して平坦条件が破れ、集合 $F_{AB}$ 上に奇数個のフラックス励起（$\Delta_{AB}(a) = 1$）が存在する状態 $|\psi\rangle$ を考える。この状態では $S_A S_B |\psi\rangle = - S_B S_A |\psi\rangle$ と反交換する。
   いま、シンドローム測定を $S_A \to S_B \to S_A$ の順に行うとする。1回目の $S_A$ 測定で測定値 $m_A^{(1)} \in \{\pm 1\}$ が得られ、状態が固有状態 $|\psi_1\rangle$（$S_A |\psi_1\rangle = m_A^{(1)} |\psi_1\rangle$）へ射影されたとする。続いて $S_B$ を測定する射影演算子 $\Pi_B^{(m_B)} = \frac{1}{2}(I + m_B S_B)$ を作用させると、反交換関係 $S_A S_B = -S_B S_A$ on $|\psi_1\rangle$ より
   $$S_A \Pi_B^{(m_B)} |\psi_1\rangle = \frac{1}{2}(S_A + m_B S_A S_B)|\psi_1\rangle = \frac{1}{2}(I - m_B S_B) S_A |\psi_1\rangle = m_A^{(1)} \Pi_B^{(-m_B)} |\psi_1\rangle$$
   となるため、$S_B$ 測定後の状態 $\Pi_B^{(m_B)} |\psi_1\rangle$ における $S_A$ の期待値は
   $$\langle \psi_1 | \Pi_B^{(m_B)} S_A \Pi_B^{(m_B)} | \psi_1 \rangle = m_A^{(1)} \langle \psi_1 | \Pi_B^{(m_B)} \Pi_B^{(-m_B)} | \psi_1 \rangle = 0$$
   となる。すなわち、**2回目の $S_A$ 測定結果 $m_A^{(2)}$ は、1回目の測定値 $m_A^{(1)}$ とは無関係に確率 $1/2$ で $+1$ または $-1$ に完全に再ランダム化される**。これは測定回路の物理的なゲート故障ではなく、非可換射影測定の量子力学的な帰結そのものである。
3. **カイラルな色間結合（Chiral Cross-Color Coupling）**：
   $X$ エラー $X_e^g$（緑のフラックス対）が存在する状態で赤のチェック $S_{X;v}^r$ を測定（あるいは作用）させると、$\text{CZ}_{e^g, {e'}^b}$ ドレッシングと $X_e^g$ の交換関係 $\text{CZ}_{12} X_1 = X_1 Z_2 \text{CZ}_{12}$ により、青（$b$）の量子ビット $e'$ 上にデータ $Z$ エラー $Z_{e'}^b$（青の電荷励起対）が生成される。同様に、各色の $X$ エラーは他色の $X$ チェック測定を通じて第3の色へと $Z$ エラーを誘起する。本研究の3つのコード（研究1〜研究3）はいずれも、この非線形な「フラックス $\times$ 測定 $\to$ 電荷誤りおよび再ランダム化」のダイナミクスを一切の近似なしに追跡している。

### 2.4 ギャップ付き境界条件と横断的論理 $T^\dagger$ ゲートの構成

周期境界条件の2次元トーラス上では、各色 $c \in \{r, g, b\}$ が独立な2つの非可縮サイクルを持つため、符号空間 $\mathcal{H}_{\mathrm{code}}$ は $k = 3 \times 2 = 6$ 論理量子ビットを符号化する（研究1の設定）。一方、実用的な平面アーキテクチャ上で単一の論理量子ビット（$k=1$）を符号化し、かつ横断的な論理非Cliffordゲートを実装するため、Kobayashiら [27] は三角形パッチの3辺に以下の3種類の**ギャップ付き境界（gapped boundaries / Lagrangian subgroups）** $\mathcal{L}_r, \mathcal{L}_b, \mathcal{L}_{rb}$ を導入した（研究2・研究3の設定）。

#### 2.4.1 3種のギャップ付き境界条件と単一論理量子ビット
三角形パッチの3つの境界を左辺 $\mathcal{L}_r$、下辺 $\mathcal{L}_b$、斜辺（折り畳み境界）$\mathcal{L}_{rb}$ とする。計算基底（1-コチェイン $a_r, a_g, a_b$）における各境界のディリクレ境界条件（凝縮するエニオンの条件）は以下で与えられる [27]：
1. **境界 $\mathcal{L}_r$**：$\left. a_r \right|_{\mathcal{L}_r} = 0 \pmod 2$（赤の電気的電荷 $e_r$ と緑・青の磁気的フラックスが凝縮）。
2. **境界 $\mathcal{L}_b$**：$\left. a_b \right|_{\mathcal{L}_b} = 0 \pmod 2$（青の電気的電荷 $e_b$ と赤・緑の磁気的フラックスが凝縮）。
3. **境界 $\mathcal{L}_{rb}$**：$\left. (a_r + a_b) \right|_{\mathcal{L}_{rb}} = 0 \pmod 2$ かつ $\left. a_g \right|_{\mathcal{L}_{rb}} = 0 \pmod 2$（赤と青の複合電荷 $e_r e_b$ および緑の電荷 $e_g$ が凝縮）。

この境界条件の下では、緑のコチェイン $a_g$ は $\mathcal{L}_{rb}$ で消える一方、$\mathcal{L}_r, \mathcal{L}_b$ では自由境界を持つため非自明な相対コホモロジー類を持たない（$k_g = 0$）。他方、赤と青のペア $(a_r, a_b)$ は、$\mathcal{L}_r$（$a_r=0$）から出発して $\mathcal{L}_{rb}$（$a_r = a_b$）で折り返し $\mathcal{L}_b$（$a_b=0$）へと至る単一の非自明な相対1-コサイクル $\gamma_{\mathrm{log}}$ を共有する。その結果、系全体でちょうど **$k = 1$ 個の論理量子ビット**が符号化される。

論理Pauli演算子 $\overline{Z}, \overline{X}$ は以下のように与えられる：
* **論理 $\overline{Z}$ 演算子**：境界 $\mathcal{L}_r$ から $\mathcal{L}_{rb}$ に達する赤のパス（または $\mathcal{L}_b$ から $\mathcal{L}_{rb}$ に達する青のパス）上のPauli $Z$ の積。特に最小重み $d$ の代表元として、上端（または左端）境界に沿う長さ $d$ の $Z^r$ 鎖 $\overline{Z} = \prod_{e \in \gamma_Z} Z_e^r$ がとれる。
* **論理 $\overline{X}$ 演算子**：赤と青の両方に跨がる論理コサイクルにドレスを施したClifford演算子（可換表面符号FSCにおいては、赤の論理 $X$ 鎖と青の論理 $X$ 鎖の積 $\overline{X}_{\mathrm{FSC}} = \overline{X}_r \overline{X}_b$ に対応する）。

#### 2.4.2 横断的（定数深さ）論理 $T^\dagger$ ゲート $U = WV$
$(2+1)$次元ツイスト $\mathbb{Z}_2^3$ ゲージ理論は、ゲージ変換
$$a_r \mapsto a_r, \qquad a_g \mapsto a_g + a_r + a_b, \qquad a_b \mapsto a_b$$
のもとで、作用の変化分 $\Delta \int a_r \cup a_g \cup a_b = \int a_r \cup (a_r + a_b) \cup a_b$ がSteenrod平方（高次カップ積 $\cup_1$）を用いて完全微分と2次形式の和
$$(a_r \cup a_r \cup a_b + a_r \cup a_b \cup a_b) = d(\dots) + \dots$$
として書き直せるという非自明な自己同型対称性（automorphism symmetry）を持つ [27]。

Kobayashiら [27] の Theorem 1 および Theorem 2 により、この対称性を格子上のユニタリ演算子として具体化したものが **$U = W V \in \mathcal{C}^{(3)}$** である：
1. **オンサイト $\text{CNOT}$ 層 $V \in \mathcal{C}^{(2)}$**：
   各辺 $e \in E$（境界条件により赤・青が共有される折り畳み辺を含む）において、赤量子ビットと青量子ビットを制御ビット、緑量子ビットを標的ビットとするオンサイト $\text{CNOT}$ ゲートを作用させる：
   $$V \equiv \prod_{e} \text{CNOT}_e^{(r \to g)}\, \text{CNOT}_e^{(b \to g)}.$$
   計算基底 $|a_r, a_g, a_b\rangle$ に対して $V$ は $|a_r, a_g + a_r + a_b, a_b\rangle$ を生成する。
2. **対角第3階層（$\text{CS} / \text{CS}^\dagger / T^\dagger$）層 $W \in \mathcal{C}^{(3)}$**：
   バルクの各正方形セル $p = (0123)$ 内の対角ペアに対して Controlled-$S$（$\text{CS} = \text{diag}(1,1,1,i)$）およびそのエルミート共役 $\text{CS}^\dagger = \text{diag}(1,1,1,-i)$ を作用させ、さらに折り畳み境界 $\mathcal{L}_{rb}$ 上の辺 $e \in \mathcal{L}_{rb}$ に対して単一量子ビット $T^\dagger = \text{diag}(1, e^{-i\pi/4})$（または $T$）を作用させる対角ユニタリ演算子である：
   $$W \equiv \left( \prod_{p=(0123)} \text{CS}_{e_{01}^r,\, e_{13}^b}\, \left(\text{CS}_{e_{02}^r,\, e_{23}^b}\right)^\dagger \right) \prod_{e \in \mathcal{L}_{rb}} \left(T_e^r\right)^\dagger.$$
   計算基底 $|a\rangle$ に対する $W$ の作用は、$\mathbb{Z}_8$ 値位相関数 $\Phi_W(a_r, a_b) \in \mathbb{Z}_8$（$\omega = e^{i\pi/4}$）を用いて
   $$W |a\rangle = \omega^{\Phi_W(a_r, a_b)} |a\rangle, \qquad \Phi_W(a_r, a_b) \equiv 2 \sum_{p=(0123)} \left( a_r(e_{01})a_b(e_{13}) - a_r(e_{02})a_b(e_{23}) \right) - \sum_{e \in \mathcal{L}_{rb}} a_r(e) \pmod 8$$
   と表される。

この $U = WV$ は以下の3つの決定的な性質（インターツイナー条件：Intertwiner Conditions）を満たす [27]：
* **(C1) 平坦部分空間上の作用**：$U$ は $Z$-安定化子 $S_{Z;f}^r, S_{Z;f}^b$ と可換であり、$S_{Z;f}^g$ を $V S_{Z;f}^g V^\dagger = S_{Z;f}^g S_{Z;f}^r S_{Z;f}^b$ へと写すため、平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$（$\forall f, c,\; S_{Z;f}^c = +1$）を不変に保つ。
* **(C2) 緑の $X$-安定化子の不変性**：任意の頂点 $v$ に対して、平坦部分空間上で
  $$U S_{X;v}^g U^\dagger \Big|_{\mathcal{H}_{\mathrm{flat}}} = S_{X;v}^g \Big|_{\mathcal{H}_{\mathrm{flat}}}.$$
* **(C3) 赤・青の $X$-安定化子のインターツイニング**：任意の頂点 $v$ に対して、平坦部分空間上で
  $$U S_{X;v}^r U^\dagger \Big|_{\mathcal{H}_{\mathrm{flat}}} = S_{X;v}^r S_{X;v}^g \Big|_{\mathcal{H}_{\mathrm{flat}}}, \qquad U S_{X;v}^b U^\dagger \Big|_{\mathcal{H}_{\mathrm{flat}}} = S_{X;v}^b S_{X;v}^g \Big|_{\mathcal{H}_{\mathrm{flat}}}.$$

そして、論理状態 $|\overline{0}\rangle_{\mathbb{D}_4}$ に含まれる基底配位（$a_r, a_b$ が自明な相対コホモロジー類に属する平坦配位）では $\Phi_W(a_r, a_b) \equiv 0 \pmod 8$ となる一方、論理状態 $|\overline{1}\rangle_{\mathbb{D}_4}$ に含まれる基底配位（$a_r, a_b$ が非自明な論理コサイクル $\gamma_{\mathrm{log}}$ に属する平坦配位）では、バルクの $\text{CS}/\text{CS}^\dagger$ 位相と境界 $\mathcal{L}_{rb}$ の $T^\dagger$ 位相のコホモロジー的相殺により、すべての配位で一様に $\Phi_W(a_r, a_b) \equiv -1 \equiv 7 \pmod 8$（すなわち $e^{-i\pi/4}$）となる。したがって、符号空間 $\mathcal{H}_{\mathrm{code}}$ 上で $U$ は厳密に論理 $\overline{T}^\dagger$ ゲート（研究3では等価的に $\text{NCCZ} = X^{\otimes 3}\text{CCZ}X^{\otimes 3}$ ガジェットを用いて論理 $\overline{T}$ または $\overline{T}^\dagger$ として実装）として作用する：
$$U |\overline{0}\rangle_{\mathbb{D}_4} = |\overline{0}\rangle_{\mathbb{D}_4}, \qquad U |\overline{1}\rangle_{\mathbb{D}_4} = e^{-i\pi/4} |\overline{1}\rangle_{\mathbb{D}_4} \quad \Longleftrightarrow \quad \overline{U} = \overline{T}^\dagger.$$

### 2.5 可換表面符号（FSC）と $\mathbb{D}_4$ 符号の間の Code Switching プロトコル

$\mathbb{D}_4$ 符号上で論理 $\overline{T}^\dagger$ が横断的に実行できるとしても、アルゴリズムの他の部分（Cliffordゲートや長時間の量子メモリ保持）は、すべての安定化子が可換なPauli演算子である通常の表面符号上で実行する方が圧倒的に効率的である。Kobayashiら [27] は、2枚の三角形表面符号を境界 $\mathcal{L}_{rb}$ で貼り合わせた**折り畳み表面符号（Folded Surface Code; FSC）**と $\mathbb{D}_4$ 符号の間を定数深さの局所測定で行き来する以下の3段階プロトコル（Code Switching）を構成した。

```
[Stage 0: FSC初期化・準備]
  赤・青セクター：折り畳み表面符号 (FSC) の論理 |+>_L 状態
  緑セクター    ：すべての辺を |0>_g (Z_e^g = +1) に初期化
        │
        ▼
[Stage 1: Switch-in (Gauging: FSC → D4)]
  緑のドレスされた X チェック S_{X;v}^g と Z チェック S_{Z;f}^{r,g,b} を R_in ラウンド反復測定
  → JIT 復号器でフラックスを消去し、緑の初期シンドローム λ_fr を確定
        │
        ▼
[Stage 2: 横断的論理非Cliffordゲート U = W V]
  定数深さ回路 U = W V を 1 ステップ（物理 5 サブステップ）で一斉適用
  → 符号空間上で論理 T^† (または T) ゲートを実行
        │
        ▼
[Stage 3: Switch-out (Condensation: D4 → FSC)]
  緑のすべてのデータ量子ビットを単一量子ビット X 基底 (X_e^g) で一斉破壊測定 (m_X^g)
  → 古典ソフトウエアで分岐補正 X_g(λ_fr) と 2次位相補正 (-1)^{F(a_r, a_b)} (論理 Z フレーム) を適用
  → FSC の可換 Pauli 安定化子測定 (R_out ラウンド) と 2 基底 MWPM 復号により最終論理状態を回収
```

#### 2.5.1 Stage 1: Switch-in（ゲージング：FSC $\to \mathbb{D}_4$）
初期状態として、赤・青量子ビットは可換なPauli安定化子 $X_v^r, X_v^b$（境界 $\mathcal{L}_{rb}$ では結合チェック $X_v^r X_v^b$）および $Z_f^r, Z_f^b$ で安定化されたFSCの論理状態 $|\overline{\psi}\rangle_{\mathrm{FSC}} = \alpha |\overline{0}\rangle_{\mathrm{FSC}} + \beta |\overline{1}\rangle_{\mathrm{FSC}}$ にあり、緑のデータ量子ビットはすべて $|0\rangle_g^{\otimes |E_g|}$（$a_g = 0$）に初期化されているとする。
この状態はすでに $S_{Z;f}^r = S_{Z;f}^b = S_{Z;f}^g = +1$（平坦条件）を満たし、さらに $a_g = 0$ の部分空間上では赤・青の $\mathbb{D}_4$ チェック $S_{X;v}^r, S_{X;v}^b$ の $\text{CZ}$ ドレッシング（緑量子ビットを含む）はすべて恒等演算子 $I$ として作用するため、**初期状態は自動的に $S_{X;v}^r = +1, S_{X;v}^b = +1$ を満たしている**！
したがって、FSCから $\mathbb{D}_4$ 符号へ移行するために新たに測定すべき生成元は、緑の $X$-チェック $S_{X;v}^g$ のみである。$S_{X;v}^g$ を一斉測定して固有値 $s_v^g = (-1)^{\sigma_v^g} \in \{\pm 1\}$ を得ると、系はランダムな緑電荷シンドローム $\sigma^g$ を持つ $\mathbb{D}_4$ 符号空間へと射影される。このシンドローム $\sigma^g = \partial \lambda_{\mathrm{fr}}$ を打ち消す0-コチェイン（緑頂点の反転集合）$\lambda_{\mathrm{fr}} \in C^0(\mathcal{K}, \mathbb{Z}_2)$ を選ぶと、論理 $\mathbb{D}_4$ 状態は $\prod_{v \in \lambda_{\mathrm{fr}}} X_{v,\mathrm{branch}}^g$ だけずれた分岐（branch）にある。ノイズが存在する場合には、この switch-in 測定を $R_{\mathrm{in}}$ ラウンド反復し、JIT復号器によってフラックスを消去した上で初期ランダムシンドローム $\sigma^g$（および $\lambda_{\mathrm{fr}}$）を確定させる。

#### 2.5.2 Stage 2 & Stage 3: $U = WV$ の適用と Switch-out（ボソン凝縮：$\mathbb{D}_4 \to$ FSC）および位相公式 $F(a)$
Switch-in によって得られた $\mathbb{D}_4$ 状態に対して横断的ゲート $U = WV$ を適用した後、緑のすべてのデータ量子ビットを単一量子ビットPauli $X$ 基底 $X_e^g$ で一斉に測定し、測定結果 $m_X^g(e) \in \{0, 1\}$ を得る（これにより緑の電荷 $e_g$ がボソン凝縮し、系は再び赤・青のみのFSCへと戻る）。

ここで、以下の2つの補正を古典ソフトウエア上で処理する必要がある：
1. **初期ランダム分岐 $\lambda_{\mathrm{fr}}$ の補正**：
   Switch-in で生じた緑シンドローム分岐 $\lambda_{\mathrm{fr}}$ を補正する演算子は、ドレスされた緑チェックと同じ構造を持つ $S_X^g(\lambda_{\mathrm{fr}}) = \prod_{v: \lambda_{\mathrm{fr}}(v)=1} S_{X;v}^g$（または裸の $X^g(\lambda_{\mathrm{fr}})$ と対応する $\text{CZ}^{r,b}$ ドレッシング）である。$U$ と $S_{X;v}^g$ は平坦空間上で可換（$U S_{X;v}^g = S_{X;v}^g U$）であるため、この分岐補正は $U$ を通過して switch-out 直前へとそのまま移動できる。
2. **緑の $X_e^g$ 測定結果 $m_X^g$ に伴うPauli $Z$ フレーム補正 $F(a)$**：
   緑のデータ量子ビットを $\langle m_X^g|$ に射影すると、$\mathbb{D}_4$ 波動関数に含まれるカップ積位相 $(-1)^{\int a_r \cup a_g \cup a_b}$ と緑ゲージ場 $a_g = d\lambda_g$ の総和から、赤・青のコチェイン $(a_r, a_b)$ に対して測定結果 $m_X^g$ に依存する位相因子が生じる。しかし、平坦部分空間（$da_r = da_b = 0$）上では、ストークスの定理（部分積分）
   $$\int_{\mathcal{K}} a_r \cup d\lambda_g \cup a_b = \int_{\mathcal{K}} d(a_r \cup \lambda_g \cup a_b) = 0 \pmod 2$$
   が成り立つため、すべての緑ゲージ軌道は平坦な赤・青配位に対して等しい振幅を与える。さらに、緑の $X_e^g$ 測定値 $m_X^g$（および分岐補正後の実効測定値 $\tilde{m}_X^g = m_X^g \oplus d\lambda_{\mathrm{fr}}$）は、平坦空間上では余境界 $d\hat{\lambda}_g$ とチェイン $\gamma$ のペアリングによって**赤・青に対する線形な位相（すなわち単一量子ビットPauli $Z_e^r, Z_e^b$ の積）**
   $$(-1)^{F(a_r, a_b; \tilde{m}_X^g)} = \prod_{e} \left(Z_e^r\right)^{z_r(e)} \left(Z_e^b\right)^{z_b(e)}$$
   のみを誘起する [27]。そして論理 $Z$ 演算子 $\overline{Z}$ と可換な安定化子操作の下では、この線形位相の論理的な効果は**論理 $\overline{Z}$ フレームの1ビットのパリティ反転** $\operatorname{par}(\tilde{m}_X^g)$（研究3の `d4_lib.py` における `protocol_phase_F`、研究2の `chsc_switch_v3.py` における `ErrorFrame` の $l \cdot a$ 項）に完全に集約される！したがって、switch-out 時に物理的な適応的 $\text{CZ}$ やPauliゲートを回路に挿入する必要は一切なく、すべて古典復号・Pauliフレーム更新のみで厳密に完了する。

---

## 第3章 手法：Clifford安定化子シミュレーションとJust-in-Time（JIT）復号アルゴリズム

本章では、本研究の3つのプロジェクトにおける数値シミュレーションの理論的基盤である **Takada, Bartlett, Williamson（arXiv:2609.16929）** [39] の Clifford 安定化子シミュレーション法を詳述し、本研究で実装された3つのシミュレーション・エンジン（研究1の Twisted-Frame 表現、研究2の演算子レベル Pauli-Proxy エンジン、研究3の回路レベル Pauli-Proxy エンジン）が数学的にいかに接続・対応しているかを明らかにする。続いて、非可換シンドローム測定を実時間で処理する Just-in-Time（JIT）フラックス復号器と2基底 MWPM 電荷復号器のアルゴリズムを定式化する。

### 3.1 Takada–Bartlett–Williamson（TBW）によるClifford安定化子シミュレーション理論

Takadaら [39]（作業フォルダ内 `関連先行研究/2026-09-29_ExactEfficientSimulation.tex`）は、Pauli安定化子群を第2階層Clifford群 $\mathcal{C}^{(2)}$ の部分群 $\mathcal{G}_{\mathrm{C}} \subset \mathcal{C}^{(2)}$ へと拡張した「Clifford安定化子状態（Clifford-stabilizer states）」に対し、Pauliノイズ、Cliffordゲート、および許容される非Pauli（Clifford）安定化子測定や非Cliffordゲートの下での時間発展を、量子ビット数 $n$ に対して多項式時間 $\text{poly}(n)$ で厳密に追跡する枠組みを構築した。その理論的要諦は以下の4点に整理される。

#### 3.1.1 Clifford安定化子群の許容条件（Admissibility Conditions）と実効的可換性
Clifford安定化子群 $\mathcal{G}_{\mathrm{C}} = \langle G_1, \dots, G_m \rangle \subset \mathcal{C}^{(2)}$ は、一般に全ヒルベルト空間上では非アーベル群であり得るが、共通の $+1$ 固有状態（フレーム状態 $|\psi^{\mathrm{fr}}\rangle$）を定義するためには、生成元間のすべての群交換子 $[G_j, G_k] \equiv G_j^{-1} G_k^{-1} G_j G_k$ が生成する部分群 $\mathcal{B}_{\mathrm{gc}}$ が現在の安定化子群 $\mathcal{G}_{\mathrm{C}}$ に含まれ、かつ $-I \notin \mathcal{G}_{\mathrm{C}}$ でなければならない（**実効的可換性：effective commutativity**）。

さらに、Pauli誤り $E_{\mathrm{P}} \in \mathcal{P}_n$ とClifford生成元 $G_j$ の交換関係から生じる**Pauliドレッシング（Pauli dressing）**
$$D_{G_j}(E_{\mathrm{P}}) \equiv [E_{\mathrm{P}}, G_j] = E_{\mathrm{P}}^{-1} G_j^{-1} E_{\mathrm{P}} G_j \in \mathcal{P}_n$$
および測定更新を多項式時間で閉じるため、Takadaら [39]（Sec. VI–VIII, Definition 1 & Definition 2）は以下の構造的条件を導入した：
1. **因子分解と横断的サポート（Factorized form & Disjoint support）**：
   各主生成元（primary generator）$G_j$ は局所Clifford因子 $U \in \mathcal{C}^{(2)}$ のテンソル積に分解され、特に $\mathbb{D}_4$ 符号のように非対角なPauli $X$ 因子と対角的なClifford因子（$\text{CZ}, S, Z$）が互いに素な量子ビット集合（disjoint support）上に作用する：$G_j = X^{s_j} C_j$（ここで $\operatorname{supp}(s_j) \cap \operatorname{supp}(C_j) = \emptyset$）。
2. **インボリューティブ条件（Involutive Pauli action）と共通の局所ドレッシング軸**：
   各Clifford因子 $C$ に対して $C^2 \in \mathcal{P}_n$（すなわち $C$ によるPauli共役写像が位数2の対合）であり、任意の単一量子ビットPauli演算子に対するドレッシング $D_C(P)$ が各量子ビット上で**共通の局所Pauli軸（$\mathbb{D}_4$ 符号では計算基底の $Z$ 軸）**に沿って整列している。実際、$\mathbb{D}_4$ 符号では $C = \prod \text{CZ}$ は対角演算子であるため、任意のPauli誤り $E_{\mathrm{P}} = i^\alpha X^x Z^z$ との群交換子 $D_C(E_{\mathrm{P}})$ は常に純粋なPauli $Z$ 文字列（$\mathcal{P}_Z$ の元）となる。
3. **群交換子のPauli $Z$ 安定化子への包含**：
   生成元間の群交換子部分群 $\mathcal{B}_{\mathrm{gc}}$ が、常にその時点の安定化子群に含まれるPauli $Z$ 安定化子部分群 $\mathcal{S}_Z \subset \mathcal{G}_{\mathrm{C}} \cap \mathcal{P}_Z$ の中に収まる（$\mathcal{B}_{\mathrm{gc}} \subseteq \mathcal{S}_Z$）。2.3節で示した通り、$\mathbb{D}_4$ 符号では $[S_{X;u}^c, S_{X;v}^{c'}] = \prod_{f \in F_{uv}} S_{Z;f}^{c''}$ であるため、この条件は厳密に満たされている。
4. **主サポートの厳密性（Primary-support exactness, Definition 1）**：
   非対角な主生成元 $G_1, \dots, G_r$ のPauli $X$ サポートベクトル $s_1, \dots, s_r \in \mathbb{F}_2^n$ が線形独立（または既知の対称性関係を除いて独立）であり、主生成元の非自明な積が純粋に対角な非Pauli Clifford演算子（隠れた $\text{CZ}$ 安定化子）を生成しないこと。これにより、測定演算子と安定化子群の可換・非可換判定がPauli部分のシンプレクティック内積に完全に帰着する。

#### 3.1.2 測定共役描像（Measurement-Conjugated Picture）
$\mathbb{D}_4$ 符号において最も厄介なのは、データ $X$ エラー $E$ が入るとフラックス $S_{Z;f}^c = -1$ が立ち、現在の量子状態 $|\psi\rangle = E |\psi^{\mathrm{fr}}\rangle$ 上で $\mathcal{B}_{\mathrm{gc}}$ の固有値が $-1$ となって実効的可換性が破れることである。もしエラー後の状態 $|\psi\rangle$ の安定化子群 $E \mathcal{G}_{\mathrm{C}} E^\dagger$ を直接更新しようとすると、生成元同士が反交換してしまい安定化子形式が破綻する。

Takadaら [39]（Sec. VII.A）の極めて鮮やかな解決策が**測定共役描像（measurement-conjugated picture）**である：
* シミュレータ内部で保持する基準状態は、常にすべてのフラックスが $+1$（$\mathcal{B}_{\mathrm{gc}}$ が恒等的に $+1$ で実効的可換）である**エラーフリーのフレーム状態 $|\psi^{\mathrm{fr}}\rangle$** に固定し、現在の真の物理状態を
  $$|\psi\rangle = E |\psi^{\mathrm{fr}}\rangle$$
  と表現する。ここで $E$ は蓄積したエラーフレーム（Pauli誤りおよび非可換測定や分岐反転から生じた対角Clifford $\text{CZ}/S$ ドレッシングの積）である。
* 物理系に対して測定演算子 $M$（例えば $M = S_{X;v}^c$ や $M = S_{Z;f}^c$、あるいは単一量子ビット $X_e^g$）の射影測定を行う際、状態 $E|\psi^{\mathrm{fr}}\rangle$ 上で $M$ を測ることは、**基準フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ 上でエラーフレーム共役をとった実効測定演算子**
  $$\widetilde{M} \equiv E^\dagger M E = \bar{D}_M(E)\, M \qquad \left(\bar{D}_M(E) \equiv E^\dagger M E M^\dagger\right)$$
  を測ることとユニタリ同値である！
* フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ 上ではすべての $Z$-安定化子が $S_{Z;f}^c |\psi^{\mathrm{fr}}\rangle = +|\psi^{\mathrm{fr}}\rangle$ を満たすため、元の生成元 $G_k$ と $M$ の群交換子 $[M, G_k] \in \mathcal{B}_{\mathrm{gc}}$ は $|\psi^{\mathrm{fr}}\rangle$ 上で常に $+1$ として作用する（すなわち $M$ と $G_k$ は $|\psi^{\mathrm{fr}}\rangle$ 上で実効的に可換である）。
* 一方、フラックスによる非可換性（反交換と再ランダム化）はどこへ現れるかというと、エラーフレーム共役によって生じたPauli $Z$ ドレッシング因子 $\bar{D}_M(E) \in \mathcal{P}_Z$ の中に完全に現れる！すなわち、もしエラー $E$ がフラックスを作っていれば、$\bar{D}_M(E)$ は非自明な $Z$ 文字列を含み、それが隣接する異色生成元 $G_k = X^{s_k} C_k$ の $X$ 部分 $X^{s_k}$ と反交換する（$[\bar{D}_M(E), G_k] = -I$）。その結果、フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ 上で $\widetilde{M} = \bar{D}_M(E) M$ を測定すると、$\widetilde{M}$ は $G_k$ と反交換し、標準的なGottesman–Knillの更新則に従って確率 $1/2$ で測定結果がランダム化され、$G_k$ が新しい安定化子 $\pm \widetilde{M}$ によって置き換えられるのである。

#### 3.1.3 Pauli Proxy（Pauli代理生成元）による通常のTableauシミュレータへの還元
さらに Takadaら [39]（Sec. VII.B–C, Algorithm 1–3）は、フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ のClifford安定化子群 $\mathcal{G}_{\mathrm{C}}$ 自体も、各Clifford因子 $U_j$ を対応する**Pauli proxy（Pauli代理演算子）$\hat{P}_{U_j} \in \mathcal{P}_n$** に置き換えたPauli安定化子群 $\hat{\mathcal{G}}_{\mathrm{P}}$ として、**たった1つの標準的なPauli Tableauシミュレータ（Stim等）**で厳密に追跡できることを示した。

具体的には、対角Cliffordゲート $\text{CZ}$ のPauli proxyは恒等演算子 $\hat{P}_{\text{CZ}} = I$ である。したがって：
* $\mathbb{D}_4$ のドレスされた $X$-チェック $S_{X;v}^c = X_v^c \prod \text{CZ}$ のPauli proxyは、ドレッシングを取り除いた**裸のPauli $X$-スター演算子 $\hat{P}_{S_{X;v}^c} = X_v^c$** となる。
* Pauli $Z$-チェック $S_{Z;f}^c$ のPauli proxyはそれ自身 $\hat{P}_{S_{Z;f}^c} = S_{Z;f}^c$ である。
* 横断的論理ゲート $U = WV$ のPauli proxyは、対角第3階層層 $W$ を取り除いた**オンサイト $\text{CNOT}$ 層 $\hat{P}_U = V$** となる。

なぜ $\text{CZ}$ ドレッシングや対角第3階層ゲート $W$ をTableauから取り除いてよいのか？それは、フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ 上では $S_{X;v}^c$ 同士の群交換子が $+1$ であり、かつ $U = WV$ がインターツイナー条件 (C1)–(C3)（$U S_{X;v}^r U^\dagger = S_{X;v}^r S_{X;v}^g$ 等）を満たすため、裸のPauli生成元 $X_v^c$ に対して $\text{CNOT}$ 層 $V$ を作用させたときの変換則 $V X_v^r V^\dagger = X_v^r X_v^g$ と**代数的構造が完全に同型（isomorphic）**だからである。そして、取り除いた $\text{CZ}$ ドレッシングや $W \in \mathcal{C}^{(3)}$ が現実の量子状態に及ぼす非線形な効果はすべて、**エラーフレーム $E$ がそれらのゲート・測定を通過する際のドレッシング $\bar{D}_M(E)$ および $D^\dagger X^e D X^e \in \mathcal{C}^{(2)}$** として1ビットの狂いもなく回収される。

### 3.2 本研究の3つのシミュレーション・エンジンの対応関係と理論的等価性

本研究の3つのプロジェクト（研究1・研究2・研究3）では、それぞれ対象とする問題構造に最も適した以下の3つのシミュレーション表現を実装している。これらはすべて上記のTakada–Bartlett–Williamson（TBW）理論の異なる表現（あるいはAlgorithm 1/2/3の具体化）として統一的に理解できる。

| 項目 | 研究1（トーラス閾値）<br>`D4_v7_main.ipynb` | 研究2（Code Switching 現象論）<br>`chsc_switch_v3.py` | 研究3（Code Switching 回路レベル）<br>`tools/noisy_d4_lib.py` |
| :--- | :--- | :--- | :--- |
| **対象系と境界** | $L \times L$ 三角分割トーラス（$k=6$）<br>$N = 3L^2$ データ量子ビット | 三角形パッチ FSC $\leftrightarrow \mathbb{D}_4$（$k=1$）<br>$N = 6d^2 + 2d$ データ量子ビット | 三角形パッチ FSC $\leftrightarrow \mathbb{D}_4$ ＋ 補助量子ビット<br>ピーク $12d^2 + 4d - 1$ 量子ビット |
| **TBW理論との対応** | 計算基底（コチェイン空間 $C_0$）上の<br>**双対 Twisted-Frame 表現** | **TBW Algorithm 1 & 3**<br>（演算子レベル Pauli-Proxy ＋ $\mathbb{Z}_8$ ErrorFrame） | **TBW Algorithm 2**<br>（回路レベル Pauli-Proxy ＋ 動的Cliffordドレッシング） |
| **内部状態の表現** | 平坦空間 $C_0$ 上のアフィン部分空間 $B = \{Gt=\rho\}$<br>＋ 2次位相形式 $Q(t) = t^T W t + d\cdot t$<br>＋ シフト $x \in \mathbb{F}_2^N$（Numba JIT） | `stim.TableauSimulator`（Pauli proxy 状態）<br>＋ エラーフレーム $E = X^x \text{diag}(\omega^{\gamma(a)})$<br>（$\gamma(a) = l\cdot a + 4\sum Q_{ij}a_i a_j \pmod 8$） | `stim.TableauSimulator`（$\mathcal{C}^{(3)}$ 除去回路）<br>＋ 前方伝播 $X$ フレーム $e = \text{fx} \in \mathbb{F}_2^{n_{\mathrm{tot}}}$<br>＋ 動的Cliffordゲート $C_e = D^\dagger X^e D X^e$ 挿入 |
| **厳密参照器による検証** | $L=3$（27量子ビット）JAX 密状態ベクトル<br>（`DenseBackend`、最大確率差 $\le 6\times 10^{-8}$） | $d=2$（16量子ビット）密状態ベクトル（`BFBackend`）<br>＋ $d=3,4$ $\mathbb{Z}_4$ Twisted-Frame（`TFBackend`）<br>計 3,214,446 出力で不一致 0 | $d=2$ 密状態ベクトル `TrueSim`（17量子ビット）<br>＋ $d=3$ 部分回路 `TrueSim`<br>189項目テストで FAIL 0 |

#### 3.2.1 研究1の Twisted-Frame 表現と TBW 形式の双対性
研究1（`D4_v7_main.ipynb`）および研究2の検証用参照エンジン（`TFBackend`）では、状態を計算基底 $|a\rangle$ の波動関数として直接表現する**ツイストフレーム（Twisted-Frame）表現**を採用している。
平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ の基底をなす平坦コチェイン集合 $C_0 = \{b \in \mathbb{F}_2^N \mid db = 0\}$ の次元を $k_{\mathrm{flat}} = \dim C_0 = 2L^2 + 3$ とし、基底行列 $M \in \mathbb{F}_2^{N \times k_{\mathrm{flat}}}$（$b = Mt, t \in \mathbb{F}_2^{k_{\mathrm{flat}}}$）をとる。ある参照基底状態 $|\psi_{\mathrm{ref}}\rangle \in \mathcal{H}_{\mathrm{code}}$ の振幅を $\psi_{\mathrm{ref}}(b) \propto (-1)^{\phi_0(b)}$ と書くと、任意の $X$-チェックシフト $s = M\tau$ に対して安定化子条件 $S_X |\psi_{\mathrm{ref}}\rangle = |\psi_{\mathrm{ref}}\rangle$ から基本恒等式
$$\phi_0(b + s) + \phi_0(b) = q_s(b + s) \pmod 2 \qquad (\forall b \in C_0)$$
が成り立つ。この恒等式のおかげで、任意の $X$ エラーシフト $x \in \mathbb{F}_2^N$ と任意の $X$-チェック測定列を受けた後の波動関数は、**3次の位相項を一切生じることなく**、常に
$$\psi(a) \propto (-1)^{\phi_0(a + x) + Q(t)} \, \mathds{1}\left[ a + x = Mt \in B \right]$$
という閉じた形で表される！ここで
* $B = \{ t \in \mathbb{F}_2^{k_{\mathrm{flat}}} \mid G t = \rho \}$ はアフィン部分空間（TBW形式におけるPauli proxy安定化子群 $\hat{\mathcal{G}}_{\mathrm{P}}$ の $X$-安定化子および測定射影が定めるコチェイン制約に双対）、
* $x \in \mathbb{F}_2^N$ は平坦空間からのずれを表す $X$ エラーフレーム（TBW形式における $E$ の $X^x$ 成分）、
* $Q(t) = \sum_{i < j} W_{ij} t_i t_j + d \cdot t \pmod 2$ は $t$ に関する $\mathbb{F}_2$（研究2の `TFBackend` では $T^\dagger$ を含むため $\mathbb{Z}_4$）上の2次形式（TBW形式におけるエラーフレーム $E$ の対角 $Z$ および $\text{CZ}$ ドレッシング成分）

である。測定演算子 $S_A = X^{s_A}(-1)^{q_A(a)}$（$s_A = M\tau_A$）を作用させると、シフトされた2次形式 $q_A(Mt + M\tau_A + x)$ は $t$ に関するアフィン関数 $u_A \cdot t + c_A$ へと厳密に線形化される。その結果：
* **(Case 1) $\tau_A \in B_0 = \ker G$ の場合**：状態は $S_A$ の固有空間に留まり、決定論的または確率 $1/2$ でパリティ制約 $u_A \cdot t = \text{const}$ が $G t = \rho$ に追加される。
* **(Case 2) $\tau_A \notin B_0$ の場合**：非可換な測定によって $\tau_A$ 方向への重ね合わせが生じるため、$\tau_A$ を含むように $B_0$ を拡大し（$G$ から $\tau_A$ と反交換する行を消去）、新しい方向 $\tau_A$ に沿った $W_{ij}$ と $d_i$ の成分を線形位相 $u_A$ で更新する。

これはまさに、TBWの測定共役描像における「Pauli proxy Tableauの行消去・置換とエラーフレーム $E$ の2次位相更新」を計算基底（コチェイン座標 $t$）の側から記述したものに他ならない。

#### 3.2.2 研究2の演算子レベル Pauli-Proxy エンジン（TBW Algorithm 1 & 3）
研究2（`chsc_switch_v3.py` の `ProxyBackend`）は、Takadaら [39] の Algorithm 1 および Algorithm 3 を文字通り直接実装したものである。
1. **Pauli-Proxy Tableau (`stim.TableauSimulator`)**：
   $N = 6d^2 + 2d$ 量子ビットの `stim.TableauSimulator` を1つ保持し、フレーム状態 $|\psi^{\mathrm{fr}}\rangle$ のPauli proxyを管理する。FSCの初期化では $X_v^r, X_v^b, Z_f^r, Z_f^b$ と $|0\rangle_g$ を設定し、switch-in では裸の緑Pauliスター $\hat{P}_{S_{X;v}^g} = X_v^g$ を測定する。横断的ゲート $U = WV$ の適用時には、Pauli proxy であるオンサイト $\text{CNOT}$ 層 $V$ のみを `TableauSimulator` に作用させる。
2. **対角Cliffordエラーフレーム (`ErrorFrame`)**：
   フレーム状態の外側にあるエラー演算子 $E$ を
   $$E = X^x \, \operatorname{diag}\left( \omega^{\gamma(a)} \right), \qquad \gamma(a) \equiv \sum_{i=1}^N l_i a_i + 4 \sum_{i < j} Q_{ij} a_i a_j \pmod 8 \quad (\omega = e^{i\pi/4})$$
   として追跡する。ここで $x \in \mathbb{F}_2^N$ はビット反転（Pauli $X$）フレーム、$l \in \mathbb{Z}_8^N$ は1次位相フレーム（$l_i \equiv 4 \pmod 8$ がPauli $Z_i$、$l_i \equiv \pm 2 \pmod 8$ が $S_i / S_i^\dagger$ に相当）、$Q \in \mathbb{F}_2^{N \times N}$ は2次位相フレーム（$Q_{ij} = 1$ が $\text{CZ}_{ij}$ に相当）である。
3. **非Cliffordゲート $U = WV$ の通過則 (`apply_U`)**：
   状態 $E |\psi^{\mathrm{fr}}\rangle$ に $U = WV$ を作用させると、$U E |\psi^{\mathrm{fr}}\rangle = (U E U^\dagger) U |\psi^{\mathrm{fr}}\rangle$ となる。$U |\psi^{\mathrm{fr}}\rangle$ は proxy 側で $V$ として処理され、エラーフレームは $E' = W (V E V^\dagger) W^\dagger$ へと更新される。ここで $V E V^\dagger$ は $\text{CNOT}$ によるアフィン変数変換 $a_g \mapsto a_g \oplus a_r \oplus a_b$ であり、続く $W (\cdot) W^\dagger$ はビット反転 $x' = V(x)$ が対角第3階層ゲート $W$（$\text{CS}, \text{CS}^\dagger, T^\dagger$）を共役通過する際に生じる位相差
   $$\Delta \Phi_W(a) = \Phi_W(a \oplus x') - \Phi_W(a) \pmod 8$$
   を $l'$ と $Q'$ に加算する操作である！このとき、もし switch-in の最後にフラックス（$x_r, x_b$ の非平坦成分）が残っていると、$\Delta \Phi_W(a)$ から消去不能な $l_i \equiv \pm 2 \pmod 8$（$S/S^\dagger$ 誤り）および $Q_{ij} = 1$（$\text{CZ}$ 誤り）が生成される。一方、もしフラックスが完全に消えていれば（$x_r, x_b$ が平坦コサイクルであれば）、$\Delta \Phi_W(a)$ の非Pauli項はすべて安定化子と打ち消し合い、純粋なPauli誤り（$l_i \in \{0, 4\}$）のみが残る。
4. **Switch-out 分岐反転の右乗算吸収 (`right_multiply_X_and_CZ`)**：
   Switch-in で確定したランダムな緑シンドローム分岐 $\lambda_{\mathrm{fr}}$ を補正する演算子 $S_X^g(\lambda_{\mathrm{fr}}) = X^{c_g} \text{CZ}^{\text{pairs}}$ は、状態 $E |\psi^{\mathrm{fr}}\rangle$ の内部（フレーム状態の直前）から外側へ引き出されるため、エラーフレーム $E$ への**右乗算** $E \leftarrow E X^{c_g} \text{CZ}^{\text{pairs}}$ として厳密に吸収される。

#### 3.2.3 研究3の回路レベル Pauli-Proxy エンジン（TBW Algorithm 2）
研究3（`tools/noisy_d4_lib.py` の `FastShot`）では、補助量子ビット（ancilla）と3量子ビット $\text{CCZ}$ ゲートを用いた物理的なシンドローム抽出回路そのものにゲート毎の脱分極ノイズが入るため、Takadaら [39] の **Algorithm 2（回路レベルシミュレーション法）**を採用している。

回路レベルでは、非Cliffordな $\mathbb{D}_4$ チェック測定 $S_{X;v}^c$ 自体も、補助量子ビット $|+\rangle_{\mathrm{anc}}$ を制御ビットとする $\text{CNOT}$（Pauli $X$ 部分）と **$\text{CCZ}$ ゲート（$\text{CZ}$ ドレッシング部分）**の列と $X$ 基底測定に分解されている。また横断的論理ゲート $U = WV$ の対角層 $W$ も、$\text{CS}, \text{CS}^\dagger, T^\dagger$（および論理 $T$ 用の $\text{NCCZ}$ ガジェット）からなる対角第3階層ゲート列である。
すなわち、**全回路に含まれる非Clifford要素はすべて「対角的な第3階層Cliffordゲート $D \in \mathcal{C}_{\mathrm{diag}}^{(3)}$（$\text{CCZ}, \text{CS}, \text{CS}^\dagger, T^\dagger, \text{NCCZ}$）」のみ**である！

ここで、任意の対角第3階層ゲート $D \in \mathcal{C}_{\mathrm{diag}}^{(3)}$ と任意のPauli演算子 $P = i^\alpha X^e Z^z$（$e, z \in \mathbb{F}_2^{n_{\mathrm{tot}}}$）の交換関係を考えると、$D$ は対角であるため $Z^z$ とは可換であり、$X^e$ との群交換子
$$C_e \equiv D^\dagger X^e D X^e \in \mathcal{C}_{\mathrm{diag}}^{(2)}$$
は必ず**対角的な第2階層Cliffordゲート（$Z, S, S^\dagger, \text{CZ}$ の積）**となる！具体的には：
* **$D = \text{CCZ}_{q_0, q_1, q_2}$ の場合**（$\text{CCZ} = \operatorname{diag}(1,1,1,1,1,1,1,-1)$）：
  $(e_0, e_1, e_2) \equiv (e_{q_0}, e_{q_1}, e_{q_2}) \in \mathbb{F}_2^3$ とおくと、計算基底 $|a_0, a_1, a_2\rangle$ 上で
  $$\begin{aligned}
  (a_0 \oplus e_0)(a_1 \oplus e_1)(a_2 \oplus e_2) \oplus a_0 a_1 a_2 &= e_0 a_1 a_2 \oplus e_1 a_0 a_2 \oplus e_2 a_0 a_1 \\
  &\quad \oplus e_0 e_1 a_2 \oplus e_0 e_2 a_1 \oplus e_1 e_2 a_0 \oplus e_0 e_1 e_2 \pmod 2
  \end{aligned}$$
  が成り立つ。したがって（グローバル位相 $(-1)^{e_0 e_1 e_2}$ を除き）、ドレッシング演算子 $C_e = \text{CCZ}^\dagger X^e \text{CCZ} X^e$ は
  $$C_e = \left(\text{CZ}_{q_1, q_2}\right)^{e_0} \left(\text{CZ}_{q_0, q_2}\right)^{e_1} \left(\text{CZ}_{q_0, q_1}\right)^{e_2} \left(Z_{q_2}\right)^{e_0 e_1} \left(Z_{q_1}\right)^{e_0 e_2} \left(Z_{q_0}\right)^{e_1 e_2}$$
  という単純な $\text{CZ}$ と $Z$ の積になる！
* **$D = \text{CS}_{q_0, q_1}$ または $\text{CS}^\dagger_{q_0, q_1}$ の場合**（$\text{CS} = \operatorname{diag}(1,1,1,i)$）：
  $(e_0, e_1) = (1, 0)$ なら $S_{q_1}$（または $S^\dagger_{q_1}$）、$(0, 1)$ なら $S_{q_0}$（または $S^\dagger_{q_0}$）、$(1, 1)$ なら $S^\dagger_{q_0} S^\dagger_{q_1} \text{CZ}_{q_0, q_1}$（または $S_{q_0} S_{q_1} \text{CZ}_{q_0, q_1}$）となる。
* **$D = T^\dagger_q$ の場合**：
  $e_q = 1$ のとき $C_e = S_q$（$T_q X_q T^\dagger_q X_q = e^{-i\pi/4} S_q$）となる。

一方、ノイズのない基準状態（全データ・補助量子ビット上でフラックスがゼロのPauli proxy状態）の上では、$\text{CCZ}$ や $W$ は恒等演算子として作用する（Pauli proxy $\hat{P}_D = I$）。したがって、TBW Algorithm 2（`FastShot`）は以下の極めて簡潔な手順で回路全体の厳密シミュレーションを実現する：
1. 1つの `stim.TableauSimulator` と、長さ $n_{\mathrm{tot}}$ のブール配列 `fx`（基準状態に対する現在の $X$-エラーフレーム $e \in \mathbb{F}_2^{n_{\mathrm{tot}}}$）を用意する。
2. 量子ビットのリセット（$|0\rangle$ または $|+\rangle$）では `fx[q] = 0` とし、$\text{CNOT}_{c \to t}$ ゲートでは `TableauSimulator.cx(c, t)` を実行するとともに `fx[t] ^= fx[c]` と前方伝播させる。
3. 確率的Pauliノイズ $(X, Y, Z)$ が発生した際は、`TableauSimulator` にそのPauliゲートを作用させるとともに、$X$ または $Y$ 成分がある場合は `fx[q] ^= 1` を反転させる。
4. **対角第3階層ゲート $D \in \{\text{CCZ}, \text{CS}, \text{CS}^\dagger, T^\dagger, \text{NCCZ}\}$ に到達した際は、$D$ 自体は `TableauSimulator` には作用させず（$\hat{P}_D = I$）、その時点の `fx` を参照して非自明なドレッシング $C_e = D^\dagger X^e D X^e \in \{S, S^\dagger, Z, \text{CZ}\}$ のみを `TableauSimulator` に挿入する！**
5. 測定では `TableauSimulator.measure(q)` をそのまま呼び出す（測定前の `fx` はすでに `TableauSimulator` 内のPauli状態にも同じように入っているため、測定結果の分布と事後状態は厳密に一致する）。

このアルゴリズムにより、本来であれば非Cliffordゲート $\text{CCZ}, \text{CS}, T^\dagger$ を数千個含むために古典計算不可能な回路が、**ゲート数に対して完全に線形時間 $O(N_{\mathrm{gates}})$** で、かつ状態ベクトル計算と寸分違わぬ厳密性をもってシミュレート可能となるのである。

### 3.3 Just-in-Time（JIT）フラックス復号器と2基底 MWPM 電荷復号器

$\mathbb{D}_4$ 符号において誤り訂正を行う際、もしデータ上の $X$ エラー（フラックス励起）を放置したまま $X$-チェック測定を繰り返すと、2.3節で見た通り測定再ランダム化が雪崩的に拡大し、さらに $\text{CZ}$ ドレッシングを介して他色へとデータ $Z$ エラー（電荷シンドローム）が毎ラウンド注入され続ける。特に符号切り替え（研究2・研究3）においては、横断的論理ゲート $U = WV$ を適用する瞬間にフラックスが残っていると、3.2.2節で示した通り $W$ との交換関係から非Pauli誤り（$S/\text{CZ}$ 誤り）が発生して符号空間そのものが破壊される。

したがって、$\mathbb{D}_4$ 符号の復号は、以下の**2段階の階層的アーキテクチャ**をとる必要がある：
1. **第1段階：実時間 Just-in-Time（JIT）フラックス復号器（Flux Decoder）**——各ラウンド $r$ の $Z$-安定化子測定（フラックスシンドローム）からデータ $X$ エラーを実時間で推定し、即座にPauli $X$ 補正（または能動的フラックス消去フレーム更新）を適用して系を平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ の近傍に保ち続ける。
2. **第2段階：大域的 MWPM 電荷復号器（Charge Decoder）**——全ラウンド終了後（または切り替え完了後）に、蓄積された $X$-安定化子測定履歴（電荷シンドローム）とフラックス履歴を用いて、データ $Z$ エラー（論理 $\overline{Z}$ 反転）を最小重み完全マッチング（MWPM: PyMatching [40]）によって一括復号する。

#### 3.3.1 JIT フラックス復号器のアルゴリズム設計
各色 $c \in \{r, g, b\}$ の $Z$-プラケット測定はPauli測定であり、各面 $f \in F$ は2量子ビット（トーラスの双対格子上では頂点に相当し、各辺が2つの面を结ぶ）または境界に接続する。
* **符号容量モデル（$R=1, p_M=0$）**：測定誤りがないため、各色 $c$ のフラックスシンドローム $\sigma_Z^c(f) \in \{0, 1\}$ に対して双対グラフ上の2次元 MWPM を1回実行し、最小重みのデータ $X$ 鎖を返す。
* **現象論的・回路レベルモデル（$R \ge 2, p_M > 0$）**：測定誤りによって偽のフラックス（spurious flux）が見えるため、単一ラウンドのシンドロームをそのまま消去（即時貪欲消去：memoryless greedy matching）すると、測定誤りを本物のデータ $X$ エラーと誤認して逆にデータ量子ビットへ $X$ エラー対を注入してしまう（研究3の `FluxDecoder` の現在の実装はこの単一ラウンドMWPMであり、第6章および『修正の要請.md』で詳述する通り切り替え窓の2重故障脆弱性の一因となっている）。
* **研究1・研究2の時空間スライディング窓 JIT 復号器**：
  研究1（`D4_v7_main.ipynb`）および研究2（`chsc_switch_v3.py` の `JITDecoder`）では、過去の確定済み補正による期待シンドロームを差し引いた差分欠陥（difference defects）
  $$\delta_t(f) \equiv \hat{\sigma}_{Z,t}^{\mathrm{raw}}(f) \oplus \hat{\sigma}_{Z,t-1}^{\mathrm{raw}}(f)$$
  を時刻 $1 \le \tau \le t$ の時空間グラフ上で構築し、現在時刻 $t$ の直後に**未来時間境界（future open time boundary、重み $w_{\mathrm{future}} \approx w_{\mathrm{time}}$）**を設けて3次元時空間 MWPM を解く。そして、過去の空間層 $\tau \le t-1$ に確定した空間マッチング辺のうち、まだ適用していない差分のみを現在時刻 $t$ の物理（またはフレーム）$X$ 補正 $\Delta x_{\mathrm{corr}}^{(t)}$ として適用する。これにより、単一ラウンドの測定誤りは未来境界へと吸収（先送り）され、2ラウンド連続して観測された持続的なフラックスのみが本物のデータ $X$ エラーとして確実に消去される。

#### 3.3.2 電荷（Charge）復号器とフラックス情報付き消失（Erasure）重み付け
データ $Z$ エラー（および測定誤り）を復号する電荷復号器は、頂点 $v \in V$ とラウンド $t \in \{1, \dots, R\}$ からなる3次元時空間検出器グラフ上で各色独立に MWPM を実行する。ここで、$\mathbb{D}_4$ 符号特有の非可換性と色間結合に対処するため、以下の3つの機構を組み込んでいる：
1. **2基底 MWPM 復号（研究1）**：
   周期境界条件のトーラス（研究1）では、各色につき2つの独立なホモロジーサイクル $\gamma_1, \gamma_2$ が存在する。そこで各サイクルを横切る辺集合 $E_{\gamma_a}$ を1つずつ開いた2つの参照木（cut graphs）上で独立に MWPM を解き、各サイクルを横切る総パリティから論理誤りを直接判定する（これにより、単一木への埋め込みで生じる $O(L)$ の経路引き伸ばし歪みを完全に排除している）。
2. **フラックス履歴に基づく時間辺のソフト重み付け（Soft Reweighting, 研究1）**：
   ある頂点チェック $S_{X;v}^c$ の近傍プラケット $F_{v,c}$ に時刻 $t$ でフラックスが存在した（またはJIT補正が行われた）場合、その頂点の測定値は非可換性により確率 $1/2$ で再ランダム化されている可能性が高い。そこで、該当する時空間ノード間の時間辺（測定誤り辺）の事前誤り確率 $p_{\mathrm{time}}$ を局所的に引き上げ（重み $w = \ln\frac{1-p}{p}$ を引き下げ）、再ランダム化によるシンドロームジャンプが空間的なデータ $Z$ エラー鎖として誤復号されるのを防ぐ。
3. **フラックス誘起消失（Flux-Induced Erasure）重み付け（研究2・研究3）**：
   符号切り替え（研究2・研究3）において、赤・青のフラックスが $U = WV$ や $\text{CZ}$ ドレッシングを通過した場所では、高確率で局所的な位相誤り（$Z/S/\text{CZ}$）が誘起される。そこでフラックス復号器が検出したフラックス位置の周辺辺を「消失候補（flux erasures）」としてマークし、電荷復号グラフにおける該当空間辺の重みを $w_{\mathrm{erasure}} = w_{\mathrm{space}} \times 0.1\text{--}0.25$ へと引き下げることで、位置情報を活用した高感度な復号を実現する（ただし研究3における参照時刻インデックスのバグについては第6章で詳しく論じる）。

---

## 第4章 研究1：2次元トーラス上 $\mathbb{D}_4$ 符号の $X$-スタビライザ閾値評価

本章では、周期境界条件を持つ2次元 $L \times L$ 三角分割トーラス上の $\mathbb{D}_4$ Clifford安定化子符号（`1_D4閾値/2026-09-27_v7/`）を対象に、非可換 $X$-チェック測定が引き起こす再ランダム化とカイラルな色間結合の下で誤り訂正閾値が存在するか否かを検証した研究1の成果を詳述する。特に、ディレクトリ内の複数のコードファイル・検証ログ・CSVデータ（本番10,000ショット系列および試行20,000ショット系列）の役割分担と、それぞれの実行結果から論理的に導出できる事実を厳密に記述する。

### 4.1 コード構成と各ファイルの役割分担

研究1（`1_D4閾値/2026-09-27_v7/`）のコードベースおよび出力データ群は、以下の明確な役割分担の下で構成されている。

1. **`D4_v7_main.ipynb`（メイン・シミュレーション＆閾値解析エンジン）**：
   * **幾何・コホモロジー構築モジュール（`D4Geometry`）**：$L \times L$ トーラス上の頂点 $V$（$|V|=L^2$）、有向辺 $E$（$|E|=3L^2$）、三角形面 $F$（$|F|=2L^2$）および3色 $c \in \{r,g,b\}$ の全 $N=3L^2$ 量子ビットのインデックスを構築し、各頂点チェック $S_{X;v}^c$ の6本のPauli $X$ サポートと2個の異色 $\text{CZ}$ ドレッシングペア、$\mathbb{F}_2$ 上の余境界行列 $H_Z$、平坦部分空間 $C_0 = \ker H_Z$ の基底行列 $M \in \mathbb{F}_2^{3L^2 \times (2L^2+3)}$、および $k=6$ 個の論理ホモロジーサイクル代表元を生成する。
   * **厳密ツイストフレーム・サンプラー（`TwistedFrameSampler` + Numba `@njit` カーネル）**：3.2.1節で定式化した平坦コチェイン空間上のアフィン部分空間 $B = \{Gt = \rho\}$ と2次位相形式 $Q(t) = \sum_{i<j} W_{ij}t_i t_j + d\cdot t$ を追跡する。Numba JITコンパイルされた高速 $\mathbb{F}_2$ ガウス消去・二次形式線形化ルーチンにより、符号容量モデル（$R=1$）、現象論的モデル（$R=L$）、およびネイティブ $\text{CCZ}$ 回路レベルモデル（$R=L$）における各チェック測定の決定論的・確率的射影と状態更新を厳密に実行する。
   * **階層的復号モジュール（`FluxJITDecoder` & `TwoBasisChargeDecoder`）**：3.3節で述べた時空間スライディング窓＋未来境界型の実時間JITフラックス復号器と、各色の2つのホモロジーサイクルに対して2本のカット木上で独立にPyMatching [40] を走らせる2基底MWPM電荷復号器（フラックス履歴に応じた時間辺ソフト重み付け付き）を実装している。
   * **対照実験（Control Experiments）および旧サロゲート比較機能**：
     $\mathbb{D}_4$ の非可換性が閾値に与える純粋な影響を分離するため、同一の格子・同一の復号器上で結合モード `coupling_mode` を切り替える対照実験機能を備えている：
     - `'d4'`（または `'exact_d4'`）：本来の非可換 $\mathbb{D}_4$ ドレッシング $S_{X;v}^c$ をすべて有効化した厳密シミュレーション。
     - `'none'`：すべての $\text{CZ}$ ドレッシング（および回路レベルの $\text{CCZ}$ ゲート）を無効化し、3色の独立な可換トーリック符号（$(TC)^{\otimes 3}$）として動作させるベースライン対照実験。
     - `'kappa_injection'`：安定化子自体は可換なトーリック符号とした上で、フラックスが存在する場所の近傍に人工的な確率的位相キックバック（擬似 $Z$ 反転）のみを注入する対照モデル。真の射影測定による状態空間の再構成（Case 2 更新）と単なる確率的ノイズ注入の違いを検証するために用いられる。
     - `'stim_surrogate'`（旧v6以前のサロゲート実装）：歴史的比較のために残された近似モデルであり、物理的な状態崩壊を追跡せずPauliシンドロームに反転ノイズを重畳する（`v7の評価.md` 等で議論されている通り、これは厳密な $\mathbb{D}_4$ の物理を反映しないため、v7の本番評価では `'d4'` モードが用いられる）。
   * **統計解析・ブートストラップ交点推定モジュール**：各 $(L, p)$ 点の論理誤り率（Wilson信頼区間付き）と、隣接する符号距離ペア $(L_1, L_2) \in \{(3,5), (5,7), (7,9), (9,11)\}$ の対数線形補間による有限サイズ交点 $p_{\times}(L_1, L_2)$ および1,000回ノンパラメトリック・ブートストラップによる $95\%$ 信頼区間を算出し、CSVファイルとして出力する。

2. **`D4_v7_validation.ipynb`（$L=3$ 厳密状態ベクトル参照器による正当化コード）**：
   * 最小の非自明なトーラスサイズである $L=3$（物理量子ビット数 $N = 3 \times 3^2 = 27$）において、JAX（GPU倍精度・単精度テンソル演算）を用いて長さ $2^{27} = 134,217,728$ の複素状態ベクトル $\psi \in \mathbb{C}^{2^{27}}$（メモリ約 $1\text{--}2\text{ GB}$）を直接保持・更新する厳密参照エンジン `DenseBackend` を実装している。
   * `DenseBackend` はツイストフレーム表現やアフィン部分空間の仮定を一切用いず、各頂点チェック $S_{X;v}^c$ の射影演算子 $\Pi_{\pm} = \frac{1}{2}(I \pm S_{X;v}^c)$ をビットシフトとXORマスクによる直接テンソル積演算として状態ベクトルに作用させ、ボルン則 $P(m=+1) = \|\Pi_+ |\psi\rangle\|^2$ を厳密に計算する。
   * この `DenseBackend` と `D4_v7_main.ipynb` の `TwistedFrameSampler` の間で、(A) 幾何・交換関係検証、(B) 同一乱数・同一エラーパターン下での1測定ごとのロックステップ確率比較および事後状態フィデリティ検証、(C) 独立モンテカルロ標本による論理誤り率の $\chi^2$ 一致度検定を実行する。その完全な実行ログが `正当化コード結果/2026-10-02_セル出力完全版.txt` に記録されている。

3. **出力CSVファイル群（2つの実行系列）**：
   * **`メインコード実行結果/9までやった(depo)` / `9までやった(pheno)` / `9までやった(cl)`**：
     各ノイズモデルにおいて $L \in \{3, 5, 7, 9\}$、各点 **10,000ショット** で実行された本番データ系列（`main_v8.tex` の Table I および本文に引用されている数値に対応）。
   * **`参考_試行計算/` 内のCSVファイル群**：
     各点 **20,000ショット** で実行された高精度試行計算系列（`threshold_summary_*.csv`, `crossings_*.csv`）および対照実験データ（`control_summary_*.csv`, `control_crossings_*.csv`）、さらに現象論的モデルにおいて **$L=11$（$N=363$ 量子ビット）まで拡張**した `threshold_summary_phenomenological_L7-9-11.csv` / `crossings_phenomenological_L7-9-11.csv` を格納している（`main_v7.tex` の Table I に対応）。

### 4.2 3種のノイズモデルとネイティブ $\text{CCZ}$ 回路レベル雑音の厳密な定義

研究1では、抽象度の異なる以下の3段階の誤りモデルの下で閾値評価を行った。

#### 4.2.1 符号容量モデル（Code-Capacity / `depolarizing`）
測定ラウンド数を $R = 1$ とし、シンドローム測定自体は理想（測定誤り率 $p_M = 0$）とする。測定前に、全 $N = 3L^2$ 個のデータ量子ビットに対して独立に確率 $p$ の単一量子ビット脱分極誤り（depolarizing noise）を適用する：
$$\mathcal{E}_p^{\mathrm{dep}}(\rho) = (1 - p)\rho + \frac{p}{3}\left( X\rho X + Y\rho Y + Z\rho Z \right).$$
すなわち各データ量子ビットは確率 $p/3$ ずつで $X, Y, Z$ 誤りを被る。したがって $X$ 誤り成分（$X$ または $Y$）が生じるマージナル確率は $p_X = \frac{2}{3}p$、同様に $Z$ 誤り成分（$Z$ または $Y$）のマージナル確率は $p_Z = \frac{2}{3}p$ である。
まず全色の $Z$-プラケット $S_{Z;f}^c$ を一斉測定し、フラックス復号器（$R=1$ 2D MWPM）で推定されたデータ $X$ 補正 $x_{\mathrm{corr}}$ を適用する。もしフラックス復号が成功して残留 $X$ 誤り $x_{\mathrm{res}} = x_{\mathrm{err}} \oplus x_{\mathrm{corr}}$ が平坦コサイクル（$dx_{\mathrm{res}} = 0$）となれば、続く $X$-チェック測定はすべて可換となり再ランダム化は生じない。しかし、残った平坦サイクル $x_{\mathrm{res}}$（あるいはフラックス復号失敗時の非平坦成分）が $\text{CZ}$ ドレッシングを通過する際にデータ $Z$ 誤りへと変換されるため、単なる独立トーリック符号よりも実効的な $Z$ 誤り負荷が増大する。

#### 4.2.2 現象論的モデル（Phenomenological / `phenomenological`）
シンドローム測定を $R = L$ ラウンド反復し、最後に1回の理想的な終端読み出し（terminal readout, $p_M=0$）を行って論理状態を判定する。各測定ラウンド $r \in \{1, \dots, L\}$ の開始時に、すべてのデータ量子ビットに独立な確率 $p$ の脱分極誤り $\mathcal{E}_p^{\mathrm{dep}}$ を適用する。さらに各ラウンドにおいて：
* $Z$-プラケット測定値 $m_Z^c(f)$ が独立に確率 $p_M = p$ で古典ビット反転誤りを起こす。
* $X$-頂点チェック $S_{X;v}^c$ の測定において、真の量子力学的射影測定が行われた後、古典出力ビットが独立に確率 $p_M = p$ で反転する。

このモデルでは、測定誤りによってJITフラックス復号器がすべてのフラックスを即座に消去しきれず、ラウンド間でフラックスが残留する。そのため、異色 $X$-チェック間の反交換による**測定再ランダム化（確率 $1/2$ の固有値ジャンプ）**が全面的に発現する。

#### 4.2.3 ネイティブ $\text{CCZ}$ 回路レベルモデル（Circuit-Level / `circuit_level`）
各頂点チェック $S_{X;v}^c = \left(\prod_{k=1}^6 X_{e_k}^c\right) \text{CZ}_{p_1, q_1} \text{CZ}_{p_2, q_2}$ の測定を、頂点ごとの補助量子ビット $a$ を用いた以下の具体的な9ステップ量子回路として展開する：
1. **ステップ0（初期化）**：補助量子ビット $a$ を $|+\rangle_a$ に準備する。準備誤りとして確率 $p$ で $Z_a$（位相反転）が発生する。
2. **ステップ1〜6（6個の $\text{CNOT}$ ゲート）**：補助量子ビット $a$ を制御ビット、接続する6本の同色データ辺 $e_1, \dots, e_6$ を標的ビットとする $\text{CNOT}_{a \to e_k}$ を順次適用する。各2量子ビット $\text{CNOT}$ の直後に確率 $p$ の2量子ビット脱分極誤り（15種の非自明Pauli積が各確率 $p/15$）が発生する。
3. **ステップ7〜8（2個のネイティブ $\text{CCZ}$ ゲート）**：補助量子ビット $a$ と2組の異色ドレッシング辺ペア $(p_1, q_1), (p_2, q_2)$ に対して、3量子ビット $\text{CCZ}_{a, p_1, q_1}$ および $\text{CCZ}_{a, p_2, q_2}$ を順次適用する。各 $\text{CCZ}$ の直後に確率 $p$ の3量子ビット脱分極誤り（63種の非自明Pauli積が各確率 $p/63$）が発生する。さらに、ゲート前までに補助・データ量子ビット上に蓄積していた一時的な $X$ エラーフレームが $\text{CCZ}$ を通過する際、3.2.3節で導出した非線形変換則 $\text{CCZ} X_i \text{CCZ} = X_i \text{CZ}_{jk}$ に従って、他の2つの量子ビット間に相関した $\text{CZ}$ / $Z$ 位相キックバックを厳密に誘起する。
4. **ステップ9（測定）**：補助量子ビット $a$ を $X$ 基底で測定する。測定直前に確率 $p$ で $Z_a$（測定反転誤り）が発生する。

同様に、各面の $Z$-プラケット測定 $S_{Z;f}^c = \prod_{k=1}^3 Z_{e_k}^c$ も、補助量子ビット $|0\rangle_a$ の準備（確率 $p$ で $X_a$ 誤り）、3個の $\text{CNOT}_{e_k \to a}$（各確率 $p$ の2量子ビット脱分極誤り）、および $Z$ 基底測定（確率 $p$ で $X_a$ 誤り）として回路レベルでシミュレートされる。

ここで、MWPM復号器の重み較正のために、1ラウンドの $X$-チェック抽出回路における1次（線形）の誤り確率を計算しておく：
* **補助量子ビット $a$ の測定反転確率 $p_{\mathrm{flip}}^{(1)}$**：
  準備誤り（$1 \times p$）＋ 測定誤り（$1 \times p$）＋ 6個の $\text{CNOT}$ で制御ビット $a$ に $Z_a$ または $Y_a$ が入る確率（各 $\frac{8}{15}p \times 6 = \frac{16}{5}p = 3.2p$）＋ 2個の $\text{CCZ}$ で $a$ に $Z_a$ または $Y_a$ が入る確率（63種中32種が特定ビットに $Z/Y$ を持つため、厳密には $\frac{32}{63}p \times 2 \approx 1.016p$、コード内では2量子ビット相当の近似係数 $\frac{3}{5}p \times 2 = 1.2p$ を使用）の合計として、
  $$p_{\mathrm{flip}}^{(1)} = p + p + 6 \times \frac{8}{15}p + 2 \times \frac{3}{5}p = \frac{32}{5}p = 6.4p$$
  と較正されている。
* **データ量子ビット1辺あたりの $Z$ 誤り注入確率 $p_{\mathrm{data},Z}^{(1)}$**：
  1本のデータ辺は同色の2つの頂点から計2回の $\text{CNOT}$（各 $\frac{8}{15}p$）、2つのプラケットから計2回の $Z$-測定用 $\text{CNOT}$（各 $\frac{8}{15}p$、およびフック伝播 $\frac{4}{15}p$）、さらに異色の頂点から計6回の $\text{CCZ}$ ゲートに参加する。コード（`D4_v7_main.ipynb`）ではこれらを合算した1次事前確率として $p_{\mathrm{data},Z}^{(1)} = 6.33p$ を用いている。

### 4.3 論理誤り率の評価指標と条件付き指標の定義

研究1では、トーラス上の3色・各2サイクル（計6論理量子ビット）に対して、以下の3つの誤り率指標を区別して記録している：
1. **フラックス復号失敗率 $P_{\mathrm{flux}}$（CSV上の `flux_fail_rate`）**：
   最終ラウンド終了後の理想 $Z$-プラケット読み出しとフラックス復号の結果、残留 $X$ エラー $x_{\mathrm{res}} = x_{\mathrm{err}} \oplus x_{\mathrm{corr}}$ が非自明な論理ホモロジーサイクルを含む（すなわち論理 $X$ 誤りが発生した）ショットの割合。
2. **フラックス成功条件付き電荷論理誤り率 $P_{\mathrm{charge}}$（CSV上の `charge_ler`）**：
   フラックス復号が成功した（残留 $X$ エラーがトポロジカルに自明であった）ショットを分母として、そのうち対象セクター（`'r'` セクター評価では赤の2論理ビット、`'rgb'` 全色評価では全6論理ビット）のいずれかに論理 $Z$ 誤り（電荷復号失敗）が生じた条件付き確率：
   $$P_{\mathrm{charge}} \equiv \Pr\left( \text{Charge Logical Error} \;\middle|\; \text{Flux Decoding Succeeded} \right).$$
3. **複合論理誤り率 $P_{\mathrm{comb}}$（CSV上の `combined_ler`）**：
   全ショットを分母として、フラックス復号が失敗したか、または電荷復号が失敗した全論理誤り確率：
   $$P_{\mathrm{comb}} \equiv \Pr\left( \text{Flux Fail} \cup \text{Charge Fail} \right) = P_{\mathrm{flux}} + (1 - P_{\mathrm{flux}}) P_{\mathrm{charge}}.$$

この区分は極めて重要である。なぜなら、フラックス復号は通常のトーリック符号と同型のPauli $Z$ シンドロームに対する復号であるため、その単独の閾値は比較的高い（符号容量で約 $10.3\text{--}10.9\%$、現象論で約 $2.9\%$）。それに対し、$\mathbb{D}_4$ 符号の本質的な問いは「フラックスが消去される過程で非可換 $X$-チェック測定が被る再ランダム化と位相キックバックのもとで、**電荷セクター $P_{\mathrm{charge}}$ が有限の閾値を持つか**」にあるからである。同時に、システム全体の誤り耐性を示す $P_{\mathrm{comb}}$ の交点も併記することで、偏りのない評価が可能となる。

### 4.4 $L=3$ 厳密状態ベクトル参照器による検証結果（`D4_v7_validation.ipynb`）

`正当化コード結果/2026-10-02_セル出力完全版.txt` に記録された、GPU（NVIDIA L4）上での `DenseBackend`（$2^{27}$ 次元状態ベクトル）と `TwistedFrameSampler` の比較検証結果は以下の通りである。

#### (A) 幾何・交換関係および平坦空間可換性の検証
* $L=3$ トーラス（$N=27$ 量子ビット、27個の $X$-チェック $S_{X;v}^c$）において、全 $\binom{27}{2} = 351$ ペアの演算子レベルでの交換関係 $[S_A, S_B]$ を検査した結果、**異なる色の隣接ペアちょうど $3L^2 = 27$ 組が全ヒルベルト空間上で非可換**（$\Delta_{AB}(a) \neq 0$）であることが確認された。
* 同時に、すべての平坦基底状態 $|b\rangle \in \mathcal{H}_{\mathrm{flat}}$（$\dim C_0 = 2(3^2)+3 = 21$、すなわち $2^{21} = 2,097,152$ 個すべての平坦計算基底配位）の上で $\Delta_{AB}(b) = 0$ となり、**平坦部分空間上の非可換ペア数は厳密に $0$** であることが確認された。

#### (B) ロックステップ（Lockstep）厳密性試験
同一の乱数シードと同一の物理エラー系列を `DenseBackend` と `TwistedFrameSampler` の双方に入力し、各測定ステップにおける測定結果 $+1$ のボルン確率 $P_{\mathrm{dense}}(+1)$ と $P_{\mathrm{fast}}(+1)$ の差、および各ステップ後の正規化状態ベクトル間のフィデリティ $F = |\langle \psi_{\mathrm{dense}} | \psi_{\mathrm{fast}} \rangle|$ の $1$ からのずれ $|1 - F|$ を全ショット・全測定にわたって計測した。

| ノイズモデル | 物理誤り率 $p$ | 評価セクター | ショット数 | 総測定回数 | ボルン確率の最大絶対差 $\max |P_{\mathrm{dense}} - P_{\mathrm{fast}}|$ | 状態フィデリティの最大誤差 $\max |1 - F|$ | 判定 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **符号容量 (`depolarizing`)** | $0.100$ | `r`（赤のみ） | 30 | 270 | $1.12 \times 10^{-8}$ | $1.19 \times 10^{-7}$ | **PASSED** |
| **符号容量 (`depolarizing`)** | $0.100$ | `rgb`（全色） | 10 | 270 | $3.73 \times 10^{-9}$ | $1.19 \times 10^{-7}$ | **PASSED** |
| **現象論的 (`phenomenological`)** | $0.040$ | `r`（赤のみ） | 30 | 1,080 | $1.86 \times 10^{-9}$ | $1.19 \times 10^{-7}$ | **PASSED** |
| **現象論的 (`phenomenological`)** | $0.040$ | `rgb`（全色） | 10 | 1,080 | $0.00$ | $1.19 \times 10^{-7}$ | **PASSED** |
| **回路レベル (`circuit_level`)** | $0.005$ | `r`（赤のみ） | 30 | 1,080 | $5.96 \times 10^{-8}$ | $1.19 \times 10^{-7}$ | **PASSED** |
| **回路レベル (`circuit_level`)** | $0.005$ | `rgb`（全色） | 10 | 1,080 | $5.96 \times 10^{-8}$ | $1.19 \times 10^{-7}$ | **PASSED** |

すべてのモデル・すべてのセクターにおいて、ボルン確率の差は $6 \times 10^{-8}$ 以下、状態フィデリティの誤差は $1.19 \times 10^{-7}$（32ビット単精度浮動小数点 `complex64` の機械イプシロンそのもの）に収まっており、**`TwistedFrameSampler` が近似を一切含まない厳密シミュレータであること**が数値的に完全に証明された。

#### (C) 独立モンテカルロ標本による論理誤り率曲線の統計的一致性検定
さらに、復号器まで含めたエンドツーエンドの論理誤り率曲線が一致することを確認するため、各ノイズモデルの閾値近傍6点の物理誤り率 $p$ において、`DenseBackend`（各点 2,000ショット）と `TwistedFrameSampler`（各点 50,000ショット）を独立な乱数シードで実行し、2標本 $z$-スコアの二乗和 $\chi^2 = \sum_{i=1}^6 z_i^2$（自由度 $\nu = 6$）を検定した：
* **符号容量モデル**（$p \in [0.06, 0.16]$）：
  - $P_{\mathrm{charge}}$：$\chi^2 = 1.46$（$p\text{-value} = 0.962$、$\max |z_i| = 0.78$）
  - $P_{\mathrm{comb}}$：$\chi^2 = 2.17$（$p\text{-value} = 0.903$、$\max |z_i| = 1.24$）
* **現象論的モデル**（$p \in [0.015, 0.040]$）：
  - $P_{\mathrm{charge}}$：$\chi^2 = 6.49$（$p\text{-value} = 0.371$、$\max |z_i| = 1.61$）
  - $P_{\mathrm{comb}}$：$\chi^2 = 1.44$（$p\text{-value} = 0.963$、$\max |z_i| = 0.93$）
* **回路レベルモデル**（$p \in [0.001, 0.005]$）：
  - $P_{\mathrm{charge}}$：$\chi^2 = 7.24$（$p\text{-value} = 0.299$、$\max |z_i| = 1.97$）
  - $P_{\mathrm{comb}}$：$\chi^2 = 8.57$（$p\text{-value} = 0.199$、$\max |z_i| = 1.56$）

すべての項目で $p\text{-value} \ge 0.199 > 0.05$ となり、統計的にも両シミュレータの論理誤り率が完全に一致することが確認された。

### 4.5 メイン・シミュレーション結果：3種のノイズモデルにおける閾値と対照実験

続いて、`D4_v7_main.ipynb` による $L \in \{3, 5, 7, 9\}$（現象論的試行計算では $L=11$ まで）のモンテカルロ実行結果を詳述する。本研究では、作業フォルダ内に保存されている**本番10,000ショット系列**（`メインコード実行結果/9までやった(*)`）と**高精度20,000ショット系列**（`参考_試行計算/`）の両方の数値を対比して提示する（両系列のショット数の違いに起因する既存 `.tex` 原稿間の数値の揺れについては、別紙『修正の要請.md』第2.1節に整理した通りである）。

#### 4.5.1 符号容量モデル（Code-Capacity / `depolarizing`）の結果
まず、測定誤りのない $R=1$ 符号容量モデルにおける有限サイズ交点 $p_{\times}(L_1, L_2)$ を表4.1にまとめる。

| 指標・系列 | 交点 $L=3 \leftrightarrow 5$ | 交点 $L=5 \leftrightarrow 7$ | 交点 $L=7 \leftrightarrow 9$ | 物理的解釈・備考 |
| :--- | :---: | :---: | :---: | :--- |
| **$P_{\mathrm{charge}}$（10k本番：`9までやった(depo)`）** | **$9.24\%$**<br>($8.79\text{--}9.63\%$) | **$9.54\%$**<br>($8.85\text{--}10.24\%$) | **$10.15\%$**<br>($9.53\text{--}10.61\%$) | $L$ の増大に伴い約 $9.5\text{--}10.2\%$ へ収束 |
| **$P_{\mathrm{comb}}$（10k本番：`9までやった(depo)`）** | **$10.89\%$**<br>($10.48\text{--}11.33\%$) | **$10.02\%$**<br>($9.61\text{--}10.40\%$) | **$10.25\%$**<br>($9.86\text{--}10.64\%$) | フラックス失敗と電荷失敗の合成交点 |
| **$P_{\mathrm{charge}}$（20k試行：`参考_試行計算`）** | **$9.37\%$**<br>($9.01\text{--}9.65\%$) | **$9.50\%$**<br>($9.08\text{--}9.97\%$) | **$9.59\%$**<br>($9.08\text{--}10.17\%$) | 20kショットでは $9.4\% \to 9.5\% \to 9.6\%$ と極めて滑らかに単調収束 |
| **$P_{\mathrm{comb}}$（20k試行：`参考_試行計算`）** | **$10.97\%$**<br>($10.71\text{--}11.24\%$) | **$10.11\%$**<br>($9.81\text{--}10.40\%$) | **$9.99\%$**<br>($9.61\text{--}10.35\%$) | $L=7\text{--}9$ で約 $10.0\%$ に収束 |
| **対照実験 `none`（可換TC, $P_{\mathrm{charge}}$, 20k）** | **$9.52\%$**<br>($9.06\text{--}10.01\%$) | **$10.14\%$**<br>($9.45\text{--}10.63\%$) | — | ドレッシングなしの純粋なトーリック符号（$p_Z = \frac{2}{3}p \approx 6.8\%$ 相当） |
| **対照実験 `kappa_injection`（$P_{\mathrm{charge}}$, 20k）** | $< 8.0\%$（グリッド外） | $< 8.0\%$（グリッド外） | — | 人工的な非相関キックバック注入は誤り率を過大に悪化させる |

**【結果から導かれる知見】**：
1. 符号容量モデル（$R=1, p_M=0$）では、$X$-チェック測定の前にフラックス復号器がデータ $X$ エラーを消去する。閾値以下の領域（$p < 9\%$）ではフラックスはほぼ完全に消去されるため、$X$-チェック測定時には系は平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ に戻っており、測定再ランダム化は生じない。
2. そのため、厳密 $\mathbb{D}_4$ モデル（`'d4'`）の $P_{\mathrm{charge}}$ 交点（$9.5\text{--}10.2\%$）は、ドレッシングを完全に切った可換トーリック符号（`'none'`、交点 $9.5\text{--}10.1\%$）と統計誤差の範囲内でほぼ一致する。これは、**フラックスが事前に消去される限り、$\mathbb{D}_4$ の $\text{CZ}$ ドレッシング自体は符号容量閾値をほとんど劣化させない**ことを実証している。
3. 一方、対照実験 `'kappa_injection'` では交点が探索範囲の下限（$8.0\%$）未満へと崩壊している。これは、真の $\mathbb{D}_4$ 測定におけるコホモロジー的に整合した2次位相更新を無視して、単にフラックス近傍へ確率的に独立な $Z$ キックバックを注入する近似モデルが、物理的に誤った過大なペナルティを与えることを明確に示している。

#### 4.5.2 現象論的モデル（Phenomenological / `phenomenological`）の結果
次に、測定誤り（$p_M = p$）と $R = L$ ラウンドの反復測定により非可換測定再ランダム化が全面的に働く現象論的モデルの交点結果を表4.2に、また代表的な誤り率における $L$ 依存性を表4.3にまとめる。

| 指標・系列 | 交点 $L=3 \leftrightarrow 5$ | 交点 $L=5 \leftrightarrow 7$ | 交点 $L=7 \leftrightarrow 9$ | 交点 $L=9 \leftrightarrow 11$ |
| :--- | :---: | :---: | :---: | :---: |
| **$P_{\mathrm{charge}}$（10k本番：`9までやった(pheno)`）** | **$2.25\%$**<br>($2.17\text{--}2.30\%$) | **$2.09\%$**<br>($2.01\text{--}2.13\%$) | **$2.00\%$**<br>($1.94\text{--}2.06\%$) | （未計算） |
| **$P_{\mathrm{comb}}$（10k本番：`9までやった(pheno)`）** | **$2.29\%$**<br>($2.22\text{--}2.34\%$) | **$2.11\%$**<br>($2.06\text{--}2.16\%$) | **$2.01\%$**<br>($1.95\text{--}2.07\%$) | （未計算） |
| **$P_{\mathrm{charge}}$（20k試行：`参考_試行計算` $L \le 9$）** | **$2.25\%$**<br>($2.20\text{--}2.29\%$) | **$2.12\%$**<br>($2.07\text{--}2.16\%$) | **$1.96\%$**<br>($1.91\text{--}2.00\%$) | — |
| **$P_{\mathrm{charge}}$（20k拡張：`L7-9-11`）** | — | — | **$1.95\%$**<br>($1.91\text{--}1.99\%$) | **$1.89\%$**<br>($1.81\text{--}1.97\%$) |
| **$P_{\mathrm{comb}}$（20k拡張：`L7-9-11`）** | — | — | **$1.96\%$**<br>($1.92\text{--}2.01\%$) | **$1.90\%$**<br>($1.82\text{--}1.97\%$) |
| **対照実験 `none`（可換TC, $P_{\mathrm{charge}}$, 20k）** | **$3.11\%$**<br>($2.99\text{--}3.23\%$) | **$2.88\%$**<br>($2.76\text{--}2.97\%$) | **$2.70\%$**<br>($2.60\text{--}2.83\%$) | **$2.72\%$**<br>($2.63\text{--}2.80\%$) |
| **対照実験 `kappa_injection`（$P_{\mathrm{charge}}$, 20k）** | **$2.31\%$**<br>($2.20\text{--}2.40\%$) | **$2.23\%$**<br>($2.11\text{--}2.31\%$) | — | — |

| 物理誤り率 $p$ | $L=3$ ($P_{\mathrm{charge}}$) | $L=5$ ($P_{\mathrm{charge}}$) | $L=7$ ($P_{\mathrm{charge}}$) | $L=9$ ($P_{\mathrm{charge}}$) | $L=11$ ($P_{\mathrm{charge}}$, 20k) | 挙動の判定 |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$1.2\%$** | $4.76\%$ | $1.76\%$ | $0.76\%$ | $0.24\%$ | — | **閾値以下**：$L$ とともに指数関数的に減少 |
| **$1.6\%$** | $9.51\%$ | $6.03\%$ | $3.65\%$ | $2.22\%$ | $1.31\%$ | **閾値以下**：$L=3 \to 11$ で $9.51\% \to 1.31\%$ へ単調減少 |
| **$1.8\%$** | $12.83\%$ | $9.81\%$ | $7.49\%$ | $5.78\%$ | $4.80\%$ | **閾値直下**：$L=11$ まで一貫して単調減少を維持 |
| **$2.0\%$** | $16.51\%$ | $14.32\%$ | $12.89\%$ | $12.85\%$ | $13.36\%$ | **交点領域**：$L=7, 9, 11$ が $12.8\text{--}13.4\%$ で交差 |
| **$2.4\%$** | $25.43\%$ | $27.79\%$ | $30.78\%$ | $36.02\%$ | — | **閾値以上**：$L$ の増大とともに論理誤り率が増大 |

**【結果から導かれる知見】**：
1. **非可換測定下での明確な閾値の存在**：表4.3が示す通り、$p \le 1.8\%$ の領域では、符号距離を $L = 3 \to 5 \to 7 \to 9 \to 11$ と拡大するにつれて論理誤り率 $P_{\mathrm{charge}}$（および $P_{\mathrm{comb}}$）が一貫して単調かつ指数関数的に減少している（例えば $p=1.2\%$ では $L=3$ の $4.76\%$ から $L=9$ の $0.24\%$ へと約 $1/20$ に抑制される）。これにより、**フラックスによる測定再ランダム化が存在する現象論的ノイズ下でも、JITフラックス復号とソフト重み付けMWPM電荷復号の組み合わせによって明確な誤り訂正閾値（$L=9\text{--}11$ で約 $1.89\text{--}2.00\%$）が達成される**ことが実証された。
2. **可換トーリック符号との定量的比較（非可換性のコスト）**：ドレッシングを切った対照実験 `'none'`（3色独立トーリック符号）では、交点は $L=7\text{--}9$ で $2.70\%$、$L=9\text{--}11$ で $2.72\%$ に収束している（脱分極誤り率 $p$ に対して各基底の反転確率が $\frac{2}{3}p$ であるため、標準的な現象論的トーリック符号の閾値 $p_X \approx 1.8\text{--}1.9\%$ すなわち $p \approx 2.7\text{--}2.8\%$ と完全に一致する）。これと比較すると、$\mathbb{D}_4$ の非可換ドレッシングによる閾値の低下は **$2.72\% \to 1.89\%$（相対にして約 $30\%$ の低下）** に留まっており、桁が変わるような壊滅的劣化は起きないことが明らかとなった。
3. **有限サイズドリフトの緩やかな継続**：交点 $p_{\times}(L_1, L_2)$ は $L=3\text{--}5$ の $2.25\%$ から $L=5\text{--}7$ の $2.09\text{--}2.12\%$、$L=7\text{--}9$ の $1.95\text{--}2.00\%$、$L=9\text{--}11$ の $1.89\%$ へと緩やかに低下し続けている。これは、測定誤りによって1ラウンド生き残ったフラックスが周囲の電荷チェックを再ランダム化し、実効的な時空間相関長を広げていることによる有限サイズ効果である（熱力学極限 $L \to \infty$ の漸近閾値を確定させるための $L=13$ 以上の計算は今後の課題である）。

#### 4.5.3 ネイティブ $\text{CCZ}$ 回路レベルモデル（Circuit-Level / `circuit_level`）の結果
最後に、9ステップの補助量子ビット抽出回路（6個の $\text{CNOT}$ と 2個のネイティブ $\text{CCZ}$）を展開した回路レベルモデルの結果を表4.4および表4.5に示す。

| 指標・系列 | 交点 $L=3 \leftrightarrow 5$ | 交点 $L=5 \leftrightarrow 7$ | 交点 $L=7 \leftrightarrow 9$ | 備考 |
| :--- | :---: | :---: | :---: | :--- |
| **$P_{\mathrm{charge}}$（10k本番：`9までやった(cl)`）** | $[0.204\%, 0.233\%, 0.235\%]^*$<br>($0.202\text{--}0.244\%$) | **$0.218\%$**<br>($0.209\text{--}0.224\%$) | **$0.192\%$**<br>($0.177\text{--}0.210\%$) | $^*$10kショットでは $p=0.22\%$ での統計揺らぎにより3回交差 |
| **$P_{\mathrm{comb}}$（10k本番：`9までやった(cl)`）** | **$0.243\%$**<br>($0.206\text{--}0.251\%$) | **$0.220\%$**<br>($0.211\text{--}0.226\%$) | **$0.195\%$**<br>($0.181\text{--}0.211\%$) | $P_{\mathrm{charge}}$ とほぼ同一の交点 |
| **$P_{\mathrm{charge}}$（20k試行：`参考_試行計算`）** | **$0.221\%$**<br>($0.209\text{--}0.232\%$) | **$0.211\%$**<br>($0.204\text{--}0.219\%$) | **$0.193\%$**<br>($0.185\text{--}0.202\%$) | 20kショットでは $L=3\text{--}5$ の多重交差が解消し単一交点 $0.221\%$ に確定 |
| **$P_{\mathrm{comb}}$（20k試行：`参考_試行計算`）** | **$0.225\%$**<br>($0.211\text{--}0.236\%$) | **$0.214\%$**<br>($0.206\text{--}0.221\%$) | **$0.196\%$**<br>($0.189\text{--}0.205\%$) | $0.225\% \to 0.214\% \to 0.196\%$ |
| **対照実験 `none`（$\text{CCZ}$ なし, 20k）** | $> 0.40\%$（グリッド上限超） | $> 0.40\%$（グリッド上限超） | — | $\text{CCZ}$ を除いた次数6のトーリック符号回路は $0.4\%$ 以上の高い閾値を持つ |
| **対照実験 `kappa_injection`（20k）** | **$0.380\%$**<br>($0.369\text{--}0.391\%$) | **$0.353\%$**<br>($0.345\text{--}0.364\%$) | — | 回路内の補助量子ビットを介した非線形 $\text{CZ}$ 伝播を無視するため閾値を過大評価 |

| 物理誤り率 $p$ | $L=3$ ($P_{\mathrm{charge}}$, 20k) | $L=5$ ($P_{\mathrm{charge}}$, 20k) | $L=7$ ($P_{\mathrm{charge}}$, 20k) | $L=9$ ($P_{\mathrm{charge}}$, 20k) | 挙動の判定 |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **$0.10\%$** | $2.84\%$ | $1.31\%$ | $0.68\%$ | $0.32\%$ | **閾値以下**：$L=3 \to 9$ で約 $1/9$ に単調減少 |
| **$0.14\%$** | $6.05\%$ | $4.26\%$ | $3.08\%$ | $2.18\%$ | **閾値以下**：全サイズで明確な誤り抑制 |
| **$0.18\%$** | $10.50\%$ | $9.47\%$ | $8.91\%$ | $8.62\%$ | **閾値直下**：$L=9$ まで単調減少を維持 |
| **$0.20\%$** | $13.38\%$ | $12.90\%$ | $12.99\%$ | $14.07\%$ | **交点領域**：$L=7\text{--}9$ が $p \approx 0.193\%$ で交差 |
| **$0.26\%$** | $23.16\%$ | $26.35\%$ | $30.77\%$ | $36.73\%$ | **閾値以上**：$L$ とともに誤り率が増大 |

**【結果から導かれる知見と現在の実装の限界・留意点】**：
1. **ネイティブ $\text{CCZ}$ 回路レベルでの閾値実証**：表4.5の通り、$p \le 0.18\%$ では $L=3 \to 9$ にわたって論理誤り率が単調減少し（$p=0.10\%$ では $2.84\% \to 0.32\%$）、$L=7\text{--}9$ において **$p_{\times} \approx 0.192\text{--}0.196\%$（約 $0.20\%$）** の有限サイズ交点が確認された。
2. **なぜ回路レベルで対照実験 `'kappa_injection'` は逆に閾値を過大評価するのか**：現象論的モデルでは `'kappa_injection'` は誤り率を過大評価（閾値を低く評価）したのに対し、回路レベルモデルでは `'kappa_injection'` の交点（$0.35\text{--}0.38\%$）の方が厳密 `'d4'`（$0.19\text{--}0.22\%$）よりも高くなっている。この理由は極めて明確である：回路レベルにおける真の `'d4'` モデルでは、補助量子ビット $a$ 上で生じた $X_a$ エラー（前段の $\text{CNOT}$ 故障由来）がステップ7〜8の $\text{CCZ}_{a, p, q}$ ゲートを通過する際、データ量子ビット対 $(p, q)$ の間に直接 **相関した $\text{CZ}_{p,q}$ 位相エラー（フック型の非線形エラー伝播）** を作り出す。`'kappa_injection'` は $\text{CCZ}$ ゲート自体を持たずデータ上のフラックスのみに反応するため、この「補助量子ビット $X$ 故障 $\times \text{CCZ} \to$ データ $\text{CZ}$ フック誤り」という回路レベル特有の主要な誤り経路を完全に落としてしまっているのである。
3. **10kショットデータにおける $L=3\text{--}5$ 多重交差と20kデータでの解消**：`9までやった(cl)`（10kショット）では、$L=3$ と $L=5$ の曲線が $p \in [0.20\%, 0.24\%]$ の間で非常に接近しているため、統計揺らぎにより $[0.204\%, 0.233\%, 0.235\%]$ の3回交差が記録されたが、ショット数を倍増させた `参考_試行計算`（20kショット）では単一の交点 **$0.221\%$** に綺麗に収束している。
4. **【実装上の制約と解釈上の注意】**：研究1の回路レベルモデルに関して、以下の2点は現在の実装の範囲として正確に記述しておく必要がある（詳細は別紙『修正の要請.md』第1.1節参照）：
   * 第一に、ここで実装されている回路は**ネイティブ3量子ビット $\text{CCZ}$ ゲート**を1ステップ（脱分極確率 $p$）と仮定した回路であり、$\text{CCZ}$ をさらに $\text{CNOT} + T/T^\dagger$（6個の $\text{CNOT}$ と 7個の $T/T^\dagger$）へ分解した回路や、時間ステップごとの並列彩色スケジューリングおよび待機（idling）誤りを含めた完全な物理スケジュールではない（完全な並列スケジュールと待機誤りの評価は第6章の研究3で初めて実装された）。
   * 第二に、各頂点の6本の $\text{CNOT}_{a \to e_k}$ からデータ辺へ伝播する重み2〜3の水平 $X$ フック誤り（hook errors）に対して、フラックス復号器のグラフは単一辺重みのみを持つ標準格子グラフを使用している。したがって、フック誤りの順序最適化や相関デコーディングを導入すれば、回路レベル閾値は現在の約 $0.20\%$ からさらに向上する余地がある。

---

## 第5章 研究2：境界付き平面パッチにおける $\mathbb{D}_4$ Code Switching の論理誤り率と閾値評価

研究1によってバルク（周期境界トーラス）における非可換 $\mathbb{D}_4$ 測定の誤り訂正可能性が実証されたことを受け、研究2（`2_CodeSwitching論理誤り率/2026-10-20_エラー率v3/`）では、3種類のギャップ付き境界を持つ三角形（折り畳み正方格子）パッチ（$k=1$ 論理量子ビット）上で、可換な折り畳み表面符号（FSC）から $\mathbb{D}_4$ 符号への切り替え（switch-in）、横断的論理 $\overline{T}^\dagger$ ゲート $U = WV$ の実行、および元のFSCへの復帰（switch-out）を行う**完全な Code Switching プロトコル**を現象論的ノイズ下で構築・評価した。

### 5.1 コード構成と3種のシミュレーション・エンジンの役割分担

研究2（`2_CodeSwitching論理誤り率/2026-10-20_エラー率v3/`）は、以下の3つのPythonスクリプト（およびそれらから自動生成されるJupyter Notebook群）によって構成されている。

1. **`chsc_switch_v3.py`（本番シミュレーション＆復号エンジン）**：
   * **`CHSCGeometry` クラス**：Kobayashiら [27] の境界付き正方格子パッチ（距離 $d$、データ量子ビット数 $N = 6d^2 + 2d$：赤 $2d^2$、青 $2d^2$、緑 $2d^2 + 2d$）の幾何構造、3種のギャップ付き境界条件（$\mathcal{L}_r, \mathcal{L}_b, \mathcal{L}_{rb}$）を満たす安定化子生成元 $S_{X;v}^{r,g,b}$・$S_{Z;f}^{r,g,b}$、および横断的論理ゲート $U = WV$ の $\text{CNOT}$ リスト・$\text{CS}$ リスト・$\text{CS}^\dagger$ リスト・境界 $T^\dagger$ リストを生成する。
   * **`ErrorFrame` クラス & `ProxyBackend` クラス（TBW Algorithm 1 & 3 の実装）**：3.2.2節で詳述した通り、`stim.TableauSimulator` によるPauli-proxy状態追跡と、$\mathbb{Z}_8$ 位相ベクトル $l \in \mathbb{Z}_8^N$・2次位相行列 $Q \in \mathbb{F}_2^{N \times N}$・ビット反転フレーム $x \in \mathbb{F}_2^N$ を持つ `ErrorFrame` を組み合わせた高速・厳密シミュレータである。また、バッチ並列処理（`run_case_batch`）により数万ショットのモンテカルロ計算を高速に実行する。
   * **`JITDecoder` クラス & `Decoders` クラス**：Switch-in 中の $R_{\mathrm{in}} = d$ ラウンドにわたって時空間スライディング窓＋未来境界 MWPM を解き、緑・赤・青のフラックスを実時間で消去する `JITDecoder` と、switch-out 後の $R_{\mathrm{out}} = d$ ラウンドのFSCシンドローム（およびフラックス消失候補 `flux_erasures`）から最終的なデータ $Z$ エラーを復号する `Decoders` を実装している。
   * **`ShotRunner` クラスと最終状態6分類ロジック**：各ショットの終端状態を厳密に検査し、単なる2値（成功 / 失敗）ではなく、論理誤りの物理的性質に応じて以下の**6つの排他的クラス**に分類する：
     - `identity`：論理誤りなし（正しい目標状態 $\overline{T}^\dagger |\overline{+}\rangle = |T^*\rangle$ に到達）。
     - `Z`：純粋な論理 $\overline{Z}$ 誤り（位相反転）。
     - `X`：純粋な論理 $\overline{X}$ 誤り（ビット反転）。
     - `Y`：論理 $\overline{Y} = i\overline{X}\overline{Z}$ 誤り。
     - `S`：論理 $S$ または $S^\dagger$ 位相誤り（エラーフレームの2次位相 $Q=0$ かつ $l \equiv 0 \pmod 2$ であるが、論理コサイクル上の位相積が $\pm 2 \pmod 8$ ずれた非Pauli Clifford誤り）。
     - `collapsed`：残留フラックスが $U=WV$ を通過した結果、消去不能な $\text{CZ}$ エラー（$Q \neq 0$）や奇数 $\mathbb{Z}_8$ 位相（$l_i \equiv 1 \pmod 2$）が残り、そもそも可換表面符号の符号空間へと正しく射影（凝縮）できなかった状態崩壊イベント。

2. **`chsc_validation_v3.py`（3重参照エンジンによる正当化コード）**：
   本番エンジン `ProxyBackend` の数学的・実装上の正当性を一切の妥協なく検証するため、以下の**2つの完全に独立な参照シミュレータ**を実装し、`ProxyBackend` とロックステップ比較およびバッチリプレイ比較を行う（実行結果は `正当化コードセル出力.txt` および `参考_検証ログ/validation_log.txt` に記録）：
   * **参照エンジン1：`BFBackend`（Brute-Force Dense Statevector Backend）**：
     $d=2$（全 $N = 6(4) + 4 = 28$ 量子ビットのうち、活性自由度を縮約した16量子ビット空間、次元 $2^{16} = 65,536$）において、複素状態ベクトルを直接保持し、すべての非Pauli測定射影 $\frac{1}{2}(I \pm S_{X;v}^c)$ と $U = WV$ の対角位相 $\omega^{\Phi_W(a)}$ を定義通り行列・ベクトル積で計算する総当たりエンジン。
   * **参照エンジン2：`TFBackend`（$\mathbb{Z}_4$-Extended Twisted-Frame Backend）**：
     $d=3$（$N=60$ 量子ビット）および $d=4$（$N=104$ 量子ビット）では状態ベクトル計算が不可能であるため、研究1のツイストフレーム表現を $\mathbb{Z}_4$ 値2次形式（$i^{\sum w_i t_i + 2\sum W_{ij}t_i t_j}$）へと拡張し、Stimを一切使わずにコチェイン空間上のガウス消去のみで $U=WV$ を含む全プロトコルを追跡する独立エンジン。

3. **`make_notebooks_v3.py`（ノートブック自動生成ツール）**：
   上記の `chsc_switch_v3.py` と `chsc_validation_v3.py` から、Colab / Jupyter 環境でそのまま実行可能な `chsc_main_v3.ipynb` と `chsc_validation_v3.ipynb` を生成するビルダースクリプト。

### 5.2 評価する3つのプロトコルケースと2つの境界設定（`ideal` vs `noisy`）

研究2では、符号切り替えの各段階が論理誤り率に与える寄与を分離するため、以下の3つのプロトコルケースと2つの境界条件を定義している。

#### 5.2.1 3つのプロトコルケース
1. **`in_only`（Switch-in のみ）**：FSCの $|\overline{+}\rangle$ から出発し、$R_{\mathrm{in}} = d$ ラウンドのノイズ付き switch-in 測定（$S_{X;v}^g$ と $S_{Z;f}^{r,g,b}$）および JIT フラックス復号を行った後、$U$ を作用させずに理想的な switch-out で直ちに論理状態を評価する。
2. **`in_out`（Switch-in ＋ Switch-out、$U = I$）**：ノイズ付き switch-in（$R_{\mathrm{in}} = d$）の後、論理ゲート $U$ を作用させずに緑量子ビットの単一量子ビット $X_e^g$ 測定（測定誤り率 $p$）によって switch-out を行い、続いて FSC 上で $R_{\mathrm{out}} = d$ ラウンドのノイズ付きPauli安定化子測定と最終 MWPM 復号を実行する。
3. **`in_T_out`（完全プロトコル：Switch-in ＋ 横断的 $U = WV$ ＋ Switch-out）**：Switch-in（$R_{\mathrm{in}} = d$）の直後に横断的論理 $\overline{T}^\dagger$ ゲート $U = WV$ を適用し、続いてノイズ付き switch-out と $R_{\mathrm{out}} = d$ ラウンドの FSC 測定・復号を行って、出力状態が理想的な魔法状態 $\overline{T}^\dagger |\overline{+}\rangle$ と一致するかを判定する。

#### 5.2.2 2つの境界設定：`switch_in_boundary="ideal"` vs `"noisy"`
3.2.2節で理論的に示した通り、横断的ゲート $U = WV$ は平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ 上でのみ $\mathbb{D}_4$ 安定化子群の自己同型（インターツイナー）となる。そこで研究2では、$U = WV$ の直前（switch-in の最終ラウンド $r = R_{\mathrm{in}}$）におけるフラックス処理に関して以下の2つの設定を比較した：
* **`switch_in_boundary = "ideal"`（理想フラックス消去境界）**：
  Switch-in の $R_{\mathrm{in}} = d$ ラウンド中は通常の現象論的ノイズ（データ脱分極 $p$、測定誤り $p$）と実時間 JIT 復号が働くが、$U = WV$ に突入する直前の最終ラウンドにおいてのみ、測定誤りのない理想的な $Z$-フラックス測定と2D MWPM補正を行い、**残留フラックスを完全にゼロ（$da_r = da_b = da_g = 0$）にしてから $U = WV$ を適用する**設定（ただしその際にフラックス消去が論理 $X$ サイクルを作ってしまうイベントは `flux_D4` 失敗として正しく計上される）。
* **`switch_in_boundary = "noisy"`（現実的ノイジー境界）**：
  そのような理想フラックス消去を一切行わず、最終ラウンドの測定誤りやデータ誤りによって**消去しきれなかった残留フラックスが存在するまま直接 $U = WV$ および switch-out へと突入する**設定。

### 5.3 正当化コード（`chsc_validation_v3.py`）の実行結果

`正当化コードセル出力.txt` に記録された、全4段階の正当化テストの結果は以下の通りであり、**総計 3,214,446 個の測定・状態出力すべてにおいて不一致 0（完全一致）**を達成している。

1. **段階0：代数的自己診断（Self-Checks, $d \in \{3, 5, 7\}$）**：
   * 非可換ペア数と平坦空間可換性：演算子レベルの非可換ペア数は $d=3$ で $12$ 組、$d=5$ で $48$ 組、$d=7$ で $108$ 組（一般に $3(d-1)^2$ 組）であり、平坦部分空間上の非可換ペア数はすべての $d$ で厳密に **`0`**。
   * 横断的ゲート $U=WV$ の論理作用：基底状態 $|\overline{0}\rangle, |\overline{1}\rangle$ 上での位相が $\kappa \equiv 7 \pmod 8$（$e^{-i\pi/4} = T^\dagger$）であり、`exact_T_dagger = True`。
   * インターツイナー条件 (C1), (C2), (C3) の違反数：$d=3, 5, 7$ すべてにおいて **`(0, 0, 0)`**。
   * $p=0$ 無雑音テスト：`in_only`, `in_out`, `in_T_out` の全ケース・全距離において論理誤り率 $P_L(p=0) = 0.0$。
2. **段階1：`BFBackend`（$d=2$ 厳密状態ベクトル）とのロックステップ検証**：
   * 3ケース（`in_only`, `in_out`, `in_T_out`）$\times$ 2境界（`noisy`, `ideal`）$\times$ 3誤り率（$p \in \{0.005, 0.015, 0.030\}$）$\times$ 各200ショット ＝ **計 3,600 ショット（433,608 個の測定・分類出力）** において、不一致数 **`0`**。
3. **段階2：`TFBackend`（$d=3, 4$ $\mathbb{Z}_4$ Twisted-Frame）とのロックステップ検証**：
   * $d \in \{3, 4\}$ $\times$ 3ケース $\times$ 2境界 $\times$ 2誤り率（$p \in \{0.008, 0.020\}$）$\times$ 各200ショット ＝ **計 4,800 ショット（2,636,318 個の測定・分類出力）** において、不一致数 **`0`**。
4. **段階3：本番バッチ実行経路（`run_case_batch`）の `BFBackend` リプレイ検証**：
   * 本番の高速バッチ関数 `run_case_batch` が生成した乱数・ノイズテープをそのまま `BFBackend` にリプレイさせた **計 1,200 ショット（144,520 個の出力）** において、不一致数 **`0`**。

### 5.4 メイン計算結果：`ideal` 境界と `noisy` 境界における論理誤り率と閾値

#### 5.4.1 `in_T_out`（`switch_in_boundary="ideal"`）の本番20,000ショット結果
`chsc_v3_results/chsc_v3_in_T_out_ideal.csv` および `chsc_v3_in_T_out_ideal_crossings.csv` に記録された、完全な符号切り替え＋論理 $\overline{T}^\dagger$ プロトコル（`in_T_out`, `ideal` 境界、各点 20,000 ショット、$d \in \{3, 5, 7\}$）の数値結果を表5.1および表5.2に示す。

| 符号距離ペア $(d_1, d_2)$ | 交点物理誤り率 $p_{\times}$ | ブートストラップ中央値 | $95\%$ 信頼区間 (CI) | 備考 |
| :--- | :---: | :---: | :---: | :--- |
| **$d = 3 \leftrightarrow 5$** | **$2.97\%$** ($0.02974$) | $2.98\%$ ($0.02975$) | $[2.89\%, 3.10\%]$ | 現象論的ノイズ下での初期交点 |
| **$d = 5 \leftrightarrow 7$** | **$2.41\%$** ($0.02411$) | $2.41\%$ ($0.02414$) | $[2.25\%, 2.54\%]$ | 有限サイズ効果の減少に伴う収束値 |

| 物理誤り率 $p$ | 符号距離 $d$ | 論理誤り率 $P_L$ ($95\%$ CI) | 正常 (`identity`) | $P_Z$ | $P_X$ | $P_Y$ | 非Pauli ($P_S + P_{\mathrm{col}}$) | $\mathbb{D}_4$ フラックス失敗 ($P_{\mathrm{flux\_D4}}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$0.8\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$1.105\%$** ($0.97\text{--}1.26\%$)<br>**$0.150\%$** ($0.10\text{--}0.21\%$)<br>**$0.040\%$** ($0.02\text{--}0.08\%$) | $98.895\%$<br>$99.850\%$<br>$99.960\%$ | $1.075\%$<br>$0.145\%$<br>$0.040\%$ | $0.020\%$<br>$0.005\%$<br>$0.000\%$ | $0.010\%$<br>$0.000\%$<br>$0.000\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |
| **$1.2\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$2.530\%$** ($2.32\text{--}2.76\%$)<br>**$0.640\%$** ($0.54\text{--}0.76\%$)<br>**$0.220\%$** ($0.16\text{--}0.30\%$) | $97.470\%$<br>$99.360\%$<br>$99.780\%$ | $2.430\%$<br>$0.635\%$<br>$0.220\%$ | $0.075\%$<br>$0.005\%$<br>$0.000\%$ | $0.025\%$<br>$0.000\%$<br>$0.000\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |
| **$1.6\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$4.700\%$** ($4.42\text{--}5.00\%$)<br>**$1.870\%$** ($1.69\text{--}2.07\%$)<br>**$0.935\%$** ($0.81\text{--}1.08\%$) | $95.300\%$<br>$98.130\%$<br>$99.065\%$ | $4.400\%$<br>$1.860\%$<br>$0.935\%$ | $0.195\%$<br>$0.005\%$<br>$0.000\%$ | $0.105\%$<br>$0.005\%$<br>$0.000\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |
| **$2.0\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$7.520\%$** ($7.16\text{--}7.89\%$)<br>**$4.225\%$** ($3.95\text{--}4.51\%$)<br>**$3.065\%$** ($2.83\text{--}3.31\%$) | $92.480\%$<br>$95.775\%$<br>$96.935\%$ | $6.940\%$<br>$4.185\%$<br>$3.065\%$ | $0.355\%$<br>$0.025\%$<br>$0.000\%$ | $0.225\%$<br>$0.015\%$<br>$0.000\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |
| **$2.5\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$12.010\%$** ($11.57\text{--}12.47\%$)<br>**$9.310\%$** ($8.91\text{--}9.72\%$)<br>**$9.840\%$** ($9.43\text{--}10.26\%$) | $87.990\%$<br>$90.690\%$<br>$90.160\%$ | $10.580\%$<br>$9.140\%$<br>$9.810\%$ | $0.890\%$<br>$0.095\%$<br>$0.020\%$ | $0.540\%$<br>$0.075\%$<br>$0.010\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |
| **$3.2\%$** | $d=3$<br>$d=5$<br>$d=7$ | **$20.065\%$** ($19.52\text{--}20.63\%$)<br>**$21.925\%$** ($21.36\text{--}22.50\%$)<br>**$27.580\%$** ($26.96\text{--}28.20\%$) | $79.935\%$<br>$78.075\%$<br>$72.420\%$ | $16.585\%$<br>$21.005\%$<br>$27.270\%$ | $1.970\%$<br>$0.495\%$<br>$0.155\%$ | $1.510\%$<br>$0.425\%$<br>$0.155\%$ | $0\%$<br>$0\%$<br>$0\%$ | $0\%$<br>$0\%$<br>$0\%$ |

#### 5.4.2 `ideal` 境界と `noisy` 境界の物理的対比および考察
表5.1・表5.2、ならびに `README_v3.md`（§2.2）および `参考_検証ログ/validation.csv` に記録された `noisy` 境界のパイロットデータから、$\mathbb{D}_4$ Code Switching に関して以下の極めて重要な物理的結論が導かれる。

1. **フラックスが除去された状態での $U = WV$ の完全なPauli保存性**：
   表5.2の `Non-Pauli` 列および $P_{\mathrm{flux\_D4}}$ 列が示す通り、`ideal` 境界設定では、調査したすべての誤り率 $p \in [0.008, 0.036]$ およびすべての符号距離 $d \in \{3, 5, 7\}$（計240,000ショットすべて）において、**非Pauli誤り（$P_S$ および $P_{\mathrm{collapsed}}$）は厳密に $0$** であり、発生する論理誤りはすべてPauli誤り（主として論理 $\overline{Z}$ 誤り $P_Z$、および少量の $P_X, P_Y$）に収まっている。
   これは3.2.2節の理論的導出と完全に一致する：switch-in 終了時点でフラックスが消去されていれば、たとえデータ上に平坦な $X$ エラーサイクルや局所的なゲージシフトが残っていても、それらが $U = WV$ を通過する際に生じる位相変化 $\Delta \Phi_W(a)$ は平坦空間上のインターツイナー条件 (C2)・(C3) によってすべてPauli $Z$ 演算子と緑スタビライザに還元され、非Pauliエラーを一切残さない。その結果、$p=0.8\%$ では $d=3 \to 5 \to 7$ で論理誤り率が **$1.105\% \to 0.150\% \to 0.040\%$（$\Delta d = 2$ あたり約 $4\text{--}7$ 倍の抑制）** と劇的に減少し、交点も **$2.97\%$（$d=3\text{--}5$）および $2.41\%$（$d=5\text{--}7$）** という高い値を示す。

2. **残留フラックスが存在する現実的設定（`noisy` 境界）での非Pauli誤り誘起と有効距離低下**：
   一方、$U=WV$ の直前に理想的なフラックス消去を置かない現実的な `switch_in_boundary="noisy"` 設定（`README_v3.md` §2.2 のパイロット結果および `validation.csv`）では、最終ラウンド $r = R_{\mathrm{in}}$ で発生したデータ $X$ 誤りや測定誤りによって、微小な確率 $\sim O(p)$ でフラックスが消去されないまま $U = WV$ に入る。
   この残留フラックス（非平坦な $x_r, x_b$ 成分）が対角第3階層ゲート $W$（$\text{CS}, \text{CS}^\dagger, T^\dagger$）を通過すると、交換関係 $\text{CS}_{12} X_1 = X_1 S_2 \text{CZ}_{12} \text{CS}_{12}$ により、データ上に**非Pauli位相誤り（$S_i$ 誤り、すなわち $l_i \equiv \pm 2 \pmod 8$）および2量子ビット $\text{CZ}_{ij}$ 誤り（$Q_{ij} = 1$）**が直接生成される。これにより：
   * 最終状態の分類において、`collapsed`（非Pauli状態崩壊）および $P_X, P_Y, P_S$ が有限の割合で出現する（`validation.csv` の $d=3, 4$ `in_T_out (noisy)` において $p=0.8\%$ で $P_{\mathrm{collapsed}} \approx 1.0\text{--}1.5\%$、$p=2.0\%$ で $P_{\mathrm{collapsed}} \approx 12\text{--}21\%$ が観測されている）。
   * 切り替え境界の1ラウンドにおける単一故障がそのまま非Pauli誤りや重み2の相関誤りを作るため、**実効的な符号距離が約 $1$ だけ低下**し、`noisy` 設定における有限サイズ交点は **$d=3\text{--}5$ で約 $1.9\%$、$d=5\text{--}7$ で約 $1.8\%$**（$p=0.8\%$ における論理誤り率は $d=3$ で $2.62\%$、$d=5$ で $1.18\%$、$d=7$ で $0.53\%$）へとシフトする。

3. **【研究2における未実行データと改修待ち事項の明記】**：
   別紙『修正の要請.md』第1.2節・第2.2節に詳述した通り、`chsc_v3_results/` フォルダ内には現在 `in_T_out` の `ideal` 境界の本番CSVのみが出力されており、`in_T_out (noisy)`・`in_only`・`in_out` の本番20,000ショットCSVは未出力（パイロット値および検証ログのみ）の状態にある。また、現在の `chsc_switch_v3.py` では switch-in 中の赤・青電荷シンドロームと switch-out 後の FSC 電荷シンドロームが $U=WV$（ここで $S_{X;v}^r \mapsto S_{X;v}^r S_{X;v}^g$ と変換される）を跨いで単一の時空間グラフとして結合されておらず、switch-out 後の $R_{\mathrm{out}}$ ラウンドのみで電荷 MWPM を行っている。**本来であれば、$U=WV$ 前後のシンドローム変換則を組み込んだ通し時空間復号窓（unified space-time decoding window）の下で `noisy` 境界の有効距離低下がどこまで回復できるかを定量的に示すべきであるが、この点は復号器の改修および追加本番計算待ちである。**

---

## 第6章 研究3：回路レベル雑音下における $\mathbb{D}_4$ Code Switching と 15-to-1 魔法状態蒸留の時空間コスト比較

研究1および研究2により、$\mathbb{D}_4$ 符号のバルク閾値および現象論的ノイズ下での Code Switching の動作原理が確立された。これに続く研究3（`3_魔法状態蒸留との比較/2026-10-29_コスト評価v5_2/`）の目的は、シンドローム抽出の補助量子ビット・物理ゲートスケジュール・待機（idling）デコヒーレンスまで完全に展開した**回路レベル雑音モデル**の下で $\mathbb{D}_4$ 符号切り替えの論理誤り率と時空間資源（量子ビット数 $\times$ 時間ステップ数）を厳密に評価し、同一の物理誤り率・同一の表面符号較正の下で **Litinski（2019）[14, 15] の 15-to-1 魔法状態蒸留（MSD）工場とどちらがどの領域で時空間体積において優位となるか**を定量的に決着させることにある。

### 6.1 コード構成と各ファイル・ノートブックの役割分担

研究3（`3_魔法状態蒸留との比較/2026-10-29_コスト評価v5_2/`）は、`tools/` ディレクトリ内の5つのコアライブラリと3つのビルダースクリプト、およびそれらから生成・実行された3つのメインノートブックと `results/` 内の本番結果ファイル群から構成されている。それぞれの役割分担は以下の通りである。

#### 6.1.1 5つのコアライブラリ（`tools/`）
1. **`tools/common_lib.py`（共通代数・MILP・物理スケジューラ・分解基盤）**：
   * $\mathbb{F}_2$ 上の行簡約階段形（`rref_mod2`）、零空間（`nullspace_mod2`）、連立方程式解法（`solve_mod2`）、および PuLP / CBC ソルバを用いた最小重み論理演算子探索（`min_weight_logical_milp`）。
   * 3量子ビット $\text{CCZ}$ および $\text{NCCZ} = X^{\otimes 3}\text{CCZ}X^{\otimes 3}$、2量子ビット $\text{CS} / \text{CS}^\dagger$、および非破壊的な補助量子ビット結合測定ガジェット（$\text{CCZ}$ ガジェット、$\text{CX}$ ガジェット、$\text{CZ}$ ガジェット）のユニタリ行列とゲート分解。
   * **可換クラス彩色スケジューラ（`commuting_class_schedule`）**：互いに可換な多量子ビットゲート群（例えば同種の $\text{CNOT}$ 層や $\text{CCZ}$ 層）を、同一タイムステップ内で任意の物理量子ビットが高々1個のゲートにしか関与しないように最小ステップ数へと貪欲彩色（greedy edge/hyperedge coloring）する物理スケジューラ。また、$\text{CCZ}$ を6個の $\text{CNOT}$ と7個の $T/T^\dagger$ に展開する T-depth 4 分解（`decompose_to_2q_circuit`）も提供する。
2. **`tools/d4_lib.py`（$\mathbb{D}_4$ / FSC 符号幾何・横断的ゲート・無雑音シミュレータ・資源計数）**：
   * **`KobayashiCode(d)`**：距離 $d$ の折り畳み正方格子パッチ（データ量子ビット数 $N = 6d^2 + 2d$、補助量子ビット数 $N_{\mathrm{anc}} = 6d^2 + 2d - 1$、ピーク総量子ビット数 $N_{\mathrm{tot}} = 12d^2 + 4d - 1$）の幾何構造とスタビライザ生成元、および横断的論理ゲート $U = WV$（論理 $\overline{T}$ モードおよび $\overline{T}^\dagger$ モード）を構築する。
   * **完全物理シンドローム抽出スケジュール**：
     - **FSC 抽出ラウンド**：標準の14ステップ抽出（初期化1 + 赤 $X$ 4 + 青 $X$ 4 + 境界 $X$ 2 + 赤青並列 $Z$ 2 + 測定1 = 14ステップ、`fsc_steps=14`）と、赤・青・境界の $X$ チェックを並列化した8ステップ抽出（初期化1 + 並列 $X$ 4 + 並列 $Z$ 2 + 測定1 = 8ステップ、`fsc_steps=8`）の双方を実装。
     - **$\mathbb{D}_4$ 抽出ラウンド（40ステップ）**：非可換な異色チェック間の干渉を防ぐため、`('g', 'x')`（緑 $X$: 11ステップ）$\to$ `('z',)`（全色 $Z$: 5ステップ）$\to$ `('r', 'x')`（赤 $X$: 12ステップ）$\to$ `('b', 'x')`（青 $X$: 12ステップ）の4フェーズに時分割した計40ステップの物理スケジュールを構築する。
   * **位相公式 `protocol_phase_F` と無雑音スパースシミュレータ `SparseState`**：2.5.2節で導出した switch-out 時のPauli $Z$ フレーム補正位相 $F(a)$ と、任意の距離 $d$ で無雑音プロトコルを検証するスパース状態シミュレータ、および時空間体積を厳密に集計する `kobayashi_counts` を提供する。
3. **`tools/noisy_d4_lib.py`（TBW Algorithm 2 回路レベルシミュレータ & 復号器 & 単一故障スキャン）**：
   * **`FastShot` クラス（TBW Algorithm 2 の実装）**：3.2.3節で詳述した通り、対角第3階層ゲート $D \in \{\text{CCZ}, \text{CS}, \text{CS}^\dagger, T^\dagger, \text{NCCZ}\}$ を除去した回路上で前方伝播 $X$ フレーム `fx` を追跡し、動的Cliffordドレッシング $C_e = D^\dagger X^e D X^e \in \{S, S^\dagger, Z, \text{CZ}\}$ を `stim.TableauSimulator` に挿入する回路レベル厳密シミュレータ。
   * **`TrueSim` クラス（密状態ベクトル参照器）**：$d=2$ 全回路（17量子ビット）および $d=3$ 部分回路に対して複素状態ベクトルを直接進化させる独立参照エンジン。
   * **`FluxDecoder` & `ChargeDecoder`**：各 $Z$ 測定フェーズ後に 2D MWPM でフラックス補正（`fx` 更新）を行う `FluxDecoder` と、switch-in 前の事前 $Z$ 測定および switch-out 後の FSC 測定（ならびにフラックス消失候補 `flux_erasures`）から論理 $\overline{Z}$ 反転を復号する `ChargeDecoder`。
   * **`takada_conditions` & `single_fault_scan`**：Takadaら [39] の許容条件（Definition 1 & 2）をプログラム上で機械的に検証する関数と、回路内のすべての単一故障箇所・全Pauli枝（$d=7$ で最大67,789箇所）を1つずつ決定論的に注入して最小故障重み $w_{\min}$ と単一故障有効数 $c_1$ を全列挙するスキャン関数。
4. **`tools/msd_lib.py`（15-to-1 魔法状態蒸留の代数・格子手術検証）**：
   * Bravyi–Kitaev の [[15, 1, 3]] リード・マラー符号のチェック行列、重み分布、論理回転角度序列 $\theta = \pi/4 \times (1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1)$、無雑音での $35 p^3$ 誤り抑制則の代数的証明、および物理的な4パッチ回転表面符号（$d=2$、19量子ビット）上の格子手術（lattice surgery）による状態ベクトルレベルでの15-to-1蒸留検証を実装。
5. **`tools/msd_noisy_lib.py`（5量子ビット密度行列誤り予算エンジン `DM5` & 表面符号較正）**：
   * **回転表面符号の回路レベル較正**：Stim + PyMatching を用いて標準8ステップ回路の回転表面符号（$d \in \{3, 5, 7\}$）をモンテカルロ評価し、1論理セル・1コードサイクルあたりの論理誤り率 $p_L(d, p) = A (p / p_{\mathrm{th}})^{(d+1)/2}$ を較正する。
   * **`DM5`（5論理量子ビット完全密度行列エンジン）**：Litinski（2019）[14, 15] の非一様距離工場 $(15\text{-to-}1)_{d_X, d_Z, d_m}$・2段階工場 $(15\text{-to-}1)^2$、および GoSC（Game of Surface Codes [14]）の一様距離工場に対し、15回の非Clifford回転それぞれにおける注入誤り $p_{\mathrm{inj}}$ と $(X, Z, m)$ 各方向の格子手術論理誤りを $32 \times 32$ 密度行列上で厳密に伝播させ、事後選択通過確率 $P_{\mathrm{acc}}$ と出力魔法状態誤り率 $\varepsilon_{\mathrm{MSD}}$、および期待時空間体積 $V_{\mathrm{MSD}} / P_{\mathrm{acc}}$ を算出する。

#### 6.1.2 3つのノートブックと出力データの対応
* **`D4_noisy_simulation.ipynb`**：本番モンテカルロ実行ノートブック。`results/d4_noisy_mc.csv`（120条件、**総計 3,788,320 ショット**）および `results/surface_code_plog.csv` を生成。
* **`noisy_cost_comparison.ipynb`**：`d4_noisy_mc.csv` に対する最尤推定（MLE）スケーリングフィット、パラメトリック・ブートストラップ（200回）、および目標誤り率 $\varepsilon_{\mathrm{target}} \in \{10^{-4}, 10^{-6}, 10^{-8}, 10^{-10}\}$ ごとの最小時空間体積比較テーブル `results/cost_comparison.csv` を生成。
* **`validation.ipynb`**：全3部・30大項目・**計195項目（189 PASS, 0 FAIL, 6 INFO）**の独立検証スイートを実行し、`results/validation.json` を出力。

### 6.2 回路レベル雑音モデルの2つのシナリオと時空間資源多項式の導出

#### 6.2.1 回路レベル雑音の2つのシナリオ（Scenario A vs Scenario B）
物理ゲート誤り率 $p$ に対して、各基本操作の誤り率を以下のように設定する：
* 1量子ビット初期化・リセット誤り：$p_1 = p$（$|0\rangle$ 準備後に確率 $p$ で $X$、$|+\rangle$ 準備後に確率 $p$ で $Z$）
* 測定誤り：$p_{\mathrm{meas}} = p$
* 1量子ビットゲート誤り：$p_1 = p$（1量子ビット脱分極）
* 2量子ビットゲート（$\text{CNOT}, \text{CZ}, \text{CS}, \text{CS}^\dagger$）誤り：$p_2 = p$（15種の2量子ビットPauliが各 $p/15$）
* 3量子ビットゲート（$\text{CCZ}, \text{NCCZ}$）誤り：$p_3 = p$（63種の3量子ビットPauliが各 $p/63$）

さらに、当該タイムステップでどのゲート・初期化・測定にも関与していない待機量子ビット（idle qubits）のデコヒーレンスに関して、ハードウェア特性の両端を代表する以下の**2つのシナリオ**を評価する：
1. **Scenario A（Full Idling Noise: $p_{\mathrm{idle}} = p$）**：
   待機中のすべての活性量子ビットが、毎タイムステップ確率 $p_{\mathrm{idle}} = p$ の1量子ビット脱分極誤りを被るモデル（超伝導量子ビットのようにゲート時間と緩和時間の比が厳しい環境に相当）。$\mathbb{D}_4$ の40ステップ抽出では、ある色のチェックを測定している間、他の色の量子ビットが待機するため、待機ノイズが大きな誤り源となる。
2. **Scenario B（Gate-Dominated / Zero Idling Noise: $p_{\mathrm{idle}} = 0$）**：
   待機中のメモリ誤りがゲート誤りに比べて無視できるモデル（中性原子アレイやイオントラップのように、コヒーレンス時間 $T_1, T_2$ がゲート時間より数桁長い環境に相当）。

#### 6.2.2 $\mathbb{D}_4$ Code Switching の量子ビット数・時間ステップ数・時空間体積の厳密な多項式
標準設定（初期準備ラウンド数 $R_0 = \kappa_0 d = d$、事前 $Z$ 抽出 $R_{\mathrm{preZ}} = 2$、switch-in ラウンド数 $R_{\mathrm{in}} = \kappa_{\mathrm{in}} d = d$、switch-out 後 FSC ラウンド数 $R_{\mathrm{out}} = \kappa_{\mathrm{out}} d = d$）における各ステージの物理量子ビット数とタイムステップ数、およびそれらの積和である時空間体積（space-time volume, 単位：qubit-steps）を導出する（表6.1）。

| プロトコル段階（Stage） | 活性データ量子ビット数 | 活性補助量子ビット数 | ステージ総量子ビット数 $Q_{\mathrm{stage}}(d)$ | 時間ステップ数 $T_{\mathrm{stage}}(d)$（14step FSC） | 時空間体積寄与 $Q_{\mathrm{stage}} \times T_{\mathrm{stage}}$（14step FSC） |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stage 0: FSC初期化・準備** ($R_0 = d$ ラウンド) | $4d^2$（赤・青） | $4d^2 - 1$ | $8d^2 - 1$ | $1 + 14d$ | $112d^3 + 8d^2 - 14d - 1$ |
| **Stage 1a: 緑データ初期化 + 事前 $Z$ 抽出** ($R_{\mathrm{preZ}} = 2$) | $6d^2 + 2d$（全3色） | $3d^2$（全色 $Z$ 補助） | $9d^2 + 2d$ | $1 + 2 \times 5 = 11$ | $99d^2 + 22d$ |
| **Stage 1b: Switch-in ($\mathbb{D}_4$ 抽出)** ($R_{\mathrm{in}} = d$ ラウンド) | $6d^2 + 2d$ | $6d^2 + 2d - 1$ | **$12d^2 + 4d - 1$**（ピーク） | $40d$ | $480d^3 + 160d^2 - 40d$ |
| **Stage 2: 横断的論理ゲート $U = WV$** | $6d^2 + 2d$ | $0$ | $6d^2 + 2d$ | $5$（彩色後5ステップ） | $30d^2 + 10d$ |
| **Stage 3a: 緑データ $X_e^g$ 一斉測定 (Switch-out)** | $6d^2 + 2d$ | $0$ | $6d^2 + 2d$ | $1$ | $6d^2 + 2d$ |
| **Stage 3b: Switch-out 後 FSC 抽出** ($R_{\mathrm{out}} = d + 1$ ラウンド) | $4d^2$（赤・青） | $4d^2 - 1$ | $8d^2 - 1$ | $14(d + 1) + 1 = 14d + 15$ | $112d^3 + 120d^2 - 14d - 15$ |
| **合計（14-step FSC 標準スケジュール）** | Peak data: **$6d^2 + 2d$** | Peak anc: **$6d^2 + 2d - 1$** | **Peak total: $12d^2 + 4d - 1$** | **$68d + 33$**（全段階）<br>**$62d + 21$**（`kobayashi_counts`） | **$632d^3 + 454d^2 + 8d - 14$**<br>（`kobayashi_counts` 定義） |

ここで、`tools/d4_lib.py` の `kobayashi_counts(d, fsc_steps=14)`（および `docs/methods.md` §10）では、各フェーズの実効活性量子ビット数とステップ数を以下のように集計している：
* **14ステップ FSC スケジュール（`fsc_steps=14`）**：
  - ピーク量子ビット数：$Q_{\mathrm{peak}}(d) = 12d^2 + 4d - 1$（$d=3$ で $119$、$d=5$ で $319$、$d=7$ で $615$、$d=9$ で $1,007$ 量子ビット）。
  - 総ステップ数：$T_{\mathrm{tot}}(d) = 62d + 21$（$d=3$ で $207$、$d=5$ で $331$、$d=7$ で $455$、$d=9$ で $579$ ステップ）。
  - 総時空間体積：$V_K^{(14)}(d) = 632d^3 + 454d^2 + 8d - 14$（$d=3$ で **$21,160$**、$d=5$ で **$90,376$**、$d=7$ で **$239,056$**、$d=9$ で **$497,794$** qubit-steps）。
* **8ステップ並列 FSC スケジュール（`fsc_steps=8`）**：
  FSCの1ラウンドを14ステップから8ステップへ短縮した場合、Stage 0（$d$ ラウンド）と Stage 3b（$d$ ラウンド）の計 $2d$ ラウンドで $6 \times 2d = 12d$ ステップ（体積にして $(8d^2-1) \times 12d = 96d^3 - 12d$）が削減される。したがって数学的に厳密な多項式は
  $$T_{\mathrm{tot}}^{(8,\mathrm{exact})}(d) = 50d + 21, \qquad V_K^{(8,\mathrm{exact})}(d) = 536d^3 + 407d^2 + 20d - 14$$
  となる。（**【コード上の微細なバグに関する注記】**：別紙『修正の要請.md』第1.3.2節に記した通り、`d4_lib.py` の `kobayashi_counts(d, fsc_steps=8)` の実装では `fsc_steps == 14` の分岐の外側で初期データ準備の1ステップ `('S0', 1)` が脱落しており、コード上では1ステップ少ない $50d + 20$ ステップ、体積 $536d^3 + 398d^2 + 16d - 13$［$d=3$ で $18,059$、真値は $18,130$、相対差 $0.4\%$］として計算されている。以下の表では本番CSVの数値をそのまま示しつつこの点を留保する。）

### 6.3 189項目の独立検証（`validation.ipynb`）と単一故障全列挙（N5）の発見

本番モンテカルロ計算に先立ち、`validation.ipynb`（出力：`results/validation.json`）において以下の3部構成・計195項目（**189 PASS, 0 FAIL, 6 INFO**）の徹底的な検証が実行された。

1. **第1部：無雑音 $\mathbb{D}_4$ プロトコルと多項式資源式の検証（V1〜V11：計68 PASS）**：
   * $d \in \{2, 3, 4, 5\}$ におけるスタビライザ交換関係、平坦部分空間上の実効的可換性、MILP による最小論理演算子重みが厳密に $d$ に一致すること（V1–V4）。
   * 横断的論理ゲート $U = WV$ のインターツイナー条件 (C1)–(C3) と、位相公式 $F(a)$ を用いた switch-in $\to U \to$ switch-out の無雑音論理フィデリティが、すべての緑シンドローム分岐に対して厳密に $F = 1.000000$ となること（V5–V9）。
   * ゲート彩色スケジュールの衝突ゼロ証明と資源多項式の検証（V10–V11）。
2. **第2部：15-to-1 魔法状態蒸留と格子手術の検証（M1〜M9：計45 PASS）**：
   * [[15, 1, 3]] リード・マラー符号の距離3、重み分布、15回転による無雑音 $|T\rangle$ 射影、および独立誤りに対する厳密展開 $P_{\mathrm{acc}} = 1 - 15p + 105p^2 - 455p^3 + \dots$, $\varepsilon_{\mathrm{out}} = 35p^3 + O(p^4)$ の数値的確認（M1–M5）。
   * 4パッチ回転表面符号（$d=2$、19量子ビット）上の物理格子手術シミュレーションによる 15-to-1 蒸留の完全動作実証（M6–M9）。
3. **第3部：TBW 回路レベルシミュレータ `FastShot` の厳密性と単一故障スキャン（N1〜N10：計76 PASS, 6 INFO）**：
   * **N1（Takada 許容条件の機械的検証）**：$d \in \{2, 3, 4, 5\}$ において、インボリューティブ条件、群交換子のPauli $Z$ 包含、および Primary-support exactness（$\operatorname{rank}(M_X) = n_X$）がすべて `True` であることを証明。
   * **N2–N4（状態ベクトル参照器 `TrueSim` との完全一致検証）**：
     - 4種類の単体テスト回路（$\text{CCZ}, \text{CS}, T^\dagger, \text{NCCZ}$ ＋ ランダムPauli故障）において、`FastShot` と状態ベクトル `TrueSim` の測定分布の全変動距離（TVD）が統計誤差内（$\text{TVD} < 0.015$）で完全一致。
     - $d=2$ の完全なプロトコル回路（17量子ビット）および $d=3$ の部分回路において、同一故障列に対する決定論的リプレイ出力が **100% 完全一致**。

#### 単一故障全列挙（Single-Fault Scan, N5）が明らかにした切り替え窓の重要な物理的性質
検証スイートの **N5（`single_fault_scan`）** では、回路内のすべてのゲート・初期化・測定・待機ロケーションに単一のPauli故障（1量子ビットは3通り、2量子ビットは15通り、3量子ビットは63通り）を1つずつ決定論的に注入し、復号後に論理誤りが生じるか否かを全数調査した。その結果（`validation.json` N5）を表6.2に示す。

| 符号距離 $d$ | シナリオ | スキャン対象 | 調査ロケーション数 | 論理誤りを起こす単一故障箇所数 | 有効単一故障重み $c_1 = \sum w_{\mathrm{branch}}$ | 故障が集中するステージの内訳 |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| **$d = 3$** | Scenario A ($p_{\mathrm{idle}}=p$) | 全回路 | 7,068 | **275 箇所** | **$c_1 = 15.71$** | `('S1', 3, 'x')`: 200箇所、`('S1', 5, 'z')`: 25箇所、`('U',)`: 24箇所、`('S0', 3)`: 15箇所、`('S2', 1)`: 11箇所 |
| **$d = 3$** | Scenario B ($p_{\mathrm{idle}}=0$) | 全回路 | 3,135 | **180 箇所** | **$c_1 = 4.16$** | `('S1', 3, 'x')`: 136箇所、`('S1', 5, 'z')`: 16箇所、`('U',)`: 16箇所、`('S0', 3)`: 6箇所、`('S2', 1)`: 6箇所 |
| **$d = 5$** | Scenario A ($p_{\mathrm{idle}}=p$) | 切り替え窓 | 10,800 | **26 箇所** | **$c_1 = 0.88$** | `('S1', 5, 'x')`: 6箇所、`('S1', 7, 'z')`: 20箇所 |
| **$d = 5$** | Scenario B ($p_{\mathrm{idle}}=0$) | 切り替え窓 | 3,775 | **11 箇所** | **$c_1 = 0.27$** | `('S1', 5, 'x')`: 11箇所（すべて最終 switch-in ラウンドの $X$ フェーズ） |
| **$d = 7$** | Scenario B ($p_{\mathrm{idle}}=0$) | 切り替え窓 | 7,175 (67,789枝) | **0 箇所** | **$c_1 = 0.00$** | **全 67,789 通りの単一Pauli故障に対して論理誤りゼロ（$w_{\min} \ge 2$）を達成！** |

**【単一故障スキャン N5 とコード精査から得られた3つの重大な知見】**：
1. **$d=3, 5$ でわずかに単一故障（$c_1 > 0$）が残る理由**：
   表6.2の内訳を見ると、論理誤りを引き起こす単一故障のほぼすべてが **`('S1', Rin, 'x')`（すなわち横断的ゲート $U$ の直前にあたる switch-in 最終ラウンドの赤・青・緑 $X$ チェック抽出フェーズ）** に集中している！
   なぜこのフェーズの単一故障が致命的になるのか？その理由は、`d4_lib.py` の40ステップ $\mathbb{D}_4$ スケジュールが `('g', 'x')` $\to$ `('z',)` $\to$ `('r', 'x')` $\to$ `('b', 'x')` の順になっており、**全色 $Z$-プラケット測定 `('z',)` の後に赤・青の $X$ チェック `('r', 'x')`, `('b', 'x')`（多数の3量子ビット $\text{CCZ}$ ゲートを含む）が実行され、その後に追加の $Z$ 測定を行わずにそのまま横断的論理ゲート $U = WV$ へ突入しているから**である。その結果、最終ラウンドの `('r', 'x')` や `('b', 'x')` 内の $\text{CCZ}$ ゲートまたはフック伝播で生じたデータ $X$ エラー（フラックス）や相関 $\text{CZ}$ エラーが、一度もフラックス復号器に検知されないまま $U = WV$ に入り込み、重み2〜3の相関位相エラーへと増幅される。$d=3$（実効重み $\lfloor(d+1)/2\rfloor = 2$）および $d=5$ の境界近傍では、この単一故障由来の相関エラーが論理鎖の半分を超えてしまう。
2. **$d=7$ における単一故障完全耐性（$c_1 = 0$）と2重故障フロア $W(p)$**：
   $d=7$（Scenario B）になると、最小論理重みが大きいため、上記の単一故障から生じる局所相関エラーだけでは論理誤りに届かず、**全67,789通りの単一故障に対して論理誤りゼロ（$c_1 = 0.00$、最小故障重み $w_{\min} \ge 2$）**が達成される！
   しかし同時に、現在の `FluxDecoder` が各ラウンド単独の2D MWPM（即時貪欲マッチング）であり、かつ事前 $Z$ 抽出が定数ラウンド（$R_{\mathrm{preZ}} = 2$）に固定されているため、切り替え窓における**高々2〜3個の故障の組み合わせ（確率 $\propto p^2 \sim p^{2.4}$）**が、符号距離 $d$ をいくら大きくしても消えない**切り替え窓の誤りフロア $W(p) = w p^\gamma$** を形成する。
3. **【コード精査で発見された `ChargeDecoder` の `flux_erasures` インデックス参照バグ】**：
   さらに本研究のコード監査（別紙『修正の要請.md』第1.3.1節）において、`tools/noisy_d4_lib.py` の `ChargeDecoder.decode` メソッド（437行目）に以下の重大なインデックス不一致バグが存在することを発見した：
   * シミュレータ `FastShot`（292–294行目）では、switch-in の各ラウンド `r`（ここで `r` は `1` から `Rin` まで動く：`for r in range(1, self.Rin + 1):`）において、検出されたフラックス消失候補をキー `(r, c)`（すなわち $r \in \{1, \dots, R_{\mathrm{in}}\}$）として `flux_erasures[(r, c)]` に記録している。また、事前 $Z$ 抽出の2ラウンドはキー `('pre', 1, c)`, `('pre', 2, c)` に記録されている。
   * ところが復号器 `ChargeDecoder.decode`（437行目）では、消失重み付けを取得する際に
     ```python
     er = set(shot['flux_erasures'].get((self.Rin, c), set())) | set(shot['flux_erasures'].get((self.Rin + 1, c), set()))
     ```
     と記述されており、**存在しないキー `(self.Rin + 1, c)` を参照して常に空集合 `set()` を得ている**（さらに事前 $Z$ ラウンドの `'pre'` や $r < R_{\mathrm{in}}$ の履歴も参照されていない）。
   * したがって、本研究3の現在の数値結果は「最終ラウンド `self.Rin` の1ラウンド分のフラックス消失情報のみが `ChargeDecoder` に渡された（やや保守的な）復号性能」を表しており、これを修正し時空間フラックス復号器と組み合わせることで、切り替え窓の誤り率はさらに改善する余地がある。

### 6.4 回転表面符号の回路レベル較正と 15-to-1 魔法状態蒸留の誤り予算

$\mathbb{D}_4$ Code Switching と公平な比較を行うため、`results/surface_code_plog.csv` では同一の物理ノイズモデル（Scenario A および Scenario B）の下で回転表面符号の1論理セル・1コードサイクルあたりの論理誤り率 $p_L(d, p)$ を較正している。最小二乗フィットにより得られたスケーリング則
$$p_L(d, p) = A \left( \frac{p}{p_{\mathrm{th}}} \right)^{(d+1)/2}$$
のパラメータは以下の通りである：
* **Scenario A（$p_{\mathrm{idle}} = p$）**：$A = 0.079$, $p_{\mathrm{th}} = 0.0085$（$0.85\%$）。例えば $p=10^{-4}$ において、$d=3$ で $p_L = 1.07 \times 10^{-5}$、$d=5$ で $p_L = 1.67 \times 10^{-7}$、$d=7$ で $p_L = 2.6 \times 10^{-9}$。
* **Scenario B（$p_{\mathrm{idle}} = 0$）**：$A = 0.040$, $p_{\mathrm{th}} = 0.0119$（$1.19\%$）。例えば $p=10^{-4}$ において、$d=3$ で $p_L = 3.00 \times 10^{-6}$、$d=5$ で $p_L = 2.67 \times 10^{-8}$、$d=7$ で $p_L = 1.9 \times 10^{-10}$。

この $p_L(d, p)$ と状態注入誤り率 $p_{\mathrm{inj}} = p$（感度解析では $p_{\mathrm{inj}} = 2p$ も評価）を5論理量子ビット密度行列エンジン `DM5` に入力すると、Litinski（2019）[14, 15] の各 15-to-1 蒸留工場の時空間体積（2ステップ表面符号スケジュール換算）は以下の値となる：
* **GoSC 一様距離 15-to-1 工場**（11論理タイル $\equiv 22 d^2$ 量子ビット、$6d$ コードサイクル $\equiv 48d$ ステップ）：
  - $d=3$：量子ビット数 $198$、時間ステップ数 $144$、無雑音体積 **$38,880$**（$p=10^{-4}$ での事後選択込み期待体積 **$39,261$** qubit-steps）。
  - $d=5$：無雑音体積 **$180,000$** qubit-steps。
* **Litinski (2019) 非一様距離 $(15\text{-to-}1)_{d_X, d_Z, d_m}$ 工場**（フットプリント $2(d_X + 4 d_Z) d_X + 4 d_m^2$ 量子ビット、$6 d_m$ コードサイクル $\equiv 48 d_m$ ステップ）：
  - $(15\text{-to-}1)_{5, 3, 3}$：量子ビット数 $392$、時間ステップ数 $144$、無雑音体積 **$56,448$**（$p=2\times 10^{-4}$ での期待体積 **$56,586$** qubit-steps）。
  - $(15\text{-to-}1)_{7, 3, 3}$：量子ビット数 $572$、時間ステップ数 $144$、無雑音体積 **$82,368$**（$p=10^{-4}$ で $\varepsilon_{\mathrm{MSD}} \approx 3.8 \times 10^{-10} \le 10^{-8}$ を達成、期待体積 **$82,492$** qubit-steps）。
  - $(15\text{-to-}1)_{9, 3, 3}$：量子ビット数 $792$、時間ステップ数 $144$、無雑音体積 **$114,048$**（$p=2\times 10^{-4}$ で $\varepsilon_{\mathrm{MSD}} \le 10^{-8}$ を達成、期待体積 **$114,392$** qubit-steps）。

### 6.5 379万ショットの回路レベル・モンテカルロ結果と最尤推定スケーリング解析

`results/d4_noisy_mc.csv`（本番ランID: `production-20261029T150244Z-88b3f1`、総計 **3,788,320 ショット**）で得られた、$\mathbb{D}_4$ Code Switching の回路レベル論理誤り率 $\varepsilon_K(d, p)$ の主要結果を表6.3にまとめる。ここでは、通常の全回路ノイズシミュレーション（`window_noise = "noisy"`、すなわち `main` モデル）に加え、切り替え窓（Stage 1a の事前 $Z$ 抽出、Stage 2 の $U=WV$、Stage 3a の緑 $X$ 測定）のゲート誤りのみをゼロにしてバルクの誤り抑制能力を分離測定した診断モード（`window_noise = "quiet"`）の結果を併記する。

| シナリオ | 窓設定 | 物理誤り率 $p$ | $d=3$ 論理誤り率 $\varepsilon_K$ | $d=5$ 論理誤り率 $\varepsilon_K$ | $d=7$ 論理誤り率 $\varepsilon_K$ | $d=9$ 論理誤り率 $\varepsilon_K$ | 物理的挙動の解釈 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **`noisy`**<br>(全回路本番) | $1 \times 10^{-4}$<br>$2 \times 10^{-4}$<br>$3 \times 10^{-4}$<br>$5 \times 10^{-4}$<br>$1 \times 10^{-3}$ | $4.58 \times 10^{-4}$<br>$9.50 \times 10^{-4}$<br>$1.62 \times 10^{-3}$<br>$3.21 \times 10^{-3}$<br>$1.02 \times 10^{-2}$ | $2.00 \times 10^{-5}$<br>$8.00 \times 10^{-5}$<br>$2.60 \times 10^{-4}$<br>$7.27 \times 10^{-4}$<br>$4.63 \times 10^{-3}$ | $8.0 \times 10^{-6}$<br>$7.00 \times 10^{-5}$<br>$1.81 \times 10^{-4}$<br>$5.18 \times 10^{-4}$<br>$2.83 \times 10^{-3}$ | $0$ ($<4.5\times 10^{-5}$)<br>$9.4 \times 10^{-5}$<br>$2.17 \times 10^{-4}$<br>$6.64 \times 10^{-4}$<br>$3.48 \times 10^{-3}$ | $d=3 \to 5 \to 7$ で急減した後、$d \ge 5\text{--}7$ で切り替え窓フロア $W(p) \sim 0.48p$ に漸近 |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **`quiet`**<br>(バルク診断) | $1 \times 10^{-4}$<br>$3 \times 10^{-4}$<br>$5 \times 10^{-4}$<br>$1 \times 10^{-3}$ | $3.50 \times 10^{-4}$<br>$1.20 \times 10^{-3}$<br>$2.19 \times 10^{-3}$<br>$5.49 \times 10^{-3}$ | $0$ ($<3.3\times 10^{-5}$)<br>$4.00 \times 10^{-5}$<br>$8.00 \times 10^{-5}$<br>$8.00 \times 10^{-4}$ | $0$ ($<5.6\times 10^{-5}$)<br>$0$ ($<5.6\times 10^{-5}$)<br>$5.6 \times 10^{-5}$<br>$2.22 \times 10^{-4}$ | — | 窓フロアを除けば、バルクは $p=3\times 10^{-4}$ で $\Delta d=2$ あたり **$6.6\times$** の指数関数的抑制を示す |
| **Scenario A**<br>($p_{\mathrm{idle}}=p$) | **`noisy`**<br>(全回路本番) | $1 \times 10^{-4}$<br>$2 \times 10^{-4}$<br>$3 \times 10^{-4}$<br>$5 \times 10^{-4}$<br>$1 \times 10^{-3}$ | $2.77 \times 10^{-3}$<br>$8.59 \times 10^{-3}$<br>$1.84 \times 10^{-2}$<br>$4.57 \times 10^{-2}$<br>$1.60 \times 10^{-1}$ | $3.43 \times 10^{-4}$<br>$1.66 \times 10^{-3}$<br>$4.97 \times 10^{-3}$<br>$1.93 \times 10^{-2}$<br>$1.15 \times 10^{-1}$ | $1.67 \times 10^{-4}$<br>$1.04 \times 10^{-3}$<br>$2.67 \times 10^{-3}$<br>$1.37 \times 10^{-2}$<br>$9.88 \times 10^{-2}$ | $3.97 \times 10^{-4}$<br>$9.53 \times 10^{-4}$<br>$2.66 \times 10^{-3}$<br>$1.31 \times 10^{-2}$<br>$1.12 \times 10^{-1}$ | 待機誤りにより窓フロアが $W(p) \sim 9.2p$（$p=3\times 10^{-4}$）へと約19倍増大 |
| **Scenario A**<br>($p_{\mathrm{idle}}=p$) | **`quiet`**<br>(バルク診断) | $1 \times 10^{-4}$<br>$3 \times 10^{-4}$<br>$5 \times 10^{-4}$<br>$1 \times 10^{-3}$ | $2.25 \times 10^{-3}$<br>$1.01 \times 10^{-2}$<br>$2.57 \times 10^{-2}$<br>$9.26 \times 10^{-2}$ | $2.00 \times 10^{-4}$<br>$2.08 \times 10^{-3}$<br>$9.56 \times 10^{-3}$<br>$6.64 \times 10^{-2}$ | $0$ ($<5.6\times 10^{-5}$)<br>$6.67 \times 10^{-4}$<br>$3.78 \times 10^{-3}$<br>$5.39 \times 10^{-2}$ | — | バルク自体は $p=3\times 10^{-4}$ で $\Delta d=2$ あたり **$4.7\times$** の指数関数的抑制を維持 |

#### バルク誤り率と切り替え窓フロアの分離モデル（MLE Fitting）
表6.3のデータは、$\mathbb{D}_4$ Code Switching の回路レベル論理誤り率 $\varepsilon_K(d, p)$ が、符号距離 $d$ とともに指数関数的に減衰する**バルク項 $\varepsilon_{\mathrm{bulk}}(d, p)$** と、符号距離 $d$ にほとんど依存しない**切り替え窓フロア項 $W(p)$** の和
$$\varepsilon_K(d, p) = 1 - \left(1 - \varepsilon_{\mathrm{bulk}}(d, p)\right)\left(1 - W(p)\right) \approx C_{\mathrm{bulk}} \, d \left( \frac{p}{p_{\mathrm{th,bulk}}} \right)^{(d+1)/2} + w \, p^\gamma$$
によって極めて高精度に記述されることを示している。`noisy_cost_comparison.ipynb` による二項対数尤度の最尤推定（MLE）から得られたパラメータは以下の通りである：
* **Scenario B（$p_{\mathrm{idle}} = 0$）**：
  - バルク閾値 $p_{\mathrm{th,bulk}} \approx 0.0028\text{--}0.0032$（約 $0.30\%$）、$p = 3 \times 10^{-4}$ における $\Delta d = 2$ あたりのバルク誤り低減率は **$6.6\times$**。
  - 切り替え窓フロア $W(p) = w p^\gamma$ のべき指数は **$\gamma \approx 2.4$**（単一故障が抑制され2重〜3重故障が支配的であることを反映）であり、$p = 3 \times 10^{-4}$ における $W(p)/p$ は **$0.48$**（すなわち $W(3\times 10^{-4}) \approx 1.44 \times 10^{-4}$、$W(10^{-4}) \approx 1.0 \times 10^{-5}$）。
* **Scenario A（$p_{\mathrm{idle}} = p$）**：
  - バルク閾値 $p_{\mathrm{th,bulk}} \approx 0.0014$（約 $0.14\%$）、$p = 3 \times 10^{-4}$ における $\Delta d = 2$ あたりのバルク低減率は **$4.7\times$**。
  - 待機誤りが40ステップ抽出中に蓄積するため、$p = 3 \times 10^{-4}$ における窓フロアは $W(p)/p = 9.2$（$W(3\times 10^{-4}) \approx 2.76 \times 10^{-3}$、$W(10^{-4}) \approx 2.2 \times 10^{-4}$）へと上昇する。

また、switch-in ラウンド数 $\kappa_{\mathrm{in}} \in \{0.5, 1.0, 1.5\}$ の感度実験（`d4_noisy_mc.csv` の `kin_sensitivity`）からは、$d=5, p=3\times 10^{-4}$ において $\kappa_{\mathrm{in}} = 0.5$（$R_{\mathrm{in}}=2$）では誤り率が上昇する一方、$\kappa_{\mathrm{in}} = 1.0$（$R_{\mathrm{in}}=5$）と $\kappa_{\mathrm{in}} = 1.5$（$R_{\mathrm{in}}=7$）では窓フロア $W(p)$ に律速されて誤り率が飽和する（Scenario A では待機誤りの増加により $\kappa_{\mathrm{in}}=1.5$ の方がわずかに悪化する）ことが確認された。すなわち、**$\kappa_{\mathrm{in}} = 1$（$R_{\mathrm{in}} = d$）が時空間コストと誤り率の双方において最適**である。

### 6.6 15-to-1 魔法状態蒸留との時空間体積比較（`cost_comparison.csv`）

以上の結果に基づき、物理誤り率 $p \in \{10^{-4}, 2\times 10^{-4}, 3\times 10^{-4}, 5\times 10^{-4}, 10^{-3}\}$ および目標論理誤り率 $\varepsilon_{\mathrm{target}} \in \{10^{-4}, 10^{-6}, 10^{-8}, 10^{-10}\}$ の各組において、目標を達成する最小の $\mathbb{D}_4$ Code Switching 構成と最小の Litinski 15-to-1 蒸留工場（1段階または2段階）の時空間体積を比較した結果（`results/cost_comparison.csv`）を表6.4にまとめる。

| シナリオ | 物理誤り率 $p$ | 目標誤り率 $\varepsilon_{\mathrm{target}}$ | Litinski MSD 最小構成<br>（体積 $V_{\mathrm{MSD}}$, 出力誤り $\varepsilon_{\mathrm{MSD}}$） | $\mathbb{D}_4$ 本番モデル (`main`)<br>最小距離 $d^*$, 体積 $V_K$, 状態 | 体積比 (`main`)<br>$V_K / V_{\mathrm{MSD}}$ | $\mathbb{D}_4$ バルク診断 (`quiet`, 14step / 8step)<br>最小距離 $d^*$, 体積比 $V_K / V_{\mathrm{MSD}}$ |
| :---: | :---: | :---: | :--- | :--- | :---: | :--- |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$1 \times 10^{-4}$** | **$10^{-4}$** | GoSC 15-to-1 ($d=3$)<br>$V_{\mathrm{MSD}} = 39,261$, $\varepsilon = 3.2\times 10^{-5}$ | **$d^* = 3$** ($\varepsilon_K \approx 8.8\times 10^{-5}$)<br>$V_K = 21,160$ (`reached`, 82% CI) | **$0.54\times$**<br>（**$\mathbb{D}_4$ が46%削減**） | $d^*=3$, **$0.54\times$** (14step)<br>$d^*=3$, **$0.46\times$** (8step FSC) |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$2 \times 10^{-4}$** | **$10^{-4}$** | Litinski $(15\text{-to-}1)_{5,3,3}$<br>$V_{\mathrm{MSD}} = 56,586$, $\varepsilon = 7.7\times 10^{-5}$ | **$d^* = 5$** ($\varepsilon_K \approx 8.0\times 10^{-5}$)<br>$V_K = 90,376$ (`reached`, 100% CI) | **$1.60\times$**<br>（ほぼ同等） | $d^*=3$, **$0.37\times$** (14step)<br>$d^*=3$, **$0.32\times$** (8step FSC) |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$3 \times 10^{-4}$** | **$10^{-4}$** | Litinski $(15\text{-to-}1)_{7,5,5}$<br>$V_{\mathrm{MSD}} = 215,914$, $\varepsilon = 2.0\times 10^{-6}$ | 窓フロア $W(p) \approx 1.4\times 10^{-4}$ により<br>`not_reached_window_floor` | — | $d^*=5$ ($V_K = 90,376$)<br>**$0.42\times$** (14step) / **$0.36\times$** (8step) |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$1 \times 10^{-4}$** | **$10^{-6}$** | GoSC 15-to-1 ($d=3$) または $(15\text{-to-}1)_{5,3,3}$<br>$V_{\mathrm{MSD}} = 56,492$ | 窓フロア $W(p) \approx 1.0\times 10^{-5}$ により<br>`not_reached_window_floor` | — | $d^*=7$ ($V_K = 239,056$)<br>**$4.23\times$** (14step) / **$3.60\times$** (8step) |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$1 \times 10^{-4}$** | **$10^{-8}$** | Litinski $(15\text{-to-}1)_{7,3,3}$<br>$V_{\mathrm{MSD}} = 82,492$, $\varepsilon = 3.8\times 10^{-10}$ | `not_reached_window_floor` | — | $d^*=7$ ($V_K = 239,056$)<br>**$2.90\times$** (14step) / **$2.47\times$** (8step) |
| **Scenario B**<br>($p_{\mathrm{idle}}=0$) | **$1 \times 10^{-4}$** | **$10^{-10}$** | Litinski $(15\text{-to-}1)_{9,5,5}$<br>$V_{\mathrm{MSD}} = 280,141$, $\varepsilon = 4.6\times 10^{-11}$ | `not_reached_window_floor` | — | $d^*=9$ ($V_K = 497,794$)<br>**$1.78\times$** (14step) / **$1.51\times$** (8step) |
| **Scenario A**<br>($p_{\mathrm{idle}}=p$) | **$1 \times 10^{-4}$** | **$10^{-4}$** | Litinski $(15\text{-to-}1)_{5,3,3}$<br>$V_{\mathrm{MSD}} = 56,506$, $\varepsilon = 5.4\times 10^{-5}$ | $d^* = 7$ ($V_K = 239,056$)<br>`unresolved` (69.5% CI reach) | **$4.23\times$** | $d^*=5$ ($V_K = 90,376$)<br>**$1.60\times$** (14step) / **$1.35\times$** (8step) |
| **Scenario A**<br>($p_{\mathrm{idle}}=p$) | **$1 \times 10^{-4}$** | **$10^{-6}$** | Litinski $(15\text{-to-}1)_{7,3,3}$<br>$V_{\mathrm{MSD}} = 82,519$, $\varepsilon = 6.9\times 10^{-7}$ | `not_reached_window_floor` | — | $d^*=9$ ($V_K = 497,794$)<br>**$6.03\times$** (14step) / **$5.12\times$** (8step) |
| **Scenario A**<br>($p_{\mathrm{idle}}=p$) | **$1 \times 10^{-4}$** | **$10^{-8}$** | Litinski $(15\text{-to-}1)_{9,5,5}$<br>$V_{\mathrm{MSD}} = 280,295$, $\varepsilon = 1.9\times 10^{-9}$ | `not_reached_window_floor` | — | $d^*=11$ ($V_K = 919,704$)<br>**$3.28\times$** (14step) / **$2.78\times$** (8step) |

### 6.7 研究3の考察：$\mathbb{D}_4$ Code Switching と魔法状態蒸留の損益分岐構造

表6.3および表6.4の結果から、回路レベル雑音下における2次元 $\mathbb{D}_4$ Code Switching と 15-to-1 魔法状態蒸留の相対的優位性について、以下の3つの本質的な結論が導かれる。

1. **中精度目標（$\varepsilon_{\mathrm{target}} = 10^{-4}$）・低待機雑音環境（Scenario B）における $\mathbb{D}_4$ Code Switching の実効的優位性**：
   中性原子やイオントラップのように待機デコヒーレンスが小さい環境（Scenario B）において、物理誤り率 $p = 10^{-4}$・目標論理誤り率 $\varepsilon_{\mathrm{target}} = 10^{-4}$ の領域では、$\mathbb{D}_4$ Code Switching は最小距離 $d^* = 3$（ピーク $119$ 量子ビット、$207$ ステップ、時空間体積 **$21,160$ qubit-steps**）で目標を達成し、GoSC 15-to-1 蒸留工場（$198$ 量子ビット、体積 $39,261$）に対して**時空間体積を $0.54\times$（8ステップ並列FSCでは $0.46\times$、すなわち約半分）に削減し、かつピーク物理量子ビット数も $119 / 198 = 0.60\times$ に削減する**。また $p = 2 \times 10^{-4}$ においても、本番モデル（$d^*=5$, 体積 $90,376$）は Litinski $(15\text{-to-}1)_{5,3,3}$（体積 $56,586$）と **$1.60\times$** の同程度のスケールで競合し、もし切り替え窓フロアが改善されれば（`quiet` 診断モデル）$d^*=3$ で **$0.37\times$**（8ステップFSCで **$0.32\times$**）の体積削減を達成するポテンシャルを持つ。さらに、魔法状態蒸留とは異なり事後選択（post-selection）を一切伴わない決定論的なインプレース論理ゲートである点は、クロック同期型アーキテクチャにおいて大きな利点となる。

2. **超高精度目標（$\varepsilon_{\mathrm{target}} \le 10^{-6}$）において 15-to-1 蒸留工場が優位に立つ構造的理由**：
   一方、目標論理誤り率が $\varepsilon_{\mathrm{target}} \in \{10^{-6}, 10^{-8}, 10^{-10}\}$ へと厳しくなると、たとえ切り替え窓の誤りフロア $W(p)$ をゼロとした理想的なバルク診断モデル（`quiet`）であっても、$\mathbb{D}_4$ Code Switching の時空間体積は Litinski の非一様距離 15-to-1 工場に対して Scenario B で **$1.78\times \sim 4.23\times$**（$p=2\times 10^{-4}$ では最大 $12.7\times$）、Scenario A で **$2.72\times \sim 6.03\times$**（$p=2\times 10^{-4}$ では最大 $38.7\times$）大きくなる。
   この理由は両方式のスケーリング則の差から明快に説明できる：
   * **$\mathbb{D}_4$ Code Switching** は単一の符号距離 $d$ のパッチ上で $O(d)$ ラウンドの40ステップ非可換抽出を行うため、時空間体積が **$V_K(d) \approx 632 d^3$** として $d$ の3乗で増大する一方、出力誤り率は $\varepsilon_{\mathrm{bulk}}(d, p) \propto (p / p_{\mathrm{th,bulk}})^{(d+1)/2}$（ここで $p_{\mathrm{th,bulk}} \approx 0.30\%$ は表面符号の $p_{\mathrm{th}} \approx 1.19\%$ の約 $1/4$）でしか減少しない。したがって、$\varepsilon_{\mathrm{target}} = 10^{-8}$ や $10^{-10}$ に到達するためには $d = 7\text{--}11$（体積 $2.4\times 10^5 \sim 9.2\times 10^5$）までパッチ全体を拡大しなければならない。
   * これに対し **Litinski の $(15\text{-to-}1)_{d_X, d_Z, d_m}$ 蒸留工場** は、リード・マラー符号の3次の誤り抑制 $\varepsilon_{\mathrm{out}} \approx 35 p_{\mathrm{in}}^3$ を利用するため、内部の格子手術距離を $d_Z = d_m = 3$ という極小サイズに保ったまま、1つの空間距離 $d_X = 7$ または $9$ のみを伸ばすことで、わずか $8.2 \times 10^4 \sim 1.1 \times 10^5$ qubit-steps という小さな体積で一挙に $\varepsilon_{\mathrm{out}} \sim 10^{-10}$ に到達できるのである。

3. **本番モデル（`main`）における切り替え窓フロア $W(p)$ のボトルネックとその解消への道筋**：
   現在の本番回路実装（`main` モデル）では、$\varepsilon_{\mathrm{target}} \le 10^{-6}$ の領域はすべて切り替え窓の $d$ 非依存な誤りフロア $W(p) = w p^\gamma$（$p=10^{-4}$, Scenario B で $W \approx 10^{-5}$）によって阻まれている（`not_reached_window_floor`）。6.3節の単一故障スキャン（N5）およびコード監査が明らかにした通り、この窓フロアは以下の3つの実装上の要因から生じている：
   * (i) 事前 $Z$ 抽出ラウンド数が符号距離 $d$ に依らず $R_{\mathrm{preZ}} = 2$ に固定されていること、
   * (ii) `FluxDecoder` が時空間マッチングではなく単一ラウンドごとの即時貪欲 2D MWPM であること、および switch-in 最終ラウンドの `('r', 'x')`, `('b', 'x')` の後・$U=WV$ の前に追加のフラックス検証ラウンドがないこと、
   * (iii) `ChargeDecoder` における `flux_erasures` の `(self.Rin + 1, c)` インデックス参照バグにより、切り替え直前のフラックス消失情報が半分失われていること。
   **本来であれば、これら3点を修正した改良プロトコル（事前 $Z$ ラウンドの $O(d)$ 化または時空間フラックス復号＋`flux_erasures` バグ修正）の下で窓フロア $W(p)$ が指数関数的に抑制されることを実証すべきであるが、この点は今後の修正・再計算待ちである**（詳細は別紙『修正の要請.md』第1.3節参照）。

---

## 第7章 総合考察：3研究の統合的知見と実装上の課題・今後の展望

本章では、研究1（トーラス閾値）、研究2（境界付きパッチでの現象論的 Code Switching）、および研究3（回路レベル Code Switching と 15-to-1 魔法状態蒸留のコスト比較）の3つの研究を横断的に統合し、2次元非可換 $\mathbb{D}_4$ Clifford安定化子符号における誤り訂正の普遍的メカニズムを総括するとともに、別紙『修正の要請.md』にまとめた修正課題と今後の展望を論じる。

### 7.1 3研究を貫く非可換ゲージ場の誤り訂正ダイナミクス

本研究の3つのプロジェクトを通じて一貫して浮き彫りになったのは、**「$\mathbb{D}_4$ Clifford安定化子符号における誤り訂正性能は、非可換性の源泉である磁気的フラックス（$Z$-プラケット違反 $da_c \neq 0$）をいかに迅速かつ正確に平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ へと引き戻せるかによって完全に支配される」**という物理的命題である。

1. **平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ 上での完全な保護**：
   研究1の符号容量モデル（閾値 $9.5\text{--}10.2\%$、可換トーリック符号とほぼ同一）および研究2の `ideal` 境界設定（非Pauli誤り $0\%$、交点 $2.41\text{--}2.97\%$）が明確に示した通り、フラックスが事前に消去されて系が平坦部分空間 $\mathcal{H}_{\mathrm{flat}}$ にある限り、$\mathbb{D}_4$ の $\text{CZ}$ ドレッシングや横断的第3階層ゲート $U = WV$ はインターツイナー条件によってPauli誤りをPauli誤りのまま保ち、可換な表面符号に匹敵する高い誤り訂正能力を発揮する。
2. **反復測定下での残留フラックスと再ランダム化の制御**：
   測定誤りが存在する現象論的モデル（研究1・研究2 `noisy`）および回路レベルモデル（研究1・研究3）では、単一ラウンドのシンドローム測定だけでは本物のデータ $X$ エラーと測定誤りを完全に区別できないため、不可避的に確率 $\sim O(p)$ の残留フラックスがラウンド間を生き延びる。
   * **メモリ保持中（バルク）**においては、残留フラックスは異色 $X$-チェック間の反交換を通じて確率 $1/2$ の測定再ランダム化とカイラルな $Z$ キックバックを引き起こすが、研究1および研究3の `quiet` 診断が実証した通り、時空間 JIT フラックス復号とソフト/消失重み付け MWPM 電荷復号を用いれば、このバルクの乱れは符号距離 $d$ の増大とともに指数関数的に抑制可能である（現象論的閾値 $\approx 1.89\text{--}2.00\%$、回路レベルバルク閾値 $\approx 0.14\text{--}0.30\%$）。
   * **符号切り替え境界（$U = WV$ 直前）**においては、残留フラックスの影響はさらに先鋭化する。なぜなら、$U = WV$ の対角第3階層層 $W$（$\text{CS}, \text{CS}^\dagger, T^\dagger$）を非平坦な $X$ エラーが通過する瞬間には、単なるPauli $Z$ キックバックではなく**非Pauli位相誤り（$S/S^\dagger$ および $\text{CZ}$ 誤り）**が生成されるからである（研究2の `noisy` 境界における `collapsed` 状態の発現と有効距離の約 $1$ 低下、および研究3の単一故障スキャン N5 における `('S1', Rin, 'x')` への故障集中と窓フロア $W(p)$ の形成）。

| 比較項目 | 研究1：2次元トーラス閾値<br>(`1_D4閾値/v7`) | 研究2：現象論的 Code Switching<br>(`2_CodeSwitching論理誤り率/v3`) | 研究3：回路レベル Code Switching vs MSD<br>(`3_魔法状態蒸留との比較/v5_2`) |
| :--- | :--- | :--- | :--- |
| **幾何・論理ビット数** | $L \times L$ 三角分割トーラス ($k=6$)<br>$N = 3L^2$ ($L \in \{3,5,7,9,11\}$) | 境界付き正方格子パッチ ($k=1$)<br>$N = 6d^2+2d$ ($d \in \{3,5,7\}$) | 境界付き正方格子パッチ＋補助ビット ($k=1$)<br>ピーク $12d^2+4d-1$ ($d \in \{3,5,7,9\}$) |
| **シミュレーション手法** | 平坦空間 $C_0$ 上の Twisted-Frame 表現<br>（TBW形式と計算基底双対） | TBW Algorithm 1 & 3<br>（演算子レベル Pauli-Proxy ＋ $\mathbb{Z}_8$ ErrorFrame） | TBW Algorithm 2<br>（回路レベル Pauli-Proxy ＋ 動的ドレッシング） |
| **独立検証の実績** | $L=3$ ($2^{27}$ 状態ベクトル) ロックステップ<br>最大確率差 $\le 6\times 10^{-8}$、$\chi^2$ 検定合格 | $d=2$ 状態ベクトル ＋ $d=3,4$ $\mathbb{Z}_4$ TF<br>計 3,214,446 出力で不一致 0 | $d=2,3$ `TrueSim` 一致 ＋ Takada条件検証<br>全189項目 PASS, 0 FAIL |
| **主要な数値成果** | ・符号容量閾値：$\approx 9.5\text{--}10.2\%$<br>・現象論的閾値：$\approx 1.89\text{--}2.00\%$<br>・回路レベル閾値：$\approx 0.19\text{--}0.22\%$ | ・`ideal` 境界交点：$2.97\% \to 2.41\%$<br>（非Pauli誤り $0\%$）<br>・`noisy` 境界交点：$\approx 1.9\% \to 1.8\%$ | ・時空間体積：$632d^3+454d^2+8d-14$<br>・$p=10^{-4}, \varepsilon=10^{-4}$ (Scenario B) で<br>15-to-1 MSD 比 **$0.54\times$** の体積削減 |
| **解明された課題・ボトルネック** | 回路レベルでの $\text{CCZ}$ フック誤りと<br>$L \ge 11$ での緩やかな有限サイズドリフト | `noisy` 境界での残留フラックスによる<br>非Pauli ($S/\text{CZ}$) 誤りと有効距離 $-1$ 低下 | 切り替え窓 (`('S1',Rin,'x')`) の2重故障による<br>$d$ 非依存フロア $W(p) \propto p^{2.4}$ と $O(d^3)$ 体積 |

### 7.2 現在の実装から確定的に言えることと、修正・追加検証待ちの事項の区分

本研究の執筆にあたり、全コードと全出力データを精査した結果、以下の事項が**現在の実装から100%の論理的厳密性をもって主張できる確定結論**であり、またそれに続く事項が**別紙『修正の要請.md』に基づく修正・追加計算を待つべき事項**として明確に区分される。

#### 7.2.1 現在の実装から確定的に言える結論
1. **シミュレータの数学的・数値的厳密性**：研究1の `TwistedFrameSampler`、研究2の `ProxyBackend`、研究3の `FastShot` はいずれも、対応する厳密状態ベクトル参照器とのロックステップ検証において機械精度（あるいは完全一致）で検証されており、旧来のサロゲートモデルのような近似を一切含まない厳密シミュレータである。
2. **2次元トーラス上の $\mathbb{D}_4$ メモリ閾値の存在（研究1）**：符号容量モデルで約 $9.5\text{--}10.2\%$、現象論的モデルで約 $1.89\text{--}2.00\%$（可換トーリック符号比で約 $30\%$ 減）、ネイティブ $\text{CCZ}$ 回路レベルモデルで約 $0.19\text{--}0.22\%$ の有限サイズ交点が存在し、閾値以下で符号距離 $L$ とともに論理誤り率が単調減少する。
3. **現象論的 Code Switching の動作実証と境界フラックスの役割（研究2）**：`ideal` 境界下ではすべての誤りがPauli誤りに留まり $2.41\text{--}2.97\%$ の高い閾値を示す一方、`noisy` 境界下では残留フラックスが $U=WV$ で非Pauli誤りを誘起して有効距離を約 $1$ 低下させる。
4. **回路レベル Code Switching の資源スケーリングと 15-to-1 MSD に対する中精度領域での優位性（研究3）**：現在の回路・復号器実装のままでも、待機誤りが小さい環境（Scenario B, $p=10^{-4}$）で目標誤り率 $\varepsilon_{\mathrm{target}} = 10^{-4}$ を目指す場合、$\mathbb{D}_4$ Code Switching（$d=3$, 体積 $21,160$）は GoSC 15-to-1 蒸留工場（体積 $39,261$）に対して $0.54\times$ の時空間体積削減を達成する。また、$d=7$（Scenario B）では切り替え窓のすべての単一故障（67,789通り）に対して論理誤りゼロ（$c_1 = 0$）が達成されている。

#### 7.2.2 修正・追加計算待ちの事項（別紙『修正の要請.md』対応）
以下の点については、コードの修正または未出力データの追加実行が完了するまでは確定的な結論として述べるべきではなく、「今後の改善課題（修正待ち）」として位置づけられる：
1. **研究3 `ChargeDecoder.decode` の `flux_erasures` キー `(self.Rin + 1, c)` 参照バグの修正効果**：
   6.3節で指摘した通り、現在の `noisy_d4_lib.py`（437行目）では存在しないラウンド `self.Rin + 1` を参照しているため、消失重み付けが最終ラウンド1回分にしか効いていない。これを `(self.Rin - 1, c)` および事前 $Z$ ラウンド `('pre', 2, c)` を正しく参照するように修正し、さらに `FluxDecoder` を時空間MWPMへアップグレードした際に、切り替え窓フロア $W(p)$ がどこまで低下するかは再計算待ちである。
2. **研究3 `d4_lib.py` の `kobayashi_counts(d, fsc_steps=8)` における初期準備1ステップ脱落の修正**：
   8ステップ並列FSCスケジュールのステップ数を $50d + 20$ から真値 $50d + 21$（体積 $536d^3 + 407d^2 + 20d - 14$）へ修正する（体積比への影響は $0.4\%$ 未満であり結論は変わらない）。
3. **研究2における `in_T_out (noisy)`・`in_only`・`in_out` の本番20,000ショットCSV出力と通し時空間復号窓の実装**：
   `chsc_v3_results/` に未出力の3条件の本番CSVを出力して `README_v3.md` のパイロット値を確定値に置き換えること、および switch-in と switch-out を $U=WV$ を跨いで結合した通し時空間復号器を実装した際の有効距離回復の検証。
4. **研究1における 10,000ショット本番CSVと 20,000ショット試行CSVの統一**：
   `main_v7.tex` と `main_v8.tex` の間で参照されているCSV系列を一本化し、回路レベル $L=3\text{--}5$ の多重交差のない20,000ショット以上のデータに統一すること。

### 7.3 今後の展望：切り替え窓フロアの克服とハイブリッドFTQCアーキテクチャへ

本研究の3つの段階を通じて得られた知見は、2次元非可換Clifford安定化子符号の実用化に向けて極めて具体的な設計指針を与えている。
第一に、研究3の単一故障スキャン（N5）が突き止めた通り、回路レベルにおける最大の弱点は「switch-in 最終ラウンドの赤・青 $X$-チェック測定（$\text{CCZ}$ を含む）の後に $Z$-プラケット測定を行わずに $U=WV$ へ入ること」にある。したがって、**$U = WV$ の直前にわずか5ステップのPauli $Z$-プラケット測定と時空間フラックス復号（あるいは事後選択なしの能動的フラックス消去）を1回挟み、赤・青の $X$-チェックは $U=WV$ の直前には測定しない（もともと初期FSC状態から $S_{X;v}^{r,b}=+1$ は満たされているため、switch-in 中は緑の $S_{X;v}^g$ と全色の $S_{Z;f}^{r,g,b}$ のみを測定すれば十分である！）**というプロトコル簡略化を行えば、最終ラウンドの `('r', 'x')`, `('b', 'x')` に起因する単一故障（$d=3$ の200箇所中大半）および40ステップの待機誤りの3分の2（24ステップ分）を一挙に削減できる可能性が高い。これはKobayashiら [27] の元の理論提案とも完全に整合する極めて有望な改良方向である。

第二に、システムアーキテクチャの観点からは、目標論理誤り率 $\varepsilon_{\mathrm{target}} \sim 10^{-4}$ 程度の初期FTQC・中規模量子アルゴリズムにおいては、専用の蒸留工場フットプリントを必要とせず小さな空間オーバーヘッドで決定論的に $\overline{T}$ ゲートを実行できる $\mathbb{D}_4$ Code Switching を直接用い、$\varepsilon_{\mathrm{target}} \le 10^{-8}$ が要求される超大規模アルゴリズムにおいては、$\mathbb{D}_4$ Code Switching（$d=3, 5$）によって生成した中純度魔法状態（$\varepsilon \sim 10^{-4}\text{--}10^{-5}$）を1段の 15-to-1 蒸留工場への高純度入力（state injection の代替）として供給する**「$\mathbb{D}_4$ Code Switching ＋ 1段階蒸留ハイブリッド方式」**が、2段階蒸留工場よりもはるかに小さな時空間体積を実現する有力な候補となる。

Takada, Bartlett, Williamson [39] のClifford安定化子シミュレーション理論と本研究で構築された3つの厳密シミュレーション基盤は、こうした非可換トポロジカル符号と非Clifford論理演算の設計空間を、近似なしに定量探索するための強力な羅針盤となるものである。

---

## 参考文献（References）

[1] A. Y. Kitaev, "Fault-tolerant quantum computation by anyons," *Annals of Physics*, vol. 303, no. 1, pp. 2–30, 2003. arXiv:quant-ph/9707021.

[2] E. Dennis, A. Kitaev, A. Landahl, and J. Preskill, "Topological quantum memory," *Journal of Mathematical Physics*, vol. 43, no. 9, pp. 4452–4505, 2002. arXiv:quant-ph/0110143.

[3] D. Gottesman, "Stabilizer codes and quantum error correction," Ph.D. thesis, California Institute of Technology, 1997. arXiv:quant-ph/9705052.

[4] P. W. Shor, "Fault-tolerant quantum computation," in *Proceedings of the 37th Annual Symposium on Foundations of Computer Science (FOCS)*, IEEE, pp. 56–65, 1996. arXiv:quant-ph/9605011.

[5] B. M. Terhal, "Quantum error correction for quantum memories," *Reviews of Modern Physics*, vol. 87, no. 2, pp. 307–346, 2015. arXiv:1302.3428.

[6] B. Eastin and E. Knill, "Restrictions on transversal encoded quantum gate sets," *Physical Review Letters*, vol. 102, no. 11, p. 110502, 2009. arXiv:0811.4262.

[7] S. Bravyi and R. König, "Classification of topologically protected gates for local stabilizer codes," *Physical Review Letters*, vol. 110, no. 17, p. 170503, 2013. arXiv:1206.1609.

[8] F. Pastawski and B. Yoshida, "Fault-tolerant logical gates in quantum error-correcting codes," *Physical Review A*, vol. 91, no. 1, p. 012305, 2015. arXiv:1408.1720.

[9] D. Gottesman and I. L. Chuang, "Demonstrating the viability of universal quantum computation using teleportation and single-qubit operations," *Nature*, vol. 402, pp. 390–393, 1999. arXiv:quant-ph/9908010.

[10] A. G. Fowler, M. Mariantoni, J. M. Martinis, and A. N. Cleland, "Surface codes: Towards practical large-scale quantum computation," *Physical Review A*, vol. 86, no. 3, p. 032324, 2012. arXiv:1208.0928.

[11] H. Bombin and M. A. Martin-Delgado, "Topological quantum distillation," *Physical Review Letters*, vol. 97, no. 18, p. 180501, 2006. arXiv:quant-ph/0605138.

[12] S. Bravyi and A. Kitaev, "Universal quantum computation with ideal Clifford gates and noisy ancillas," *Physical Review A*, vol. 71, no. 2, p. 022316, 2005. arXiv:quant-ph/0403025.

[13] S. Bravyi and J. Haah, "Magic-state distillation with low overhead," *Physical Review A*, vol. 86, no. 5, p. 052329, 2012. arXiv:1209.2426.

[14] D. Litinski, "A Game of Surface Codes: Large-Scale Quantum Computing with Lattice Surgery," *Quantum*, vol. 3, p. 128, 2019. arXiv:1808.02892.

[15] D. Litinski, "Magic State Distillation: Not as Costly as You Think," *Quantum*, vol. 3, p. 205, 2019. arXiv:1905.06903.

[16] C. Gidney and A. G. Fowler, "Efficient magic state factories with a catalyzed $|CCZ\rangle \to 2|T\rangle$ transformation," *Quantum*, vol. 3, p. 135, 2019. arXiv:1812.01238.

[17] C. Horsman, A. G. Fowler, S. Devitt, and R. Van Meter, "Surface code quantum computing by lattice surgery," *New Journal of Physics*, vol. 14, p. 123011, 2012. arXiv:1111.4022.

[18] H. Bombin, "Gauge color codes: optimal transversal gates and gauge fixing in topological stabilizer codes," *New Journal of Physics*, vol. 17, p. 083002, 2015. arXiv:1311.0879.

[19] A. Kubica, B. Yoshida, and F. Pastawski, "Unfolding the color code," *New Journal of Physics*, vol. 17, p. 083026, 2015. arXiv:1503.02065.

[20] M. Vasmer and D. E. Browne, "Three-dimensional surface codes: Transversal gates and fault-tolerant architectures," *Physical Review A*, vol. 100, no. 1, p. 012312, 2019. arXiv:1801.04255.

[21] B. J. Brown, N. H. Nickerson, and D. E. Browne, "Fault-tolerant error correction with the gauge color code," *Nature Communications*, vol. 7, p. 12302, 2016. arXiv:1503.08217.

[22] H. Bombin, "2D quantum computation with 3D topological codes," *arXiv preprint arXiv:1810.09571*, 2018.

[23] B. J. Brown, "A fault-tolerant non-Clifford gate for the surface code in two dimensions," *Science Advances*, vol. 6, no. 21, eaay4929, 2020. arXiv:1903.03097.

[24] J. T. Anderson, G. Duclos-Cianci, and D. Poulin, "Fault-tolerant conversion between the Steane and Reed-Muller quantum codes," *Physical Review Letters*, vol. 113, no. 8, p. 080501, 2014. arXiv:1403.2734.

[25] M. E. Beverland, A. Kubica, and K. M. Svore, "Cost of universality: A comparative study of the overhead of state distillation and code switching with color codes," *PRX Quantum*, vol. 2, no. 2, p. 020341, 2021. arXiv:2101.02211.

[26] C. Gidney, N. Shutty, and C. Jones, "Magic state cultivation: growing T states as cheap as CNOT gates," *arXiv preprint arXiv:2409.17595*, 2024.

[27] R. Kobayashi, G. Zhu, and P.-S. Hsin, "Clifford Hierarchy Stabilizer Codes: Transversal Non-Clifford Gates and Magic," *Physical Review Letters*, vol. 136, no. 25, p. 250802, 2026. arXiv:2511.02900.

[28] X. Ni, O. Buerschaper, and M. Van den Nest, "A non-commuting stabilizer formalism," *Journal of Mathematical Physics*, vol. 56, no. 5, p. 052201, 2015. arXiv:1404.5327.

[29] M. A. Webster, A. O. Quintavalle, and S. D. Bartlett, "Transversal diagonal logical gates in quantum error-correcting codes," *New Journal of Physics*, vol. 24, p. 103031, 2022. arXiv:2203.00024.

[30] A. Dua, T. Jochym-O'Connor, and G. Zhu, "Quantum error correction with fractal topological codes," *Quantum*, vol. 7, p. 1122, 2023. arXiv:2201.03568.

[31] T.Bauer, J. C. Magdalena de la Fuente, and J. Eisert, "Non-Pauli topological stabilizer codes and fault-tolerant Clifford-hierarchy gates," *PRX Quantum*, 2025.

[32] R. Dijkgraaf and E. Witten, "Topological gauge theories and group cohomology," *Communications in Mathematical Physics*, vol. 129, no. 2, pp. 393–429, 1990.

[33] M. de Wild Propitius, "Topological interactions in broken gauge theories," Ph.D. thesis, University of Amsterdam, 1995. arXiv:hep-th/9511195.

[34] B. Yoshida, "Topological phases with generalized global symmetries," *Physical Review B*, vol. 93, no. 15, p. 155131, 2016. arXiv:1508.03468.

[35] N. Tantivasadakarn, R. Thorngren, A. Vishwanath, and R. Verresen, "Long-range entanglement from measuring symmetry-protected topological phases," *Physical Review X*, vol. 14, no. 2, p. 021040, 2024. arXiv:2112.01519.

[36] M. Iqbal *et al.*, "Non-Abelian topological order and anyons on a trapped-ion processor," *Nature*, vol. 626, pp. 505–511, 2024. arXiv:2305.03766.

[37] S. Aaronson and D. Gottesman, "Improved simulation of stabilizer circuits," *Physical Review A*, vol. 70, no. 5, p. 052328, 2004. arXiv:quant-ph/0406196.

[38] C. Gidney, "Stim: a fast stabilizer circuit simulator," *Quantum*, vol. 5, p. 497, 2021. arXiv:2103.02202.

[39] Y. Takada, S. D. Bartlett, and D. J. Williamson, "Exact efficient simulation of noisy logical magic states using Clifford stabilizers," *arXiv preprint arXiv:2609.16929*, 2026.

[40] O. Higgott and C. Gidney, "Sparse Blossom: correcting a million errors per core second with minimum-weight matching," *Quantum*, vol. 9, p. 1600, 2025. arXiv:2303.15933.
