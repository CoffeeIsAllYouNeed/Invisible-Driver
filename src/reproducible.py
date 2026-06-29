import os
import random
import numpy as np


class Reproducible:

    def _set_os_environment_seed(self, seed: int) -> None:
        os.environ["PYTHONHASHSEED"] = str(seed)

    def _set_random_seed(self, seed: int) -> None:
        random.seed(seed)

    def _set_numpy_seed(self, seed: int) -> None:
        np.random.seed(seed)
    
    # Why seed is set to 42? Thanks to "The Hitchhiker's Guide to the Galaxy".
    # Change as per your requirement.
    def set_seed(self, seed: int = 42) -> None:
        try:
            self._set_os_environment_seed(seed)
        except Exception as e:
            raise RuntimeError(f"Seed Allotment Failure [OS Environment]: {e}")
        try:
            self._set_random_seed(seed)
        except Exception as e:
            raise RuntimeError(f"Seed Allotment Failure [Random]: {e}")
        try:
            self._set_numpy_seed(seed)
        except Exception as e:
            raise RuntimeError(f"Seed Allotment Failure [NumPy]: {e}")