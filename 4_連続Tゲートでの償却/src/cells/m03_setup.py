# 出力先の準備（パラメータの検査を含む）
assert RUN_MODE in ('quick', 'pilot', 'production', 'analysis_only'), RUN_MODE
assert all(isinstance(k, int) and k >= 1 for k in K_LIST) and 1 in K_LIST, 'K_LIST には 1 を含める（1 サイクルあたりの誤りの基準）'
assert all(g in ('d', 'half') or (isinstance(g, int) and g >= 1) for g in GAP_LIST)
if USE_GOOGLE_DRIVE:
    from google.colab import drive
    drive.mount('/content/drive')
    OUT_DIR = os.path.join(DRIVE_DIR, OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)
print('RUN_MODE =', RUN_MODE, '| 出力先 =', os.path.abspath(OUT_DIR))
