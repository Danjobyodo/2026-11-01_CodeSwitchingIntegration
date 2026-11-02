# 研究 2：CHSC code switching の論理誤り率 v9

作成日：2026-11-02（Claude）。版番号は 3 研究で 9 に統一した（研究 2 は v3 → v9。v4〜v8 は存在しない）。

方法（Pauli proxy 法、厳密性の条件 C1–C3、復号器、$d$ の意味）は **[`methods_v9.md`](methods_v9.md)** に、このフォルダだけで読めるようにまとめた（v3 までは作業フォルダにない v2 の README を参照していた：R2-2）。

## 0. ファイル

| ファイル | 内容 |
|---|---|
| `CHSC_switch_v9_main.ipynb` | メインの計算（Colab の CPU ランタイム。GPU 不要）。**既定の CFG は本番用**（3 ケース × ideal/noisy、$d=3,5,7$、20,000 ショット/点） |
| `CHSC_switch_v9_validation.ipynb` | 正当化（総当たり・v1 エンジン・本番経路の再生、最後に合否判定。CPU で約 2 分） |
| `chsc_switch_v9.py` / `chsc_validation_v9.py` | 上の 2 つと同じコード（.py 版。ノートブックはここから `make_notebooks_v9.py` で生成） |
| `methods_v9.md` | 方法・厳密性・復号器（論文の手法の節の下地） |
| `v9_検証ログ/` | 手元で実行した v9 の正当化の全ログと CSV、noisy の復号器の比較（試行計算） |
| `*_v3.*`, `chsc_v3_results/` | v3 のコードと本番データ（`in_T_out`・ideal）。**v9 の ideal は v3 と同じ標本・同じ判定を与える**ので、この本番データは v9 の ideal の値としてそのまま使える |

## 1. v3 からの変更点

| # | 変更 | 理由 |
|---|---|---|
| 1 | `switch_in_boundary="noisy"` で、**$U$ をまたいで復号を続ける**（`noisy_decoder="joint"`、既定）：$U$ の時点で JIT に保留されたフラックスを switch-out の $Z^g$ 読み出し（緑）・表面符号の $Z$ ラウンド（赤青）と、赤青の電荷を switch-in の dressed ラウンドと表面符号のラウンドと、それぞれ 1 つの時空グラフで復号する | Gemini の修正要請 2.2(1)(2)（$U$ の前後で復号窓が切れている、緑の単発読み出しが時間の履歴を使っていない）。研究 3 の復号器（全ラウンドを 1 つのグラフで扱う）と原理をそろえた。試行計算で v3 の noisy より $P_L$ が 1–2 割下がった（`methods_v9.md` §4.3） |
| 2 | 研究 3 の「$U$ 直前の $Z$ だけのラウンド」を `n_pre_u` として追加（**既定 0**） | 研究 3 との統一を検討したが、現象論的雑音では $P_L$ が 2–3 倍に悪化したので既定にはしなかった（`methods_v9.md` §4.3）。旧版（v3）の方が良い設定を誤って捨てないため |
| 3 | 既定の CFG を本番用にした（`cases_to_run=["in_only","in_out","in_T_out"]`, `boundaries_to_run=["ideal","noisy"]`） | R2-1（noisy と in_only・in_out の本番が無かった） |
| 4 | 出力名を `chsc_v9_*`、出力先を `chsc_v9_results/` に。CSV に `n_pre_u`, `noisy_decoder` 列、計算条件のキーに `n_pre_u`, `noisy_decoder` を追加 | v3 の CSV と混ざらないように |
| 5 | 正当化で `noisy_preu2`（`n_pre_u=2` の経路）も検査 | 任意の経路も正しくシミュレーションされていることの確認 |
| 6 | `methods_v9.md` を新しく作成：方法の説明（R2-2）、JIT が研究 1 と少し違うこと（R2-5）、$d$ はパッチの大きさで実効距離の主張はしないこと（R2-4） | |

**変えていないもの**：Pauli proxy エンジン（v2 以降同じ）、幾何、雑音モデル、`ideal` の手順と復号器。同じ seed なら `ideal` は v3 と全ショット一致し、`noisy_decoder="split_v3", n_pre_u=0` の `noisy` も v3 と全ショット一致することを確認した（$d=3$、3 ケース）。

## 2. ideal と noisy の意味（v9）

* `ideal`：$U$ の直前に雑音なしの $Z$ 検査と dressed $X$ 検査を 1 ラウンド置き、完全なシンドロームでフラックスを閉じ電荷を後始末する。switch-in と switch-out 以降を $U$ の位置で理想的に切り離した基準（楽観側）。残った誤りが $U$ を通る効果は構造的に 0 になる（v3 の本番で $S$ 型・collapsed が全点 0）。
* `noisy`：完全ラウンドなし。残った $X$ 誤りは $W$（CS, $T^\dagger$）を通って S・CZ 型の誤りになり、緑の電荷は $V$ で $e_g\to e_{rgb}$ と広がる。これは code switching 方式そのもののコスト。v9 では $U$ をまたいで復号を続けるので、v3 の noisy にあった「窓を切ることによる損失」の一部（フラックスと赤青の電荷）は除かれた。緑の電荷は $U$ の前に後始末したままで、その残りは $V$ で赤青の電荷になり、表面符号の側で見える。
* 実用性の議論には `noisy` を使う。`ideal` と並べることで「$U$ を挟むことのコスト」を見積もる。

## 3. 正当化の結果（手元の CPU、`v9_検証ログ/`、約 2 分）

| 検査 | 内容 | 結果 |
|---|---|---|
| 自己診断 | $d=3,5,7$：平坦部分空間での可換性（演算子として非可換な対 12, 48, 108、平坦部分空間では 0）、$U=T^\dagger$、C1–C3 の違反 0、$p=0$ で 3 ケースとも $P_L=0$、最終状態が符号空間 | すべて合格 |
| $U$ の総当たり | $d=2$ | $c_1/c_0=e^{-i\pi/4}$（$T^\dagger$） |
| 参照 1：総当たり（ロックステップ） | $d=2$、3 ケース × ideal/noisy/noisy_preu2 × 4 $p$ × 150 | 5,400 ショット、683,004 出力、**不一致 0** |
| 参照 2：v1 エンジン（ロックステップ） | $d=3,4$、同上 × 100 | 7,200 ショット、4,069,644 出力、**不一致 0** |
| 参照 3：本番経路の再生 | $d=2$、同上 × 50 | 1,800 ショット、227,640 出力、**不一致 0** |
| 合否判定 | `assert_validation` | **VALIDATION PASSED** |

## 4. 本番の実行（未実行。R2-1）

`CHSC_switch_v9_main.ipynb` を上から実行すると、3 ケース × ideal/noisy × $d=3,5,7$ × 8 点 × 20,000 ショットを計算する（`ideal` の `in_T_out` は v3 の本番と同じ値になる）。1 ショットの時間は手元の CPU で $d=3,5$ が約 2、6 ms、v3 の Colab の本番で $d=7$ が 23–59 ms（$p$ が大きいほど長い）なので、全体で十数時間。Colab では `cases_to_run`・`boundaries_to_run`・`d_values` を分けて実行し、終わるたびに `chsc_v9_results/` を保存する（同じ条件なら同じ CSV に追記される）。両方の境界を計算すると比較図 `chsc_v9_ideal_vs_noisy.png` ができる。交点付近の統計を増やす場合や $d=9$ を加える場合は、別の `out_dir`（と別の seed）を使う。

## 5. CFG の主なキー（v3 からの差分）

| キー | 意味（既定値） |
|---|---|
| `cases_to_run` | `["in_only","in_out","in_T_out"]`（None なら `case` だけ） |
| `boundaries_to_run` | `["ideal","noisy"]`（None なら `switch_in_boundary` だけ） |
| `noisy_decoder` | `"joint"`（v9：$U$ をまたいで通しで復号）/ `"split_v3"`（v3 と同じ） |
| `n_pre_u` | `0`（noisy のみ：$U$ の直前の $Z$ だけのラウンドの数。研究 3 は 2） |
| `out_dir` | `chsc_v9_results` |

その他のキー（`rounds_in`, `rounds_out`, `x_check_order`, `jit_boundary_offset`, `green_noise_after_switch_out`, `resume`, `seed` など）は v3 と同じ。
