# 修正の要請：既存コード・シミュレーション実行結果・既存ドキュメントの点検報告

本ファイルは、作業フォルダ内の3つの研究（① $\mathbb{D}_4$符号の閾値評価、② Code Switchingの論理誤り率・閾値評価、③ 魔法状態蒸留とのコスト比較）に含まれる全てのシミュレーションコード（`.py` / `.ipynb`）、実行結果ファイル（`.csv` / `.json` / `.txt`）、および既存の解説・論文原稿ファイル（`.md` / `.tex`）を精査し、**コードの誤り・復号器やプロトコル実装上の要修正箇所・シミュレーションデータの不足・既存文書（`.md` / `.tex`）の不整合**を体系的にまとめたものである。

ご指示に従い、既存のファイルは一切変更していない。論文下地ファイル（`今までの研究まとめ_論文下地.md`）の執筆にあたっては、本ファイルで指摘した「現在の実装・データからは論理的に導けない事項」を断定せず、現在の実装の前提下で厳密に言える事実のみを記述するか、「本来はこうなるはずだが修正・追加計算待ちである」旨を明記している。

---

## 総括一覧表

| 対象研究 | 区分 | 重要度 | 該当ファイル・関数 | 要修正内容の要約 |
|---|---|---|---|---|
| **研究1（1_D4閾値）** | コード（境界処理） | 中 | `D4_v7_main.ipynb` Cell 8 `_llr()` / `JITFluxDecoder` | 測定誤り率 $p_M=0$（depolarizing＝符号容量型）でも `_llr(0.0)` が有限値 `30.0` を返すため、未来境界へのマッチングが数学的に禁止されていない。 |
| **研究1（1_D4閾値）** | コード（雑音定義） | 中 | `D4_v7_main.ipynb` Cell 8 `build_xcheck_fault_table` / `nb_cl_*_round` | ネイティブCCZ後の雑音が3量子ビット脱分極 $\mathcal{D}_3(p)$ ではなく各量子ビット独立の $\mathcal{D}_1(p)$ 3個（1次故障率 $\approx 3p$）になっている。またアイドル雑音がゲート層ごとではなくラウンド冒頭1回のみ。 |
| **研究1（1_D4閾値）** | コード（旧互換部） | 低 | `D4_v7_main.ipynb` Cell 6 `_effective_per_qubit_round_p` | 旧サロゲート回路用の関数内で、`DEPOLARIZE2(p)` の片側周辺脱分極率が正確な $\frac{4}{5}p$ ではなく $\frac{2}{3}p$ と計算されている（既定の `twisted_frame` 経路には影響しない）。 |
| **研究1（1_D4閾値）** | シミュレーション実行 | 高 | `メインコード実行結果/9までやった(*)` | 本計算のショット数が `10,000` ショット/点にとどまり、circuit-level の $L=3\text{--}5$ で交点が3個に分裂している。また対照実験（`none`, `kappa_injection`）および $L=11$ の本番実行データが未作成（`参考_試行計算/` のみ）。 |
| **研究1（1_D4閾値）** | 正当化コード実行 | 中 | `D4_v7_validation.ipynb` / `正当化コード結果/` | 独立標本による論理誤り率比較（検証C）が1論理色 `logical_colors="r"` のみで実行されており、メイン計算の `logical_colors="rgb"`（3論理色）での大標本比較が未実施。 |
| **研究1（1_D4閾値）** | 既存文書（TeX/MD） | 高 | `paper/main_v7.tex`, `v8_paper/main_v8.tex` | `main_v7.tex` の `\mathbb{1}` 文字化け（`v8` で修正済）、青字プレースホルダと空図枠の残存、交点移動幅に関する記述と試行データの不整合、旧depolarizing注入率の次数正規化条件の記述漏れ。 |
| **研究2（2_CodeSwitching）** | シミュレーション実行 | 高 | `chsc_v3_results/` | `in_T_out` の `switch_in_boundary="ideal"` のみ実行されており、実用性能評価に不可欠な `switch_in_boundary="noisy"`、および切り分け用の `in_only`, `in_out` の本番データ（CSV）が未生成。 |
| **研究2（2_CodeSwitching）** | コード（復号器設計） | 高 | `chsc_switch_v3.py` Cell 6–7 `JITDecoder`, `Decoders`, `ShotRunner` | `switch_in_boundary="noisy"` において、(1) $U$ 直前の最終ラウンドで未来境界が閉じられず単一 $X$ 誤りが高確率で保留されたまま $U$ に突入して非Pauli化する、(2) $U$ の前後で電荷復号窓が分断されている、(3) 緑単発測定 `clean_green_readout` が1層の空間マッチングのみで時間履歴を使っていない。 |
| **研究3（3_蒸留との比較）** | コード（復号器バグ） | **高** | `tools/noisy_d4_lib.py` `ChargeDecoder.flux_erasures`, `D4Experiment.shot` | D4相最終Xラウンド `('S1', Rin, 'x')` のフラックスに対する消失重み付け（`flux_erasures`）において、次ラウンドを存在しない `('S1', Rin+1, 'x')` と参照しているため空間成分の重み緩和が欠落している。また `('S1', Rin+2, 'z')` で補正されたフラックスも `('S1', Rin+1, 'x')` を参照して無視される。これが $d=3, 5$ の単一故障失敗の主因（N5で `('S1', Rin, 'x')` に失敗が集中する原因）となっている。 |
| **研究3（3_蒸留との比較）** | コード（復号モデル） | 高 | `tools/noisy_d4_lib.py` `ChargeDecoder._dem_circuit`, `clifford_x_gadget` | 電荷復号器の事前分布回路（`_dem_circuit`）から非Cliffordゲート（CCZ, CS, $T^\dagger$, NCCZ）とドレッシングが全て除去されており、切り替え窓で $X$ 誤りが $U$ や CCZ を通過して生じる相関 $Z/S/\text{CZ}$ 誤りを復号グラフが表現できていない。また重み6のClifford安定化子測定が補助1量子ビットの非耐故障ガジェットであり、フック誤りと窓の2次誤り床（$W(p)\propto p^{2.4}$）を生む。 |
| **研究3（3_蒸留との比較）** | コード（計数バグ） | 中 | `tools/build_main.py` (`noisy_cost_comparison.ipynb`) `kobayashi_counts` | `fsc_steps=8`（並列FSCスケジュール感度）を指定した際、データ初期化1ステップを含む最初のブロック `('S0', 1)`（本来 $8+1=9$ ステップ）まで一律に `8` ステップで上書きしてしまい、総ステップ数が正しい $50d+21$ ではなく $50d+20$ になっている。 |
| **研究3（3_蒸留との比較）** | コード（関数引数） | 低 | `tools/msd_noisy_lib.py` `surface_code_logical_rate` | `noisy_surface_code(d, rounds, basis, p)` を呼ぶ際に `p_idle` 引数を渡しておらず、常にシナリオA（`p_idle=p`）になる（ノートブック側では直接ループを書いているため実害は回避されているが、ライブラリ関数として修正が必要）。 |
| **研究3（3_蒸留との比較）** | 既存文書（MD/NB） | 中 | `docs/methods.md`, `tools/build_sim.py`, `tools/noisy_d4_lib.py` | `docs/methods.md` §4.1（$50d+21$）、§8（$50d+20$）、§10（$62d+15$）で時間ステップ数の多項式表記が食い違っている。また第3回レビュー対応で削除したはずの「楽観的な限界（optimistic bound）」という表現が `build_sim.py`（`D4_noisy_simulation.ipynb`）と `noisy_d4_lib.py` のコメントに残存している。 |

---

## 1. 研究1（`1_D4閾値/2026-09-27_v7/`）に関する修正の要請

### 1.1 コード・アルゴリズムに関する修正要請

#### (1) `depolarizing`（符号容量型・完全測定）における `JITFluxDecoder` の未来境界コストの上限（Cell 8 `_llr`）
* **現状の実装**: `D4_v7_main.ipynb` Cell 8 の `_llr(p, cap=30.0)` は、`p <= 0.0` のとき無限大ではなく有限値 `30.0` を返す。そのため、`depolarizing` モデル（`p_meas = 0.0`、完全測定）においても、時刻 $t$ のシンドロームを未来境界に繋ぐ辺が重み `w_t = 30.0` で張られる。
* **問題点**: $L=3,5,7,9$ では空間辺の重み $w_s = \ln\frac{1-2p/3}{2p/3} \approx 2.5\text{--}3.4$ に対して双対格子上の距離が最大でも $\lfloor L/2\rfloor \le 4$ であるため、$d_{\text{sep}} w_s < 2 w_t = 60.0$ となり全てのフラックス対が即座に空間マッチングされる。しかし、数学的には未来境界が禁止されていないため、さらに大きな格子サイズや長い $X$ エラー鎖で $d_{\text{sep}} w_s > 60.0$ となると、完全測定であるにもかかわらずフラックスが次ラウンドへ持ち越される。
* **修正案**: `p_meas == 0.0`（あるいは `rounds == 1` の符号容量型）のときは、`JITFluxDecoder` の未来境界辺を追加しない（完全な空間マッチング `FluxCloser` と同等にする）よう分岐を入れること。これにより、論文中の「完全測定下ではJIT復号器が全てのフラックスをdressed測定前に除去する」という主張が任意のサイズ $L$ で厳密に保証される。

#### (2) `circuit_level` におけるネイティブ CCZ 雑音の定義とラウンド単位アイドル雑音（Cell 8 `build_xcheck_fault_table`, `nb_cl_*_round`）
* **現状の実装**:
  1. `build_xcheck_fault_table` において、2量子ビット CX ゲート直後の雑音は 15 個の非恒等 Pauli を等確率 $p/15$ で選ぶ $\mathcal{D}_2(p)$（ゲートあたりの故障確率 $p$）であるのに対し、3量子ビット CCZ ゲート直後の雑音は3個の量子ビット `(0, a, b)` それぞれに独立な1量子ビット脱分極 $\mathcal{D}_1(p)$ を順番に適用している。
  2. `nb_cl_zcheck_round` でラウンド開始時に全データ量子ビットへ `idle_p = 0.4p` の脱分極を1回だけ適用し、直列実行される3色のチェック層（$r \to g \to b$）の待機時間ごとのアイドル雑音は入れていない。
* **問題点**: CCZ 1個あたりに少なくとも1つの非恒等 Pauli 故障が入る確率は $1 - (1-p)^3 = 3p - 3p^2 + p^3 \approx 3p$ となり、パラメータ $p$ の意味が CX ゲート（故障率 $p$）と CCZ ゲート（故障率 $\approx 3p$）で3倍異なっている（研究3の `NoiseModel` では 3量子ビットゲート後に 63 個の非恒等 Pauli を等確率 $p/63$ で選ぶ $\mathcal{D}_3(p)$ を採用しており、研究1と研究3で CCZ 雑音の定義が異なる）。
* **修正案**: 論文下地では現在の実装どおり「CCZ の各量子ビットに独立な $\mathcal{D}_1(p)$ を課すモデル（1次故障率 $3p$）」として正確に記述したが、もし研究3（Takada et al. 準拠の $\mathcal{D}_3(p)$）と定義を統一する場合は、63通りの3量子ビット Pauli チャネルに変更するか、各量子ビットの率を $p/3$ にスケーリングする必要がある。

#### (3) 旧サロゲート互換コード `_effective_per_qubit_round_p` の周辺確率係数（Cell 6）
* **現状の実装**: 旧研究の再現用に残されている `build_circuit_level_x_circuit` 内の `_effective_per_qubit_round_p` で、`DEPOLARIZE2(p)` の1量子ビット周辺脱分極率を `(2.0 / 3.0) * twoq_p` としている。
* **問題点**: 2量子ビット脱分極チャネル $\mathcal{D}_2(p)$ において片方の量子ビットが非恒等（$X, Y, Z$ のいずれか）となる周辺確率は $\frac{12}{15}p = \frac{4}{5}p$（各軸 $\frac{4}{15}p$、したがって $X$ 型または $Z$ 型成分を持つ確率は $\frac{8}{15}p$）である。既定の `engine="twisted_frame"` かつ `cl_decoder_prior="calibrated"` ではこの関数は呼ばれないため現在のメイン結果には一切影響しないが、旧サロゲートとの比較コードとして残す場合はコメント等で近似式である旨を明記すべきである。

### 1.2 シミュレーション実行データに関する修正要請

#### (1) 本番実行（`メインコード実行結果/9までやった(*)`）のショット数増加と対照実験の本番実行
* **現状のデータ**:
  - `メインコード実行結果/9までやった(depo|pheno|cl)/` の CSV・manifest を確認すると、すべて $L \in \{3, 5, 7, 9\}$、**`shots = 10,000`** で実行されている（ノートブック未実行テンプレートの `CFG["shots"] = 100,000` や、`参考_試行計算/` の `shots = 20,000` よりも少ない）。
  - その結果、`9までやった(cl)/d4_v7_X_memory_circuit_level_twisted_frame_crossings.csv` では、$L=3\text{--}5$ の `charge` 交点が統計揺らぎにより **`[0.002042, 0.002328, 0.002355]` の3箇所に分裂**しており（400回のブートストラップ中176回が多重点交差）、`9までやった(depo)` でも $L=7\text{--}9$ の交点が `10.15%`（試行計算では `9.59%`）と揺らいでいる。
  - また、論文の Fig. 4（対照実験：`dressing_treatment="none"` および `"kappa_injection"`）および phenomenological の $L=11$ については、`参考_試行計算/`（20,000ショット、対照実験は $L=3,5,7$）にしかデータが存在せず、`メインコード実行結果/` に対応する本番データが存在しない。
* **修正要請**: 確定版の論文図表を作成するためには、交点近傍に $p$ 範囲を絞った上で `shots = 100,000` 以上の本番計算を実行し、対照実験（`none`, `kappa_injection`）も同じショット数・サイズで揃えて出力する必要がある。

#### (2) 正当化コード（検証C）における `logical_colors="rgb"` での統計比較
* **現状のデータ**: `正当化コード結果/2026-10-02_セル出力完全版.txt` では、ロックステップ試験（検証B）は `r`（30ショット）と `rgb`（10ショット）の両方で全3モデル `PASSED` しているが、独立標本による6点の論理誤り率曲線比較（検証C）は `VCFG["logical_colors"] = "r"`（1論理色）のみで実行されている。
* **修正要請**: メイン計算は `logical_colors = "rgb"`（3論理色）で実行されているため、検証Cについても `rgb` 設定での比較ログを残すか、あるいは論文本文で「検証Cは $k=25$（単一論理色 `r`）で実施し、3論理色 `rgb`（$k=27$）についてはロックステップ試験（検証B）で確率・忠実度の厳密一致を確認した」と正確に書き分ける必要がある（論文下地では後者の正確な記述を採用した）。

### 1.3 既存の論文原稿（`main_v7.tex`, `main_v8.tex`）および解説MDの修正要請

1. **数式表示の不具合（`main_v7.tex`）**: `main_v7.tex` の式(28)で指示関数に `\mathbb{1}` を使用しているため、`amssymb` の仕様により `2026_09_27_v7.pdf` で数字の `1` が文字化けしている。`v8_paper/main_v8.tex` では `\usepackage{dsfont}` と `\mathds{1}` により修正済みであるため、以降は必ず `v8` 側をベースとすること。
2. **プレースホルダと試行計算値の残存（`main_v8.tex`）**: `main_v8.tex` の Abstract、Sec. 6（Validation）、Sec. 7（Results）、Table 1、および Fig. 2〜4 がすべて青字の試行計算値または `[Insert ...]` の空枠のままになっている。特に Sec. 6 の検証数値は `正当化コード結果/2026-10-02_セル出力完全版.txt` の確定値（最大確率差：depol $1.12\times 10^{-8}$、pheno $1.86\times 10^{-9}$、CL $5.96\times 10^{-8}$；最大忠実度差：全モデル $1.19\times 10^{-7}$；$\sum z^2$（charge）：depol $1.46\ (p=0.962)$、pheno $6.49\ (p=0.371)$、CL $7.24\ (p=0.299)$）で埋めることができる。
3. **交点のドリフト幅に関する記述の不整合（`main_v8.tex` Sec. 7）**: `main_v8.tex` Sec. 7 に「$L$ が増えるにつれて減少するステップ幅で低 $p$ 側へ移動する（move to lower $p$ as $L$ grows, with decreasing steps）」とあるが、Table 1 に記載されている試行計算値では phenomenological が $2.25\% \to 2.12\% \to 1.96\%$（差 $-0.13\%$ のち $-0.16\%$）、circuit-level が $0.221\% \to 0.211\% \to 0.193\%$（差 $-0.010\%$ のち $-0.018\%$）であり、$5\text{--}7$ から $7\text{--}9$ への移動幅の方が大きくなっている（ただし `9までやった(pheno)` の1万ショット結果では $2.247\% \to 2.088\% \to 1.998\%$ で差 $-0.159\%$ のち $-0.090\%$ となり減少している）。データと記述を一致させる必要がある。
4. **状態表現の位相に関する記述の厳密化（`main_v8.tex` Abstract, Sec. 4）**: Abstract で状態を「二次位相で重み付けされた平坦ゲージ配位のアフィン部分空間上の一様重ね合わせ」と述べているが、実際には初期符号状態の3次（cubic）の Dijkgraaf–Witten ツイスト位相 $\phi_0(b)$ に**追加される相対位相** $Q(b)$ が二次形式である（$\psi(a) = (-1)^{\phi_0(a+x)+Q(a+x)}\mathds{1}[a+x\in B]$）。誤解を避けるため「初期符号状態のツイスト位相 $\phi_0$ に対する追加位相 $Q$ が $\mathbb{F}_2$ 上の二次形式に保たれる」と明記すべきである。
5. **条件付き指標 $P_{\mathrm{charge}}$ と符号全体の閾値の区別**: 主指標 $P_{\mathrm{charge}} = \Pr(\text{charge failure} \mid \text{flux success})$ はフラックス側が成功した試行に条件付けた確率であり、また1方向のホロノミー3色（8セクター）のみを初期状態に選んでいる。これを無条件の「$\mathbb{D}_4$符号全体の漸近閾値」と混同しないよう、必ず $P_{\mathrm{flux}}$ および $P_{\mathrm{comb}}$ を併記し、「指定プロトコル・復号器下での条件付き $X$-スタビライザ（電荷セクター）有限サイズ交点」と定義を明記する必要がある。

---

## 2. 研究2（`2_CodeSwitching論理誤り率/2026-10-20_エラー率v3/`）に関する修正の要請

### 2.1 シミュレーション実行データに関する修正要請

#### (1) `switch_in_boundary="noisy"` および `in_only`, `in_out` の本番実行データの欠如（`chsc_v3_results/`）
* **現状のデータ**: `chsc_v3_results/` フォルダ内には、`chsc_v3_in_T_out_ideal.csv`（およびその図・交点・manifest）の1条件しか保存されていない。
* **問題点**: `README_v3.md` の §2 で詳しく論じられているとおり、`switch_in_boundary="ideal"` は論理ゲート $U = WV$ の直前に「無雑音の面 $Z$ 測定＋無雑音の dressed $X$ 測定＋完全なフラックス閉鎖と電荷後始末」を挿入する理想化ベンチマークである。この設定では、**$U$ に突入する時点でデータ上に未補正の $X$ 誤り（フラックス）や緑電荷が一切残らない**ため、Code Switching 固有の物理的コストである「残留 $X$ 誤りが非Clifford層 $W$（$\text{CS}, T^\dagger$）を通過して $S/\text{CZ}$ 型の非Pauli誤りに変換される現象（論理状態の `collapsed` や `S` クラスの発生）」が構造的にゼロになる（実際、`chsc_v3_in_T_out_ideal.csv` では全24行で `n_S = 0`, `n_collapsed = 0`, `n_flux_D4 = 0` である）。
* **修正要請**: `CHSC_switch_v3_main.ipynb`（または `chsc_switch_v3.py`）において、`CFG["cases_to_run"] = ["in_only", "in_out", "in_T_out"]` かつ `CFG["boundaries_to_run"] = ["ideal", "noisy"]` を設定して実行し、`ideal` と `noisy` の比較データおよび3ケースの切り分けデータを `chsc_v3_results/` に揃える必要がある（論文下地では、`chsc_v3_results/` の `ideal` 本番データと、`README_v3.md` §2.2 に記録された `noisy` 試行データおよび `正当化コードセル出力.txt` の `noisy` 検証データを厳密に区別して記述した）。

### 2.2 コード・復号器設計に関する修正要請（`chsc_switch_v3.py`）

#### (1) `switch_in_boundary="noisy"` における $U$ 前後の復号窓の分断と JIT 未来境界の扱い（Cell 6–7 `Decoders`, `ShotRunner.run`）
* **現状の実装**:
  1. `JITDecoder` は switch-in の最終ラウンド $t = R_{\text{in}}-1$ においても、重み `offset * w_t = w_t` の未来境界辺を持ったままマッチングを行う。phenomenological 雑音では $p_X = \frac{2}{3}p < p_M = p$ のため $w_s = \ln\frac{1-2p/3}{2p/3} > w_t = \ln\frac{1-p}{p}$ となり、最終ラウンドで発生した境界上の単一 $X$ 誤りや重み2の内部 $X$ 誤りは、空間辺でペアリングされるよりも未来境界へ逃がす方が必ず低コストになる。そのため、最終ラウンドの $X$ 誤りは補正されずに保留されたまま非Cliffordゲート $U = WV$ に突入する。
  2. 電荷（dressed $X$ チェック）の復号において、switch-in 終了時（$U$ の直前）に `cin_rb`（未来境界重み $w_t$ 付き）で一度硬判定の $Z$ 補正 `z_in` を適用してシンドローム履歴をリセットし、switch-out 後の表面符号ラウンド（`out_chg`）を全く別の復号窓として復号している。
  3. さらに `cin_rb` および `cin_g` では、フラックスが存在したラウンドで dressed $X$ 測定が確率 $1/2$ にランダム化されることに対する重み緩和（研究3の `flux_erasures` に相当する処理）が行われていない。
* **問題点**: `switch_in_boundary="noisy"` での論理誤り率の大幅な悪化（有効距離が約1低下し、交点が `ideal` の約 $3.0\%/2.4\%$ から約 $1.9\%/1.8\%$ へ低下する現象）には、「$U$ 直前に無雑音測定を置かないことによる本来の物理的コスト」だけでなく、「$U$ の前後で復号窓を人為的に分断していることによる復号器起因の損失」が混入している。
* **修正要請**: 赤・青の電荷シンドローム（および $V$ によって $e_g \to e_{rgb}$ に写される緑の電荷シンドローム）を $U$ と switch-out をまたいで単一の時空間マッチンググラフで一括復号する「通しの時空間復号器（cross-$U$ unified window decoder）」へ改良することが望ましい。これが完成するまでは、`noisy` の数値は「窓分断型復号器による悲観側の上界（保守的ベンチマーク）」として位置づける必要がある。

#### (2) Switch-out における単発 $Z^g$ 読み出しの空間単独復号（Cell 6–7 `clean_green_readout`）
* **現状の実装**: `ShotRunner.run` の switch-out ステップでは、緑量子ビットの単発 $Z^g$ 測定結果 `raw`（測定反転率 $p$ を含む）に対し、`dec.clean_green_readout(raw)` を呼んで **1層のみの2次元空間マッチング（`sp_flux_g`）** で面シンドロームを消し、そこから $\lambda$ を求めて $S_X^g(\lambda)$（$\text{CZ}^{r,b}$ を含む）を作用させている。
* **問題点**: 直前の switch-in 最終ラウンドの緑面シンドロームとの時間相関を使っていないため、単発の $Z^g$ 測定誤りと実際の $X^g$ データ誤りを区別できず、誤った $S_X^g(\lambda)$ の適用によって赤・青データ上に相関した $\text{CZ}^{r,b}$ 誤りを注入してしまう。研究3（`noisy_d4_lib.py` の `FluxDecoder`）では switch-out の $Z^g$ 読み出しを S1 の緑フラックス時空間グラフと結合して復号する実装（`so_rel`）が導入されているため、研究2にも同様の時空間結合復号を導入すべきである。

---

## 3. 研究3（`3_魔法状態蒸留との比較/2026-10-29_コスト評価v5_2/`）に関する修正の要請

### 3.1 コード・復号器に関する修正要請

#### (1) 【重要】`ChargeDecoder.flux_erasures` および `D4Experiment.shot` における最終D4ラウンドのブロック名参照バグ（`tools/noisy_d4_lib.py` 695–714行目、788行目）
* **現状の実装**:
  `D4SwitchingCircuit._blocks()`（443–447行目）では、D4相（S1）のブロックは $r = 1, \dots, R_{\text{in}}$ について `('S1', r, 'z')` と `('S1', r, 'x')` が交互に並び、その後 $U$ の直前に `n_pre_u = 2` 回の Z 検査のみのブロック `('S1', Rin + 1, 'z')` と `('S1', Rin + 2, 'z')` が置かれる（したがって **`('S1', Rin + 1, 'x')` というブロックは存在しない**）。
  ところが、`D4Experiment.shot`（786–788行目）および `ChargeDecoder.flux_erasures`（694–714行目）は以下の実装になっている：
  ```python
  # D4Experiment.shot (786-788行目):
  if nm[0] == 'S1':
      # the flux was present during the X-type round preceding this Z round
      flux_events += [(q, nm[1] - 1) for q in corr if nm[1] >= 2]
  ```
  ```python
  # ChargeDecoder.flux_erasures (694-714行目):
  for q, r in flux_events:
      blk = ('S1', r, 'x')
      nxt = ('S1', r + 1, 'x')
      for lab, partner in self._cz_of.get(q, []):
          m = self.meas_idx.get((blk, lab))
          if m is None:
              continue
          dd = tuple(sorted(self.dets_of_meas.get(m, [])))
          if 1 <= len(dd) <= 2 and dd in self.comp_index:
              er.add(self.comp_index[dd])
          # space-like component: Z on the partner flips the two stars containing it
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
  ```
* **問題点（3つの連鎖的欠陥）**:
  1. **空間成分の次ラウンド参照ミス**: D4相の最後のX検査ラウンド `('S1', Rin, 'x')`（$r = R_{\text{in}}$）に存在したフラックスが直後の `('S1', Rin + 1, 'z')` で補正された場合、`flux_events` には `(q, Rin)` が入る。しかし `flux_erasures` 内で `nxt = ('S1', Rin + 1, 'x')` と置いているため、`self.meas_idx.get((nxt, l2))` は常に `None` になる（実際の次のX検査ラウンドは switch-out 後の **`('S4', 1)`** である！）。その結果、`('S1', Rin, 'x')` の後半の可換クラスで CCZ ドレッシングにより `partner` 量子ビットに蹴り出された $Z$ 誤り（`('S4', 1)` の検出器で初めて検出される空間成分）の重みが全く緩和されない。
  2. **時間成分の次数フィルタによる脱落**: $r = R_{\text{in}}$（`blk = ('S1', Rin, 'x')`）の測定 `m` は、直前のラウンドとの検出器 `(Rin - 1, Rin)` だけでなく、`('S4', 1)` の switch-out 境界検出器（`first[lab]`）の複数個に同時に含まれるため、緑チェックや `aligned=True` の赤チェックでは `len(self.dets_of_meas[m])` が **3以上** になる。その結果、`if 1 <= len(dd) <= 2` の条件で弾かれ、最終ラウンド `('S1', Rin, 'x')` の測定ランダム化に対する時間辺の重み緩和もスキップされてしまう。
  3. **2回目の pre-$U$ Zラウンドで補正されたフラックスの無視**: `('S1', Rin, 'x')` に存在したフラックスが、`('S1', Rin + 1, 'z')` の測定誤り等によって2回目の pre-$U$ Zラウンド `('S1', Rin + 2, 'z')`（`flush=True`）で補正された場合、`nm[1] - 1` は `Rin + 1` となり、`flux_events` に `(q, Rin + 1)` が登録される。すると `flux_erasures` は存在しない `blk = ('S1', Rin + 1, 'x')` を参照して `m = None` で即座に `continue` してしまい、`('S1', Rin, 'x')` でのランダム化が完全に無視される。
* **数値結果との対応（N5 単一故障スキャンの説明）**:
  `results/validation.json` の N5（単一故障全列挙）を見ると、単一故障による論理失敗は、
  - $d=3$ シナリオB：全180件中 **136件（75.6%）が `('S1', 3, 'x')`**（すなわち $r = R_{\text{in}}$）に集中
  - $d=3$ シナリオA：全275件中 **200件（72.7%）が `('S1', 3, 'x')`** に集中
  - $d=5$ シナリオB（窓全列挙）：**全11件中 11件すべて（100%）が `('S1', 5, 'x')`**（$r = R_{\text{in}}$）に集中
  している。なぜ途中のラウンド `('S1', 1..Rin-1, 'x')` では単一故障がほぼ完全に訂正されるのに、最終ラウンド `('S1', Rin, 'x')` だけで単一故障が大量に失敗するのかという直接の原因が、上記の `flux_erasures` の境界参照バグにある。
* **修正要請**:
  1. `D4Experiment.shot` の788行目で、`nm[1] > Rin`（pre-$U$ の追加Zラウンド）で補正されたフラックスについても `min(nm[1] - 1, circ.Rin)` として `('S1', Rin, 'x')` に帰属させること。
  2. `ChargeDecoder.flux_erasures` において、`r == circ.Rin` のときの次ラウンド `nxt` を `('S4', 1)` に接続し、また時間辺の検索も `self.dets_of_meas[m]` 全体ではなくラウンド間の2点検出器（または `S4` との境界検出器）を個別に特定して重み緩和を行うよう修正すること。

#### (2) 切り替え窓における非Clifford誤り伝播の復号モデルへの未反映と非耐故障ガジェット（`tools/noisy_d4_lib.py` `_dem_circuit`, `clifford_x_gadget`）
* **現状の実装**:
  1. `ChargeDecoder._dem_circuit` は `cm.base`（Cliffordゲートのみ）から Stim の DEM を生成しており、`cm.nonc`（`CCZ`, `CS`, `CSDG`, `TDG`, `NCCZ`）を通過する $X$ 誤りが生成するドレッシング（$S, Z, \text{CZ}$）を DEM に一切含めていない。
  2. そのため、`('S1', Rin + 2, 'z')` の CNOT 層以降や `('U',)` で発生した $X$ 誤りが $U = WV$ を通過して生じる $S/\text{CZ}$ 誤りや、switch-out の `NCCZ` を通過して生じる相関 $Z$ 誤りが `ChargeDecoder` のマッチンググラフに存在せず、$d=7, 9$ でも減少しない2次以上の窓の誤り床（$W(p) \propto p^{2.4}$）を生んでいる。
  3. また、D4相の重み6のClifford安定化子測定（`clifford_x_gadget`）が単一補助量子ビットによる非耐故障回路であるため、補助量子ビット上の単一故障が複数のデータ量子ビットへフック誤りとして伝播する。
* **修正要請**: 本研究のコスト比較における「要求誤り $10^{-6}$ 以下で Kobayashi 方式が目標に届かない」という結果は、Kobayashi–Zhu–Hsin プロトコル自体の理論的限界ではなく、上記の切り替え窓の復号・ガジェット実装に起因する窓の誤り床 $W(p)$ によるものである。論文下地ではこの点を明確に区別して論じたが、将来的に Kobayashi 方式の真の漸近性能を評価するためには、(a) 上記(1)の `flux_erasures` バグの修正、(b) $U$ 直前の残留フラックスと switch-out を統合した相関復号（または Belief Propagation + OSD 等のハイパーエッジ対応復号器）、(c) 重み6ガジェットへの flag 量子ビットの導入、の3点を実施して再計算する必要がある。

#### (3) `kobayashi_counts(d, fsc_steps=8)` における `('S0', 1)` のデータ初期化ステップ脱落バグ（`tools/build_main.py` 253–267行目）
* **現状の実装**:
  `noisy_cost_comparison.ipynb`（`tools/build_main.py`）の II-3 節にある `kobayashi_counts(d, fsc_steps=None)` は、`fsc_steps=8` が渡された際、`code_ == 'FSC'` である全てのブロックのステップ数を一律に `n_steps = fsc_steps`（$= 8$）に置き換えている。
* **問題点**:
  `D4SwitchingCircuit._blocks()`（441–442行目）において、最初のブロック `('S0', 1)` には FSC のシンドローム測定（14ステップ、並列版では8ステップ）の前に、**データ量子ビットを $|+\rangle$ に初期化する1ステップ `pre = [[('RX', q) for q in rb]]` が含まれている**（そのため `fsc_steps=None` のとき `block_steps(circ, ('S0', 1))` は `15` を返し、総ステップ数は $15 + 14(d-1) + (34d+13) + 5 + 2 + 14d = 62d + 21$ となる）。
  ところが、`fsc_steps=8` を指定すると、`('S0', 1)` まで `9`（$= 1 + 8$）ではなく `8` に上書きされてしまい、データ初期化の1ステップが消滅して総ステップ数が **$50d + 20$**（正しくは **$50d + 21$**）となり、時空間体積 `kobayashi_diag_volume_fsc8` も $|\text{active}_{\text{FSC}}| = 9d^2 + 4d - 1$ だけ過小評価されている。
* **修正案**: `kobayashi_counts` 内の `n_steps` 計算を以下のように修正すること：
  ```python
  extra_init = 1 if blk['name'] == ('S0', 1) else 0
  n_steps = block_steps(circ, blk) if (fsc_steps is None or code_ != 'FSC' or blk['name'][0] == 'FIN') else (fsc_steps + extra_init)
  ```

#### (4) `tools/msd_noisy_lib.py` の `surface_code_logical_rate` における `p_idle` 引数の欠落（240–250行目）
* **現状の実装**: `surface_code_logical_rate(d, p, shots, rounds=None, seed=0)` が内部で `noisy_surface_code(d, rounds, basis, p)` を呼ぶ際、`p_idle` を受け渡していない（そのため常に `p_idle = p` となる）。
* **修正案**: `D4_noisy_simulation.ipynb` の較正セルではこの関数を呼ばずに直接 `noisy_surface_code(..., p_idle=f * p)` をループしているため保存済みデータ（`surface_code_plog.csv`）に誤りはないが、ライブラリ関数の整合性のため `p_idle=None` 引数を追加して `noisy_surface_code(d, rounds, basis, p, p_idle=p_idle)` に渡すよう修正すること。

### 3.2 既存ドキュメント（`docs/methods.md`, ノートブック説明文）の修正要請

1. **時間ステップ数多項式の記述不整合（`docs/methods.md`）**:
   - `docs/methods.md` §4.1（p. 3）では「時間ステップ数 $62d+21$（...）。FSC を 8 ステップで数えると $50d+21$」と書かれている。
   - 同 §8（p. 6）では「FSC を 8 ステップで数えると時間 $50d+20$、体積 $536d^3+398d^2+16d-13$」と書かれている（上記 3.1(3) の1ステップ脱落バグの値が転記されている；正しくは時間 $50d+21$、体積 $536d^3+407d^2+20d-14$）。
   - 同 §10 の表 P0-4 欄（p. 7）では、v5.1 時点（`n_pre_u=1` のとき）の「時間は $62d+15$ に変わった（以前 $62d+16$）」という記述が更新されずに残っている（v5.2 で `n_pre_u=2` に増やしたため 6 ステップ増えて $62d+21$ になっている）。
2. **「楽観的な限界（optimistic bound）」という表現の残存（`tools/build_sim.py`, `tools/noisy_d4_lib.py`）**:
   - `docs/methods.md` §10 の「6.1」欄において、第3回レビューの指摘（「`quiet` は最適復号器の下界ではない；『楽観的な限界』の表現を削除」）を受けて `docs/methods.md` と `noisy_cost_comparison.ipynb` からは当該表現が削除された。
   - しかし、`D4_noisy_simulation.ipynb`（生成元 `tools/build_sim.py` 41行目）の解説文には「この窓の扱いを理想化したときの**楽観的な限界を与える**」という文言がそのまま残っており、`tools/noisy_d4_lib.py` 739行目のコメントにも `Gives an optimistic bound.` が残っている。これらも「同じ復号器で窓の雑音を除いた診断値（最適復号器の限界ではない）」に統一する必要がある。
