from __future__ import annotations
import numpy as np

def error_bars(values, axis=None):
    arr = np.array(values)
    return float(arr.mean()), float(arr.std(ddof=1)) if arr.size>1 else 0.0
