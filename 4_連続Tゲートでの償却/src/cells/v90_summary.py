n_pass = sum(v['status'] == 'PASS' for v in VAL.values()); n_fail = len(VAL) - n_pass
json.dump(dict(notebook='研究4_validation', quick=QUICK, seed=SEED, results=VAL,
               not_verified=['L >= 3 の真の非 Clifford 回路との照合（状態ベクトルがメモリに入らない。研究 3 と同じ制限）',
                             'S0 を含む全体の厳密照合（V3 は S0 を理想出力＋ランダムな Pauli 誤りで置き換える）',
                             'サイクルの間に論理 H を挟む列（出力の論理安定化子が Clifford でなくなるので、この方法では評価できない）',
                             '全ての測定分岐・全ての故障の列挙（標本化した軌道での照合）']),
          open(f'{OUT_DIR}/validation_study4.json', 'w'), indent=1, ensure_ascii=False)
print(f'{n_pass} PASS, {n_fail} FAIL')
print('VALIDATION PASSED' if n_fail == 0 else 'VALIDATION FAILED')
pd.DataFrame([(k, v['status'], v['detail']) for k, v in VAL.items()], columns=['検査', '結果', '詳細'])
