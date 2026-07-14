import uuid
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ai_layer.rag.interfaces.chunker import BaseChunker
from ai_layer.rag.models import Document, Chunk, ChunkMetadataModel

class LangchainChunker(BaseChunker):
    """
    Chunker implementation using Langchain's RecursiveCharacterTextSplitter.
    Ensures semantic continuity by breaking at paragraphs, then sentences, then words.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
    def split(self, documents: List[Document]) -> List[Chunk]:
        chunks = []
        for doc in documents:
            if not doc.text_content:
                continue
                
            # Split the text content
            text_chunks = self.splitter.split_text(doc.text_content)
            
            # Create Chunk objects
            for idx, text in enumerate(text_chunks):
                meta = doc.metadata.copy()
                meta["knowledge_item_id"] = doc.knowledge_item_id
                
                chunk_meta = ChunkMetadataModel(
                    source_id=doc.id,
                    source_type=doc.source_type.value if hasattr(doc, 'source_type') else "",
                    chunk_index=idx,
                    total_chunks=len(text_chunks),
                    extra=meta
                )
                
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    text=text,
                    metadata=chunk_meta
                )
                chunks.append(chunk)
                
        return chunks
