# ==================================================================================================
# セル 3：準備
# ==================================================================================================
import os, json, time, math, itertools
import numpy as np
import pandas as pd
os.makedirs(OUT_DIR, exist_ok=True)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
CHECKS = []                   # (名前, 合否, 詳細)


def record(name, ok, detail=''):
    CHECKS.append(dict(check=name, passed=bool(ok), detail=str(detail)))
    print(('PASS  ' if ok else 'FAIL  ') + name + ('  | ' + str(detail) if detail != '' else ''), flush=True)

T_START = time.time()
