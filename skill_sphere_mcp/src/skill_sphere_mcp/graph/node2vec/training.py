"""Training and embedding methods for Node2Vec."""

from dataclasses import dataclass

import numpy as np


@dataclass
class SamplingConfig:
    """Configuration for sampling."""

    learning_rate: float


@dataclass
class NegativeSamplingConfig(SamplingConfig):
    """Configuration for negative sampling."""

    num_samples: int
    rng: np.random.Generator


def get_context_nodes(walk: list[str], center_idx: int, window_size: int) -> list[str]:
    """Get context nodes for a center node in a walk.

    Args:
        walk: Random walk
        center_idx: Index of center node
        window_size: Size of context window

    Returns:
        List of context nodes
    """
    start = max(0, center_idx - window_size)
    end = min(len(walk), center_idx + window_size + 1)
    return walk[start:center_idx] + walk[center_idx + 1 : end]


def process_positive_samples(
    node: str,
    context_nodes: list[str],
    embeddings: dict[str, np.ndarray],
    config: SamplingConfig,
) -> None:
    """Process positive samples for training.

    Args:
        node: Center node
        context_nodes: Context nodes
        embeddings: Node embeddings
        config: Sampling configuration
    """
    for context_node in context_nodes:
        update_embedding(node, context_node, 1.0, embeddings, config.learning_rate)


def process_negative_samples(
    node: str,
    context_nodes: list[str],
    nodes: set[str],
    embeddings: dict[str, np.ndarray],
    config: NegativeSamplingConfig,
) -> None:
    """Process negative samples for training.

    Args:
        node: Center node
        context_nodes: Context nodes
        nodes: Set of all nodes
        embeddings: Node embeddings
        config: Negative sampling configuration
    """
    for _ in range(config.num_samples):
        neg_node = config.rng.choice(list(nodes - {node} - set(context_nodes)))
        update_embedding(node, neg_node, 0.0, embeddings, config.learning_rate)


def update_embedding(
    node1: str,
    node2: str,
    label: float,
    embeddings: dict[str, np.ndarray],
    learning_rate: float,
) -> None:
    """Update embeddings using gradient descent.

    Args:
        node1: First node
        node2: Second node
        label: Target label (1.0 for positive, 0.0 for negative)
        embeddings: Node embeddings
        learning_rate: Learning rate
    """
    if node1 not in embeddings or node2 not in embeddings:
        return

    vec1 = embeddings[node1]
    vec2 = embeddings[node2]

    # Compute dot product
    dot_product = np.dot(vec1, vec2)
    sigmoid = 1.0 / (1.0 + np.exp(-dot_product))

    # Compute gradients
    grad = (label - sigmoid) * learning_rate
    grad_vec1 = grad * vec2
    grad_vec2 = grad * vec1

    # Update embeddings
    embeddings[node1] += grad_vec1
    embeddings[node2] += grad_vec2
