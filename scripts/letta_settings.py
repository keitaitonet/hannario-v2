import os


DEFAULT_BASE_URL = "http://localhost:8283"
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_EMBEDDING = "openai/text-embedding-3-small"


def letta_base_url() -> str:
    return os.getenv("LETTA_BASE_URL", DEFAULT_BASE_URL)


def letta_model() -> str:
    return os.getenv("LETTA_MODEL", DEFAULT_MODEL)


def letta_embedding() -> str:
    return os.getenv("LETTA_EMBEDDING", DEFAULT_EMBEDDING)
