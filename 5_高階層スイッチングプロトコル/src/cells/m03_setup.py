# ==================================================================================================
# セル 3：準備（import、出力フォルダ）
# ==================================================================================================
import os, io, sys, json, time, math, itertools
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

if USE_GOOGLE_DRIVE:
    from google.colab import drive
    drive.mount('/content/drive')
    OUT_DIR = os.path.join('/content/drive/MyDrive', OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)
CASES = PLAN[RUN_MODE]
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
T_START = time.time()
print('RUN_MODE =', RUN_MODE, '| 出力先 =', os.path.abspath(OUT_DIR), '| numpy', np.__version__)
