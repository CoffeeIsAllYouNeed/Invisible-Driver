import os
import random
import numpy as np


def set_seed(seed: int = 42) -> None:
    # To produce reproducible results:
    try:
        os.environ["PYTHONHASHSEED"] = str(seed)
        random.seed(seed)
        np.random.seed(seed)
    except Exception as e:
        raise RuntimeError(f"Failed to set seeds: {e}")