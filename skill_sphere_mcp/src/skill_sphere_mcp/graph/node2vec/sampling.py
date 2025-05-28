"""Alias sampling methods for Node2Vec."""

import numpy as np


def alias_setup(probs: list[float]) -> dict[str, list[int]]:
    """Set up alias sampling.

    Args:
        probs: List of probabilities

    Returns:
        Dictionary with alias sampling tables
    """
    k = len(probs)
    q = np.zeros(k)
    j = np.zeros(k, dtype=np.int32)

    smaller = []
    larger = []
    for kk, prob in enumerate(probs):
        q[kk] = k * prob
        if q[kk] < 1.0:
            smaller.append(kk)
        else:
            larger.append(kk)

    while len(smaller) > 0 and len(larger) > 0:
        small = smaller.pop()
        large = larger.pop()

        j[small] = large
        q[large] = q[large] + q[small] - 1.0
        if q[large] < 1.0:
            smaller.append(large)
        else:
            larger.append(large)

    return {"J": j.tolist(), "q": q.tolist()}


def alias_draw(alias: dict[str, list[int]], idx: int, rng: np.random.Generator) -> int:
    """Draw sample from alias table.

    Args:
        alias: Alias sampling tables
        idx: Index to sample from
        rng: Random number generator

    Returns:
        Sampled index
    """
    j = alias["J"]
    q = alias["q"]

    if rng.random() < q[idx]:
        return idx
    return j[idx]
