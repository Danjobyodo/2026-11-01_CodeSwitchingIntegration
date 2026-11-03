[Cell 6] Circuit-Level Engine（旧研究のサロゲート回路）

旧研究の集約モデル。v7 では `engine="stim_surrogate"`（旧手法の再現）と `cl_decoder_prior="legacy"`（v6 と同じ事前分布）でだけ使います。旧研究のモデルを再現するため、中の式（2 量子ビット雑音の周辺確率の近似など）は旧研究のままにしています。