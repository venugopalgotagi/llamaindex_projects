import dataclasses
import os
import logging
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


#load env variables from .env file
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

    def __init__(self,):
        self.long_term_memory_async_engine = create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_LONG_TERM_DB}"
        )
        self.long_term_memory_sync_engine = create_engine(
            f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_LONG_TERM_DB}"
        )
        self.vector_store = PGVectorStore(engine=self.long_term_memory_sync_engine,
                                          async_engine=self.long_term_memory_async_engine,
                                          table_name=PG_LONG_TERM_DB,
                                          embed_dim=384)
        self.embed_model = self.get_embedding_model()

        Settings.embed_model = self.embed_model
        Settings.timeout = 120


    async def get_memory(self,key: str):
        logger.info("Loading memory for key {}", key)
        return llama_index.core.memory.Memory.from_defaults(
            session_id=key,
            memory_blocks=[
                VectorMemoryBlock(
                    embed_model=self.embed_model,
                    vector_store=self.vector_store)],
        )

    def get_embedding_model(self) -> HuggingFaceEmbedding:
        return HuggingFaceEmbedding(model_name=os.environ.get("EMBEDDING_MODEL_NAME"))
