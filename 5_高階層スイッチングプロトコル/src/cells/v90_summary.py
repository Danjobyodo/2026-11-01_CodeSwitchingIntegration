# ==================================================================================================
# まとめ
# ==================================================================================================
SUMMARY = pd.DataFrame(CHECKS)
display(SUMMARY)
json.dump(dict(quick=QUICK, seed=SEED, seconds=round(time.time() - T_START, 1), checks=CHECKS),
          open(os.path.join(OUT_DIR, 'validation_study5.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{int(SUMMARY.passed.sum())} / {len(SUMMARY)} 項目 PASS、{time.time() - T_START:.0f} 秒')
assert SUMMARY.passed.all(), 'VALIDATION FAILED'
print('VALIDATION PASSED')
