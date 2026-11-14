[Cell 10] Dense exact reference（JAX; GPU 推奨）と汎用プロトコル・ドライバ

厳密参照: 状態ベクトルをゲージ配位基底で密に持つ。L=3 では平坦配位（選んだ論理セクター）の
座標 t in GF(2)^k（k = 3(L^2-1) + len(logical_colors) = 25 or 27）で psi[t] (float32, 2^k 成分) を保持し、
物理配位 a = M t + x（x: X フレーム）。演算は全て定義通りに作用させる:
  X 誤り:      x_q ^= 1                         （サポートの平行移動）
  Z 誤り:      psi *= (-1)^{a_q}
  dressed X チェック S の測定（depo/pheno）:  (S psi)[t] = psi[t ^ s] * (-1)^{q(a(t ^ s))},
                P(m) = ||(psi + (-1)^m S psi)/2||^2,   psi <- 射影後に規格化
  CL の X チェック: アンシラ 2 分岐 (psi_0, psi_1) を持ち、CX(anc->q) = 分岐 1 の x_q 反転、
                CCZ(anc,q1,q2) = 分岐 1 に (-1)^{a_q1 a_q2}、故障は該当ゲートの直後にそのまま作用、
                最後に H + 測定（分岐 1 を分岐 0 の座標に移して合成）。twisted-frame の故障伝播表とは独立。
  CL の Z チェック: アンシラを配位の関数 (mask, const) として追跡し、ゲート単位で故障を作用。
  故障の位置は故障表の名前（stage）で特定する。"uniform" の CCZ 故障は 3 量子ビット Pauli（63 通り）を
      CCZ の直後に (anc, q1, q2) へそのまま作用させ、"legacy_v7" は 3 量子ビットそれぞれの 1 量子ビット Pauli。
twisted-frame エンジン（アフィン部分空間 + 二次形式）とは独立な実装で、仮定は「全演算が平坦配位の
剰余類 C0 + x を保つ」ことだけ（S のシフトは余境界なので自明に成り立つ）。