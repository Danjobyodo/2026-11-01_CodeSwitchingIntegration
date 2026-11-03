import numpy as _np
def population_count(x):
    return _np.bitwise_count(x).astype(_np.asarray(x).dtype)
