import os
import random
import numpy as np


class Reproducible:

    def _set_env_seed(self, seed: int) -> None:
        os.environ["PYTHONHASHSEED"] = str(seed)

    def _set_random_seed(self, seed: int) -> None:
        random.seed(seed)

    def _set_numpy_seed(self, seed: int) -> None:
        np.random.seed(seed)

    # To produce reproducible results:
    def set_seed(self, seed: int = 42) -> None:
        try:
            self._set_env_seed(seed)
            self._set_random_seed(seed)
            self._set_numpy_seed(seed)
        except Exception as e:
            raise RuntimeError(f"Failed to set reproducible seeds: {e}")