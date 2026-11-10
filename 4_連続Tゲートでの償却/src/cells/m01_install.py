# ==================================================================================================
# セル 1：必要なライブラリのインストール（Colab に無いものだけ）と import
# ==================================================================================================
import importlib.util, subprocess, sys
for _mod, _pkg in [('stim', 'stim'), ('pymatching', 'pymatching'), ('scipy', 'scipy')]:
    if importlib.util.find_spec(_mod) is None:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', _pkg])
import os, io, json, math, itertools
import numpy as np, pandas as pd, stim, pymatching
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats as _st
print('stim', stim.__version__, '| pymatching', pymatching.__version__, '| numpy', np.__version__, '| pandas', pd.__version__)
