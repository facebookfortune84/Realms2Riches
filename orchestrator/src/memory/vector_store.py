import json
import os
from typing import List, Dict, Any, Optional
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, path: str = "./data/vector_store"):
        self.path = path
        self.documents: List[Dict[str, Any]] = []
        # In a real implementation, this would initialize ChromaDB or FAISS
        logger.info(f"Initialized VectorStore at {path}")

    def add(self, text: str, metadata: Dict[str, Any]) -> str:
        doc_id = str(len(self.documents))
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata
        })
        logger.debug(f"Added document {doc_id} to vector store")
        return doc_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Naive keyword search for scaffold purposes to avoid heavy dependencies like torch/numpy
        results = []
        query_terms = query.lower().split()
        
        for doc in self.documents:
            score = 0
            text = doc["text"].lower()
            for term in query_terms:
                if term in text:
                    score += 1
            if score > 0:
                results.append({**doc, "score": score})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def save(self):
        # Dump to disk for persistence
        os.makedirs(self.path, exist_ok=True)
        with open(os.path.join(self.path, "store.json"), "w") as f:
            json.dump(self.documents, f)
            
    def load(self):
        filepath = os.path.join(self.path, "store.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                self.documents = json.load(f)
