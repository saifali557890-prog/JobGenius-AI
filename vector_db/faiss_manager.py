import os
import faiss
import numpy as np
from typing import List, Tuple, Dict, Any
from config import config
from utils.logger import get_logger

logger = get_logger("FAISSManager")

class FAISSVectorManager:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index_path = str(config.FAISS_INDEX_PATH)
        self.id_mapping: Dict[int, int] = {}  # Internal Vector Index -> Postgres Job ID
        
        # Inner Product (Cosine Similarity when normalized) Index
        self.index = faiss.IndexFlatIP(self.dimension)
        self._load_index_if_exists()

    def build_index(self, vectors: np.ndarray, job_ids: List[int]):
        """Builds or replaces the vector index with fresh job embeddings."""
        if len(vectors) == 0:
            logger.warning("Empty vector set provided for indexing.")
            return

        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)
        
        # Build vector-to-DB mapping dictionary
        self.id_mapping = {i: job_id for i, job_id in enumerate(job_ids)}
        self.save_index()
        logger.info(f"FAISS index built successfully with {self.index.ntotal} vectors.")

    def add_vectors(self, vectors: np.ndarray, job_ids: List[int]):
        """Appends new job vectors to existing FAISS index."""
        if len(vectors) == 0:
            return

        faiss.normalize_L2(vectors)
        start_idx = self.index.ntotal
        self.index.add(vectors)
        
        for offset, job_id in enumerate(job_ids):
            self.id_mapping[start_idx + offset] = job_id
            
        self.save_index()
        logger.info(f"Added {len(vectors)} vectors to FAISS index. Total: {self.index.ntotal}")

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Executes k-NN similarity search against resume query vector.
        Returns list of tuples: [(Postgres_Job_ID, Similarity_Score), ...]
        """
        if self.index.ntotal == 0:
            logger.warning("Search executed on an empty FAISS index.")
            return []

        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.id_mapping:
                job_id = self.id_mapping[idx]
                score = float(scores[0][i])
                results.append((job_id, score))

        logger.info(f"Vector search returned {len(results)} matches.")
        return results

    def save_index(self):
        """Persists the FAISS index to storage disk."""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            # Save ID map next to index file
            mapping_path = self.index_path + ".map"
            import pickle
            with open(mapping_path, "wb") as f:
                pickle.dump(self.id_mapping, f)
            logger.info("FAISS index and ID mapping saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")

    def _load_index_if_exists(self):
        """Loads FAISS index from disk if present."""
        try:
            mapping_path = self.index_path + ".map"
            if os.path.exists(self.index_path) and os.path.exists(mapping_path):
                self.index = faiss.read_index(self.index_path)
                import pickle
                with open(mapping_path, "rb") as f:
                    self.id_mapping = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors.")
        except Exception as e:
            logger.warning(f"Could not load index from disk, starting fresh: {str(e)}")