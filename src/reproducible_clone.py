# Wrong code 
# Should I add other string handling code? 
import os
import random
import numpy as np

def set_seed(seed: int | None) -> None:
    # DEFAULT_SEED used is 42.
    if seed is None:
        return
        
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)