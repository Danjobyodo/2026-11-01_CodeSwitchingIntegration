!pip -q install stim pymatching numpy pandas matplotlib numba
# GPU 版 JAX は Colab の GPU ランタイムにプリインストール済み。無い場合のみ次行を有効に:
# !pip -q install -U "jax[cuda12]"
import jax
print("JAX devices:", jax.devices())