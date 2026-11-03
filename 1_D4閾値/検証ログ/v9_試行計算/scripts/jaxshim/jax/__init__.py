"""Minimal numpy stand-in for the parts of JAX used by the dense reference (local CPU test only)."""
import numpy as _np
from . import numpy  # noqa: F401
from . import lax  # noqa: F401
def jit(f=None, **kw):
    return f if f is not None else (lambda g: g)
def devices():
    return ["numpy-shim-cpu"]
