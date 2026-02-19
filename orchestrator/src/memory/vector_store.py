import json
import os
import hashlib
from typing import List, Dict, Any, Optional
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, path: str = "./data/vector_store"):
        self.path = path
        self.documents: List[Dict[str, Any]] = []
        self.load()
        logger.info(f"Initialized Sovereign RAG Store at {path}")

    def add(self, text: str, metadata: Dict[str, Any]) -> str:
        # Create a content-based ID
        doc_id = hashlib.sha256(text.encode()).hexdigest()[:12]
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "timestamp": metadata.get("timestamp", "")
        })
        self.save()
        return doc_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Improved semantic-approximation search.
        In production, this would use ChromaDB/Pinecone.
        """
        if not self.documents:
            return []
            
        results = []
        query_words = set(query.lower().split())
        
        for doc in self.documents:
            text = doc["text"].lower()
            # Calculate intersection score
            matches = sum(1 for word in query_words if word in text)
            if matches > 0:
                results.append((matches, doc))
        
        # Sort by score
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

    def save(self):
        os.makedirs(self.path, exist_ok=True)
        with open(os.path.join(self.path, "sovereign_memory.json"), "w") as f:
            json.dump(self.documents, f, indent=2)
            
    def load(self):
        filepath = os.path.join(self.path, "sovereign_memory.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    self.documents = json.load(f)
            except Exception as e:
                logger.error(f"Memory corruption detected: {e}")
                self.documents = []
