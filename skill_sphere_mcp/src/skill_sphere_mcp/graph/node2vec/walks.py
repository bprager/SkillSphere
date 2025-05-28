"""Random walk generation for Node2Vec."""

from dataclasses import dataclass

import numpy as np

from .sampling import alias_draw


@dataclass
class WalkConfig:
    """Configuration for random walks."""

    graph: dict[str, list[str]]
    alias_nodes: dict[str, dict[str, list[int]]]
    alias_edges: dict[tuple[str, str], dict[str, list[int]]]
    walk_length: int
    rng: np.random.Generator


def node2vec_walk(start_node: str, config: WalkConfig) -> list[str]:
    """Generate a random walk starting from a node.

    Args:
        start_node: Starting node
        config: Walk configuration

    Returns:
        List of nodes in the walk
    """
    walk = [start_node]
    while len(walk) < config.walk_length:
        cur = walk[-1]
        if len(config.graph[cur]) > 0:
            if len(walk) == 1:
                walk.append(
                    config.graph[cur][
                        alias_draw(config.alias_nodes[cur], 0, config.rng)
                    ]
                )
            else:
                prev = walk[-2]
                next_node = config.graph[cur][
                    alias_draw(config.alias_edges[(prev, cur)], 0, config.rng)
                ]
                walk.append(next_node)
        else:
            break
    return walk


def generate_walks(config: WalkConfig, num_walks: int) -> list[list[str]]:
    """Generate random walks for all nodes.

    Args:
        config: Walk configuration
        num_walks: Number of walks per node

    Returns:
        List of random walks
    """
    walks = []
    nodes = list(config.graph.keys())
    for _ in range(num_walks):
        config.rng.shuffle(nodes)
        for node in nodes:
            walks.append(node2vec_walk(node, config))
    return walks
