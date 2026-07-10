import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai_layer.rag.interfaces.chunker import BaseChunker
from ai_layer.rag.models import Document, Chunk

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
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    document_id=doc.id,
                    knowledge_item_id=doc.knowledge_item_id,
                    text=text,
                    chunk_index=idx,
                    metadata=doc.metadata.copy()  # Inherit metadata from document
                )
                chunks.append(chunk)
                
        return chunks
