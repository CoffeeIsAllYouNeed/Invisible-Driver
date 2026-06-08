import os
import random
import numpy as np


class Reproducible:
    
    # To produce reproducible results:
    def set_seed(self, seed: int = 42) -> None:
        try:
            os.environ["PYTHONHASHSEED"] = str(seed)
            random.seed(seed)
            np.random.seed(seed)
        except Exception as e:
            raise RuntimeError(f"Failed to set reproducible seeds: {e}")