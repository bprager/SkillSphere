"""Configuration settings for the hypergraph ingestion pipeline."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the ingestion pipeline, loaded from environment variables."""

    # External services
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_pass: str = "password"
    ollama_base_url: str = "http://127.0.0.1:11434"

    # Paths
    graph_schema_yaml: str = "./graph_schema.yaml"
    doc_root: str = "./docs"
    registry_path: str = "./doc_registry.sqlite3"
    faiss_index_path: str = "./faiss.index"

    # Ingestion
    chunk_size: int = 1500
    chunk_overlap: int = 200
    glean_max_rounds: int = 3  # max LLM passes per chunk

    # Node2Vec
    node2vec_dim: int = 128
    node2vec_walks: int = 10
    node2vec_walk_length: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
