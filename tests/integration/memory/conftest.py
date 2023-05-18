import numpy
import pytest

from autogpt.config.config import Config
from autogpt.llm.providers.openai import OPEN_AI_EMBEDDING_MODELS
from autogpt.memory.vector.memory_item import MemoryItem
from autogpt.memory.vector.utils import Embedding


@pytest.fixture
def embedding_dimension(config: Config):
    return OPEN_AI_EMBEDDING_MODELS[config.embedding_model].embedding_dimensions


@pytest.fixture
def mock_embedding(embedding_dimension: int) -> Embedding:
    return numpy.full((1, embedding_dimension), 0.0255, numpy.float32)[0]


@pytest.fixture
def memory_item(mock_embedding: Embedding):
    return MemoryItem(
        raw_content="test content",
        summary="test content summary",
        chunks=["test content"],
        chunk_summaries=["test content summary"],
        e_summary=mock_embedding,
        e_chunks=[mock_embedding],
        metadata={},
    )
