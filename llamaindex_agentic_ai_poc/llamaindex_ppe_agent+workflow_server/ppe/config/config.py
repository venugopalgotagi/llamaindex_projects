"""Configuration module for PPE workflow context and settings.

This module provides configuration for LLM, embeddings, and database
connections used throughout the PPE workflow system.
"""

import dataclasses
import logging
import os

import llama_index.core.memory
import llama_index.core.storage.chat_store.sql
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.memory import VectorMemoryBlock
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger()

PG_USER = os.environ.get("PG_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
PG_LONG_TERM_DB = os.environ.get("PG_LONG_TERM_DB")

llm = Ollama(
    model=os.environ.get("LLAMA_MODEL"),
    request_timeout=360.0,
    context_window=8000,
)
Settings.llm = llm


@dataclasses.dataclass
class ContextProvider:
    """Provides context and memory management for PPE workflows.

    This class manages database connections, vector stores, and embedding
    models for long-term memory storage and retrieval in PPE workflows.

    Attributes:
        long_term_memory_async_engine: Async database engine for PostgreSQL.
        long_term_memory_sync_engine: Synchronous database engine for PostgreSQL.
        vector_store: PostgreSQL vector store for embeddings.
        embed_model: HuggingFace embedding model instance.
    """

    def __init__(self) -> None:
        """Initialize the context provider with database and embedding setup."""
        self.long_term_memory_async_engine = create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_LONG_TERM_DB}"
        )
        self.long_term_memory_sync_engine = create_engine(
            f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_LONG_TERM_DB}"
        )
        self.vector_store = PGVectorStore(
            engine=self.long_term_memory_sync_engine,
            async_engine=self.long_term_memory_async_engine,
            table_name=PG_LONG_TERM_DB,
            embed_dim=384
        )
        self.embed_model = self.get_embedding_model()

        Settings.embed_model = self.embed_model
        Settings.timeout = 120

    async def get_memory(self, key: str) -> llama_index.core.memory.Memory:
        """Retrieve or create a memory instance for a given session key.

        Args:
            key: Session identifier used to retrieve or create memory.

        Returns:
            Memory instance configured with vector store for the session.
        """
        logger.info("Loading memory for key %s", key)
        return llama_index.core.memory.Memory.from_defaults(
            session_id=key,
            memory_blocks=[
                VectorMemoryBlock(
                    embed_model=self.embed_model,
                    vector_store=self.vector_store
                )
            ],
        )

    def get_embedding_model(self) -> HuggingFaceEmbedding:
        """Get the HuggingFace embedding model instance.

        Returns:
            HuggingFaceEmbedding model configured from environment variables.
        """
        return HuggingFaceEmbedding(
            model_name=os.environ.get("EMBEDDING_MODEL_NAME")
        )
