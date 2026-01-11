"""
Response Caching
Simple cache implementation for API responses and analysis results
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path


class ResponseCache:
    """
    Simple file-based cache for API responses and analysis results
    """
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours for cached items
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Generate cache key from query and context
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Cache key as string
        """
        cache_string = query
        if context:
            cache_string += json.dumps(context, sort_keys=True)
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query: str, context: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Cached data or None if not found/expired
        """
        key = self._generate_key(query, context)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data['response']
            
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def set(self, query: str, response: Any, context: Optional[Dict] = None):
        """
        Store response in cache
        
        Args:
            query: User query
            response: Response to cache
            context: Additional context
        """
        key = self._generate_key(query, context)
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'context': context
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cached items"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def clear_expired(self):
        """Clear only expired cached items"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    
            except Exception:
                # If we can't read it, delete it
                cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_items': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Singleton instance for easy import
_default_cache = None

def get_default_cache() -> ResponseCache:
    """Get the default cache instance"""
    global _default_cache
    if _default_cache is None:
        _default_cache = ResponseCache()
    return _default_cache