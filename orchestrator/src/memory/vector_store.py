import json
import os
import hashlib
import tempfile
import shutil
from typing import List, Dict, Any
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, path: str = "./data/vector_store"):
        self.path = path
        self.documents: List[Dict[str, Any]] = []
        self.load()
        logger.info(f"Initialized Sovereign RAG Store at {path} | Count: {len(self.documents)}")

    def add(self, text: str, metadata: Dict[str, Any]) -> str:
        """Adds a document to the store with atomic persistence."""
        doc_id = hashlib.sha256(text.encode()).hexdigest()[:12]
        doc = {
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "timestamp": metadata.get("timestamp", "")
        }
        self.documents.append(doc)
        self.save()
        return doc_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Keyword-based intersection search (RAG Baseline)."""
        if not self.documents:
            return []
            
        results = []
        query_words = set(query.lower().split())
        
        for doc in self.documents:
            text = doc["text"].lower()
            matches = sum(1 for word in query_words if word in text)
            if matches > 0:
                results.append((matches, doc))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

    def save(self):
        """Atomic save using temp file to prevent corruption."""
        os.makedirs(self.path, exist_ok=True)
        filepath = os.path.join(self.path, "sovereign_memory.json")
        
        # Use tempfile for atomic write
        fd, temp_path = tempfile.mkstemp(dir=self.path, suffix=".tmp")
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(self.documents, f, indent=2)
            # Rename temp file to actual file (atomic move)
            shutil.move(temp_path, filepath)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def load(self):
        """Loads memory with corruption recovery."""
        filepath = os.path.join(self.path, "sovereign_memory.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    content = f.read()
                    if not content.strip():
                        self.documents = []
                        return
                    self.documents = json.loads(content)
            except Exception as e:
                logger.error(f"Memory corruption detected in {filepath}: {e}")
                # Recovery: Backup corrupt file and start fresh
                backup_path = filepath + ".corrupt"
                shutil.copy2(filepath, backup_path)
                logger.warning(f"Corrupt memory backed up to {backup_path}. Re-initializing empty store.")
                self.documents = []
                # Attempt to delete the bad file so it can be recreated correctly
                try:
                    os.remove(filepath)
                except: pass
