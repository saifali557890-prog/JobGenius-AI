import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from config import config
from utils.logger import get_logger

logger = get_logger("EmbeddingModel")

class EmbeddingModel:
    _instance = None

    def __new__(cls):
        """Singleton pattern so transformer model loads into RAM only once."""
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            cls._instance.model = None  # Explicitly initialize attribute
            
        # Agar pehle failure ki vajah se model load nahi ho saka tha, toh retry karein
        if cls._instance.model is None:
            logger.info(f"Loading Sentence Transformer Model: '{config.EMBEDDING_MODEL_NAME}'...")
            try:
                cls._instance.model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
                logger.info("Embedding Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load transformer model: {str(e)}")
                # Fail hone par instance ko reset kar dein taake next call par dubara try ho sake
                cls._instance = None
                raise e

        return cls._instance

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Converts text or batch of text into normalized dense vector embeddings.
        Returns 2D numpy array of shape (N, dimension).
        """
        if self.model is None:
            raise RuntimeError("Embedding model is not loaded.")

        if isinstance(texts, str):
            texts = [texts]
            
        if not texts:
            return np.array([], dtype=np.float32)

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=normalize
            )
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise e

    @property
    def embedding_dimension(self) -> int:
        """Returns the vector size dimension (e.g. 768 for BGE base model)."""
        if self.model is None:
            raise RuntimeError("Embedding model is not loaded.")
        return self.model.get_sentence_embedding_dimension()