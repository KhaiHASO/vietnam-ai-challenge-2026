from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EXCEL = "excel"
    GEOJSON = "geojson"
    CSV = "csv"
    IMAGE = "image"
    WEBSITE = "website"
    API = "api"
    EMAIL = "email"


class KnowledgeItem(BaseModel):
    id: str
    domain: str
    title: str
    source_type: SourceType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Document(BaseModel):
    id: str
    knowledge_item_id: str
    text_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    page_content: Optional[str] = None


class ChunkMetadataModel(BaseModel):
    source_id: str = Field(default="", description="ID of the source document")
    source_type: str = Field(default="", description="Type of source")
    chunk_index: int = Field(default=0, description="Position in the source document")
    total_chunks: int = Field(default=1, description="Total chunks generated from this source")
    rerank_score: Optional[float] = Field(default=None, description="Reranker relevance score")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extra metadata")


class Chunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: ChunkMetadataModel = Field(default_factory=ChunkMetadataModel)
    embedding: Optional[List[float]] = None
    sys_hash: Optional[str] = Field(default=None, description="Content-level dedup hash")
