import json
import math
import re
from collections import Counter
from pathlib import Path

from ai_layer.rag.models import Chunk


class LexicalRetriever:
    def __init__(self, index_path: str | Path | None = None) -> None:
        self.index_path = Path(index_path).resolve() if index_path else None
        self._chunks: dict[str, Chunk] = {}
        if self.index_path and self.index_path.exists():
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            self._chunks = {
                item["id"]: Chunk.model_validate(item) for item in data.get("chunks", [])
            }

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)

    def add_chunks(self, chunks: list[Chunk]) -> bool:
        for chunk in chunks:
            if not chunk.id:
                raise ValueError("Chunk id is required")
            self._chunks[chunk.id] = chunk.model_copy(deep=True)
        if self.index_path:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.index_path.with_suffix(self.index_path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(
                    {"chunks": [chunk.model_dump(mode="json") for chunk in self._chunks.values()]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            temporary.replace(self.index_path)
        return True

    def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[Chunk]:
        candidates = [
            chunk
            for chunk in self._chunks.values()
            if not filters
            or all(chunk.metadata.extra.get(key) == value for key, value in filters.items())
        ]
        if not candidates:
            return []
        query_terms = self._tokens(query)
        document_terms = [self._tokens(chunk.text) for chunk in candidates]
        average_length = sum(map(len, document_terms)) / len(document_terms) or 1.0
        document_frequency = Counter(
            term for terms in document_terms for term in set(terms)
        )
        scores: list[tuple[float, Chunk]] = []
        for chunk, terms in zip(candidates, document_terms):
            frequencies = Counter(terms)
            score = 0.0
            for term in query_terms:
                frequency = frequencies[term]
                if not frequency:
                    continue
                inverse = math.log(
                    1 + (len(candidates) - document_frequency[term] + 0.5)
                    / (document_frequency[term] + 0.5)
                )
                score += inverse * frequency * 2.5 / (
                    frequency + 1.5 * (1 - 0.75 + 0.75 * len(terms) / average_length)
                )
            if score > 0:
                result = chunk.model_copy(deep=True)
                result.metadata.extra["lexical_score"] = score
                scores.append((score, result))
        scores.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scores[:top_k]]
