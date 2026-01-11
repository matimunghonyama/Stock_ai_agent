"""
Vector Store
Simple vector database for company profiles and embeddings
This is a placeholder implementation. For production, use:
- Pinecone
- Weaviate
- Chroma
- FAISS
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class VectorStore:
    """
    Simple in-memory vector store for company profiles and document embeddings
    
    Note: This is a basic implementation. For production use, integrate with
    a proper vector database like Pinecone, Weaviate, or Chroma.
    """
    
    def __init__(self, storage_dir: str = ".vectorstore"):
        """
        Initialize vector store
        
        Args:
            storage_dir: Directory to persist vector data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.vectors = []  # List of (id, vector, metadata) tuples
        self.index_file = self.storage_dir / "index.json"
        
        self._load_index()
    
    def _load_index(self):
        """Load index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.vectors = [
                        (item['id'], np.array(item['vector']), item['metadata'])
                        for item in data
                    ]
            except Exception as e:
                print(f"Error loading vector index: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            data = [
                {
                    'id': id_,
                    'vector': vector.tolist(),
                    'metadata': metadata
                }
                for id_, vector, metadata in self.vectors
            ]
            
            with open(self.index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving vector index: {e}")
    
    def add(self, id_: str, vector: List[float], metadata: Dict):
        """
        Add a vector to the store
        
        Args:
            id_: Unique identifier
            vector: Embedding vector
            metadata: Associated metadata (company info, text, etc.)
        """
        vector_array = np.array(vector)
        self.vectors.append((id_, vector_array, metadata))
        self._save_index()
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            
        Returns:
            List of (id, similarity_score, metadata) tuples
        """
        if not self.vectors:
            return []
        
        query_array = np.array(query_vector)
        
        # Calculate cosine similarity
        similarities = []
        for id_, vector, metadata in self.vectors:
            similarity = self._cosine_similarity(query_array, vector)
            similarities.append((id_, similarity, metadata))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get(self, id_: str) -> Optional[Tuple[List[float], Dict]]:
        """
        Get a vector by ID
        
        Args:
            id_: Unique identifier
            
        Returns:
            (vector, metadata) tuple or None
        """
        for stored_id, vector, metadata in self.vectors:
            if stored_id == id_:
                return (vector.tolist(), metadata)
        return None
    
    def delete(self, id_: str) -> bool:
        """
        Delete a vector by ID
        
        Args:
            id_: Unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        for i, (stored_id, _, _) in enumerate(self.vectors):
            if stored_id == id_:
                del self.vectors[i]
                self._save_index()
                return True
        return False
    
    def update_metadata(self, id_: str, metadata: Dict) -> bool:
        """
        Update metadata for a vector
        
        Args:
            id_: Unique identifier
            metadata: New metadata
            
        Returns:
            True if updated, False if not found
        """
        for i, (stored_id, vector, _) in enumerate(self.vectors):
            if stored_id == id_:
                self.vectors[i] = (stored_id, vector, metadata)
                self._save_index()
                return True
        return False
    
    def clear(self):
        """Clear all vectors"""
        self.vectors = []
        self._save_index()
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get_stats(self) -> Dict:
        """Get store statistics"""
        return {
            'total_vectors': len(self.vectors),
            'storage_dir': str(self.storage_dir)
        }


class CompanyProfileStore:
    """
    Specialized store for company profiles
    Built on top of VectorStore
    """
    
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
    
    def add_company_profile(self, ticker: str, profile: Dict, embedding: List[float]):
        """
        Add a company profile
        
        Args:
            ticker: Stock ticker
            profile: Company profile data
            embedding: Text embedding of profile
        """
        metadata = {
            'type': 'company_profile',
            'ticker': ticker,
            'profile': profile,
            'timestamp': datetime.now().isoformat()
        }
        self.store.add(f"company:{ticker}", embedding, metadata)
    
    def search_similar_companies(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar companies
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            
        Returns:
            List of company profile dictionaries
        """
        results = self.store.search(query_embedding, top_k)
        return [
            {
                'ticker': metadata.get('ticker'),
                'profile': metadata.get('profile'),
                'similarity': score
            }
            for _, score, metadata in results
            if metadata.get('type') == 'company_profile'
        ]
    
    def get_company_profile(self, ticker: str) -> Optional[Dict]:
        """
        Get profile for a specific company
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Company profile or None
        """
        result = self.store.get(f"company:{ticker}")
        if result:
            _, metadata = result
            return metadata.get('profile')
        return None


# Example usage in comments
"""
# Initialize stores
vector_store = VectorStore()
company_store = CompanyProfileStore(vector_store)

# Add a company profile
profile = {
    'name': 'Apple Inc.',
    'sector': 'Technology',
    'description': 'Apple designs and manufactures consumer electronics...',
    'market_cap': 3000000000000
}

# In practice, you'd generate this embedding using Claude or another model
embedding = [0.1, 0.2, 0.3, ...]  # Example embedding

company_store.add_company_profile('AAPL', profile, embedding)

# Search for similar companies
similar = company_store.search_similar_companies(query_embedding, top_k=3)
"""