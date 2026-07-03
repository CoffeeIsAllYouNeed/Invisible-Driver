import os
import random
import numpy as np
from abc import ABC, abstractmethod


class SetAnySeed(ABC):

    @abstractmethod
    def set(self, seed: int | float | str | bytes | bytearray | None) -> None:
        pass


class SetOSEnvironmentSeed(SetAnySeed):

    def set(self, seed: int | float | str | bytes | bytearray | None) -> None:
        os.environ["PYTHONHASHSEED"] = str(seed)


class SetRandomSeed(SetAnySeed):

    def set(self, seed: int | float | str | bytes | bytearray | None) -> None:
        random.seed(seed)


class SetNumpySeed(SetAnySeed):

    def set(self, seed: int | float | str | bytes | bytearray | None) -> None:
        np.random.seed(seed)


class SetAllSeeds:

    def __init__(self) -> None:
        self.seeding_methods: list[SetAnySeed] = [
            SetOSEnvironmentSeed(),
            SetRandomSeed(),
            SetNumpySeed(),
        ]

    def set_seed(self, seed: int | float | str | bytes | bytearray | None) -> None:
        for method in self.seeding_methods:
            method.set(seed)