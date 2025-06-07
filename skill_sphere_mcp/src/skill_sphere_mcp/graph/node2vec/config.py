"""Configuration classes for Node2Vec."""

from dataclasses import dataclass
from dataclasses import field


@dataclass
class Node2VecTrainingConfig:
    """Node2Vec training parameters."""

    walk_length: int = 80
    num_walks: int = 10
    window_size: int = 5
    num_neg_samples: int = 5
    learning_rate: float = 0.025
    epochs: int = 5


@dataclass
class Node2VecModelConfig:
    """Node2Vec model parameters."""

    dimension: int = 128
    p: float = 1.0
    q: float = 1.0


@dataclass
class Node2VecConfig:
    """Node2Vec configuration parameters."""

    model: Node2VecModelConfig = field(default_factory=Node2VecModelConfig)
    training: Node2VecTrainingConfig = field(default_factory=Node2VecTrainingConfig)


@dataclass
class TransitionConfig:
    """Configuration for transition probabilities."""

    p: float
    q: float
    weight_key: str
    directed: bool
    unweighted: bool


@dataclass
class PreprocessConfig:
    """Configuration for graph preprocessing."""

    p: float = 1.0
    q: float = 1.0
    weight_key: str = "weight"
    directed: bool = False
    unweighted: bool = False
