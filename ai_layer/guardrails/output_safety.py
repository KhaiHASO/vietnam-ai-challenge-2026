from typing import List, Tuple
import re

class OutputSafetyGuardrail:
    def __init__(self, hallucination_threshold: float = 0.5):
        self.hallucination_threshold = hallucination_threshold
        # Disallowed response keywords (e.g. system codes, inner thoughts leakage, vulgarity)
        self.disallowed_patterns = [
            r"internal system error",
            r"<system_prompt>",
            r"thought process:",
            r"\[internal\]"
        ]
        
    def evaluate_output(self, response_text: str, retrieved_docs: List[str]) -> Tuple[bool, float, str]:
        """
        Evaluates output safety and hallucination risk.
        Returns:
            is_blocked (bool): True if output should be blocked or modified.
            hallucination_score (float): Hallucination risk score (0.0 to 1.0). 
                                       1.0 means high risk (no overlap with RAG).
            reason (str): Reason for blocking.
        """
        # 1. Disallowed keyword check
        for pattern in self.disallowed_patterns:
            if re.search(pattern, response_text.lower()):
                return True, 1.0, f"Disallowed pattern '{pattern}' found in response."
                
        # 2. Hallucination risk check (Grounding Check)
        # If no RAG documents were retrieved, we cannot assess grounding this way, default to 0.0 risk
        if not retrieved_docs:
            return False, 0.0, "No RAG docs to evaluate grounding."
            
        # Basic token overlap (Jaccard similarity fallback)
        def get_words(text: str) -> set:
            return set(re.findall(r'\w+', text.lower()))
            
        response_words = get_words(response_text)
        
        # Merge all RAG documents words
        rag_words = set()
        for doc in retrieved_docs:
            rag_words.update(get_words(doc))
            
        if not response_words:
            return False, 0.0, "Empty response."
            
        # We calculate overlap of non-stop-words/important words
        stop_words = {"và", "là", "thì", "mà", "của", "cho", "để", "ở", "trong", "được", "có", "không", "với", "the", "a", "an", "and", "is", "of", "to", "in"}
        important_resp_words = response_words - stop_words
        important_rag_words = rag_words - stop_words
        
        if not important_resp_words:
            return False, 0.0, "Only stop words in response."
            
        overlap = important_resp_words.intersection(important_rag_words)
        
        # Grounding score: ratio of response words backed by RAG
        grounding_score = len(overlap) / len(important_resp_words)
        
        # Hallucination score is inverse of grounding
        hallucination_score = 1.0 - grounding_score
        
        # If hallucination score is higher than threshold, flag it
        is_blocked = hallucination_score > self.hallucination_threshold
        reason = f"High hallucination risk: {hallucination_score:.2f} (Threshold: {self.hallucination_threshold})" if is_blocked else "Safe"
        
        return is_blocked, hallucination_score, reason
