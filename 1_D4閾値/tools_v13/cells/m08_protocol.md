[Cell 8] Protocol: JIT flux decoder, circuit-level fault tables, X-memory experiment

1 ショット = 以下の物理プロトコルを twisted-frame エンジンで厳密にたどる。
  初期状態: ノイズのない D4 符号状態（logical_colors の x 方向ホロノミー・セクターの等重ね合わせ）
  各ラウンド t = 0..R-1:
    (1) データ雑音（depo/pheno: DEPOLARIZE1(p_data)、CL: idle）
    (2) Z チェック（面、パウリ）を全て測定（測定誤り付き。CL はアンシラ回路の故障込み）
    (3) JIT フラックス復号（色ごとの時空 MWPM・未来境界付き）→ 物理 X 補正を即時適用
    (4) dressed X チェックを色レイヤ順 (r→g→b) に 1 つずつ理想射影測定（測定誤り付き。CL は CCZ 回路の故障込み）
  終了処理（理想化・論文に明記）:
    (5) 完全な Z チェック → 残留フラックスを MWPM で閉じる（物理 X 補正）
    (6) 残留 X フレームがホモロジー的に非自明 → flux 側の論理エラー (fail_flux)。自明なら S のユニタリ作用で除去
    (7) 完全な dressed X チェック 1 ラウンド → 最終シンドローム
  電荷（charge）側の復号: bare MPP 型の Stim 回路の DEM を事前分布として PyMatching で時空 MWPM。
  予測された観測量（path_x_dual のパリティ）と、標準補正を当てた後の状態のセクター位相から
  論理エラーを判定する（忠実度 F、失敗確率 1-F）。
  指標: charge（X スタビライザ側。flux 成功ショットに条件付け）、flux（Z スタビライザ側）、combined（どちらか）。
  対照実験: dressing_treatment = "exact"（D4）/ "none"（dressing なし = 3 枚の Z2 トーリック符号）/
    "kappa_injection"（dressing なし + 旧研究の r=κcp の Z 注入を同じプロトコル内で行う）。
  回路レベル雑音の定義 circuit_noise_preset: "uniform"（研究 3 と同じ。CCZ の後に 3 量子ビット脱分極 D3(p)、
    準備・測定の反転 p、アイドルなし、JIT の X 補正は雑音なし）/ "legacy_v7"（以前の定義）。
    CL の電荷デコーダ事前分布は、実際の（ネイティブ CCZ）回路の故障表から一次の近似で較正する（cl_decoder_prior="calibrated"）。
  JIT の未来境界 jit_future_boundary="auto": 測定誤り 0 なら置かない（全てのフラックスをその場で組にする）。
  診断: dressed X 層の直前に残ったフラックスの数と、フラックスのない層でのランダムな測定結果の割合。
