import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple
from ai_layer.config import settings

class LocalVectorDB:
    def __init__(self):
        self.db_path = settings.VECTOR_DB_PATH
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[np.ndarray] = []
        self.model = None
        self._init_embedding_model()
        self.load_db()

    def _init_embedding_model(self):
        """Initializes the embedding model (local SentenceTransformers or a mockup fallback)"""
        if settings.EMBEDDING_PROVIDER == "local":
            try:
                from sentence_transformers import SentenceTransformer
                # Use CUDA if available
                device = "cuda" if os.environ.get("USE_CUDA", "false").lower() == "true" else "cpu"
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL, device=device)
                print(f"[RAG] Initialized local SentenceTransformer on device: {device}")
            except ImportError:
                print("[RAG] Warning: sentence-transformers not installed. Using TF-IDF/BM25 mockup embedding provider.")
                self.model = None
        else:
            # Fallback for API-based embeddings (e.g. OpenAI, Gemini)
            self.model = None

    def get_embedding(self, text: str) -> np.ndarray:
        """Generates embedding vector for a given text."""
        if self.model:
            return self.model.encode(text)
        else:
            # Fallback mockup: Character/Word frequency vector normalized
            # Hash words to a 384-dimensional vector (matches all-MiniLM-L6-v2 dimensions)
            words = text.lower().split()
            vector = np.zeros(384)
            for w in words:
                idx = idx = abs(hash(w)) % 384
                vector[idx] += 1
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            return vector

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Adds list of documents.
        Each doc: {"id": str, "content": str, "metadata": dict}
        """
        for doc in docs:
            emb = self.get_embedding(doc["content"])
            self.documents.append(doc)
            self.embeddings.append(emb)
        self.save_db()

    def search(self, query: str, top_k: int = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches similar documents using Cosine Similarity.
        Returns: List of tuples (document_dict, similarity_score)
        """
        if not self.documents:
            return []
            
        k = top_k or settings.RAG_TOP_K
        query_emb = self.get_embedding(query)
        
        scores = []
        for idx, doc_emb in enumerate(self.embeddings):
            # Cosine similarity
            dot_product = np.dot(query_emb, doc_emb)
            norm_q = np.linalg.norm(query_emb)
            norm_d = np.linalg.norm(doc_emb)
            
            similarity = 0.0
            if norm_q > 0 and norm_d > 0:
                similarity = float(dot_product / (norm_q * norm_d))
                
            scores.append((self.documents[idx], similarity))
            
        # Sort by similarity desc
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold
        filtered_scores = [s for s in scores if s[1] >= settings.RAG_SIMILARITY_THRESHOLD]
        
        return filtered_scores[:k]

    def save_db(self):
        """Saves documents and serialized embeddings to a local JSON file."""
        data = []
        for doc, emb in zip(self.documents, self.embeddings):
            data.append({
                "doc": doc,
                "embedding": emb.tolist()
            })
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_db(self):
        """Loads database from file if exists."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.documents = []
                self.embeddings = []
                for item in data:
                    self.documents.append(item["doc"])
                    self.embeddings.append(np.array(item["embedding"]))
                print(f"[RAG] Loaded {len(self.documents)} documents from vector database.")
            except Exception as e:
                print(f"[RAG] Error loading DB: {e}. Starting with empty database.")
                self.documents = []
                self.embeddings = []
        else:
            self.documents = []
            self.embeddings = []
