"""
Search Engine Core with Tokenization, Indexing, and Ranking

Uses Trie for autocomplete, HashMap for keyword indexing, and Priority Queue for ranking.

Time Complexity:
- Index document: O(n) where n is number of words in document
- Search: O(k * log(k)) where k is number of matching documents
- Autocomplete: O(m + s) where m is prefix length, s is number of suggestions

Space Complexity: O(V + D) where V is vocabulary size, D is number of documents
"""

import re
import heapq
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from data_structures.trie import Trie
from data_structures.lru_cache import LRUCache


class SearchEngine:
    """Core search engine with tokenization, indexing, and ranking"""
    
    def __init__(self, cache_capacity: int = 100):
        """
        Initialize the search engine.
        
        Args:
            cache_capacity: Maximum number of cached search results
        """
        # Trie for autocomplete
        self.trie = Trie()
        
        # HashMap: keyword -> set of document IDs containing this keyword
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)
        
        # HashMap: document_id -> document metadata
        self.documents: Dict[str, Dict] = {}
        
        # HashMap: document_id -> keyword frequency map
        self.document_keyword_freq: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # LRU Cache for search results
        self.search_cache = LRUCache(cache_capacity)
        
        # HashMap: document_id -> access history (list of timestamps)
        self.access_history: Dict[str, List[datetime]] = defaultdict(list)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words (case-insensitive, alphanumeric).
        
        Args:
            text: Input text to tokenize
        
        Returns:
            List of lowercase tokens
        """
        if not text:
            return []
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _calculate_tf(self, keyword: str, document_id: str) -> float:
        """
        Calculate Term Frequency (TF) for a keyword in a document.
        
        Args:
            keyword: The keyword
            document_id: The document ID
        
        Returns:
            Term frequency score
        """
        if document_id not in self.document_keyword_freq:
            return 0.0
        
        freq_map = self.document_keyword_freq[document_id]
        keyword_freq = freq_map.get(keyword.lower(), 0)
        
        if keyword_freq == 0:
            return 0.0
        
        # Normalize by total words in document
        total_words = sum(freq_map.values())
        return keyword_freq / total_words if total_words > 0 else 0.0
    
    def _calculate_recency_score(self, document_id: str) -> float:
        """
        Calculate recency score based on last access time.
        
        Args:
            document_id: The document ID
        
        Returns:
            Recency score (0.0 to 1.0)
        """
        if document_id not in self.access_history or not self.access_history[document_id]:
            return 0.0
        
        last_access = max(self.access_history[document_id])
        now = datetime.now()
        time_diff = (now - last_access).total_seconds()
        
        # Score decays over time (exponential decay)
        # Documents accessed within last hour get high score
        if time_diff < 3600:  # 1 hour
            return 1.0
        elif time_diff < 86400:  # 1 day
            return 0.7
        elif time_diff < 604800:  # 1 week
            return 0.4
        else:
            return 0.1
    
    def _calculate_usage_score(self, document_id: str) -> float:
        """
        Calculate usage score based on access frequency.
        
        Args:
            document_id: The document ID
        
        Returns:
            Usage score (0.0 to 1.0)
        """
        if document_id not in self.access_history:
            return 0.0
        
        access_count = len(self.access_history[document_id])
        
        # Normalize: more accesses = higher score (capped at 1.0)
        return min(1.0, access_count / 10.0)
    
    def _calculate_relevance_score(self, document_id: str, keywords: List[str]) -> float:
        """
        Calculate overall relevance score for a document.
        
        Ranking factors:
        1. Keyword frequency (TF) - 50% weight
        2. Recency of access - 30% weight
        3. Usage history - 20% weight
        
        Args:
            document_id: The document ID
            keywords: List of search keywords
        
        Returns:
            Relevance score
        """
        # Calculate TF score (average across all keywords)
        tf_scores = [self._calculate_tf(kw, document_id) for kw in keywords]
        avg_tf = sum(tf_scores) / len(tf_scores) if tf_scores else 0.0
        
        # Calculate recency score
        recency_score = self._calculate_recency_score(document_id)
        
        # Calculate usage score
        usage_score = self._calculate_usage_score(document_id)
        
        # Weighted combination
        relevance = (0.5 * avg_tf) + (0.3 * recency_score) + (0.2 * usage_score)
        
        return relevance
    
    def index_document(self, document_id: str, title: str, body: str, tags: List[str] = None) -> None:
        """
        Index a document for search.
        
        Args:
            document_id: Unique document identifier
            title: Document title
            body: Document content
            tags: Optional list of tags
        
        Time Complexity: O(n) where n is number of words
        """
        if tags is None:
            tags = []
        
        # Combine title, body, and tags for indexing
        full_text = f"{title} {body} {' '.join(tags)}"
        
        # Tokenize
        tokens = self._tokenize(full_text)
        
        # Update keyword index and document keyword frequency
        keyword_freq = defaultdict(int)
        for token in tokens:
            self.keyword_index[token].add(document_id)
            keyword_freq[token] += 1
            # Add to Trie for autocomplete
            self.trie.insert(token)
        
        # Store keyword frequencies for this document
        self.document_keyword_freq[document_id] = dict(keyword_freq)
        
        # Store document metadata
        self.documents[document_id] = {
            "id": document_id,
            "title": title,
            "body": body,
            "tags": tags
        }
    
    def remove_document(self, document_id: str) -> None:
        """Remove a document from the index"""
        if document_id not in self.documents:
            return
        
        # Remove from keyword index
        if document_id in self.document_keyword_freq:
            for keyword in self.document_keyword_freq[document_id]:
                self.keyword_index[keyword].discard(document_id)
                if not self.keyword_index[keyword]:
                    del self.keyword_index[keyword]
        
        # Clean up
        del self.documents[document_id]
        del self.document_keyword_freq[document_id]
        if document_id in self.access_history:
            del self.access_history[document_id]
    
    def update_document(self, document_id: str, title: str = None, body: str = None, tags: List[str] = None) -> bool:
        """Update an existing document"""
        if document_id not in self.documents:
            return False
        
        # Remove old index
        self.remove_document(document_id)
        
        # Get current values
        current = self.documents.get(document_id, {})
        new_title = title if title is not None else current.get("title", "")
        new_body = body if body is not None else current.get("body", "")
        new_tags = tags if tags is not None else current.get("tags", [])
        
        # Re-index
        self.index_document(document_id, new_title, new_body, new_tags)
        return True
    
    def record_access(self, document_id: str) -> None:
        """Record that a document was accessed"""
        self.access_history[document_id].append(datetime.now())
        # Keep only last 100 accesses per document
        if len(self.access_history[document_id]) > 100:
            self.access_history[document_id] = self.access_history[document_id][-100:]
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
        
        Returns:
            List of ranked document results
        
        Time Complexity: O(k * log(k)) where k is number of matching documents
        """
        if not query:
            return []
        
        # Check cache first
        cache_key = f"search:{query}:{top_k}"
        cached_result = self.search_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Tokenize query
        keywords = self._tokenize(query)
        if not keywords:
            return []
        
        # Find documents containing all keywords (AND search)
        matching_docs = None
        for keyword in keywords:
            doc_set = self.keyword_index.get(keyword, set())
            if matching_docs is None:
                matching_docs = doc_set.copy()
            else:
                matching_docs &= doc_set  # Intersection
        
        if not matching_docs:
            # If no documents match all keywords, try OR search (any keyword)
            matching_docs = set()
            for keyword in keywords:
                matching_docs |= self.keyword_index.get(keyword, set())
        
        # Rank documents using priority queue (min-heap for top-k)
        # We use negative scores because heapq is a min-heap
        heap = []
        
        for doc_id in matching_docs:
            if doc_id not in self.documents:
                continue
            
            score = self._calculate_relevance_score(doc_id, keywords)
            
            # Record access for ranking
            self.record_access(doc_id)
            
            # Use min-heap to keep top-k
            if len(heap) < top_k:
                heapq.heappush(heap, (score, doc_id))
            elif score > heap[0][0]:
                heapq.heapreplace(heap, (score, doc_id))
        
        # Extract results in descending order of score
        results = []
        while heap:
            score, doc_id = heapq.heappop(heap)
            doc = self.documents[doc_id].copy()
            doc["relevance_score"] = round(score, 4)
            results.append(doc)
        
        results.reverse()  # Highest score first
        
        # Cache the result
        self.search_cache.put(cache_key, results)
        
        return results
    
    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for a prefix.
        
        Args:
            prefix: The prefix to complete
            limit: Maximum number of suggestions
        
        Returns:
            List of autocomplete suggestions
        
        Time Complexity: O(m + s) where m is prefix length, s is number of suggestions
        """
        return self.trie.autocomplete(prefix, limit)
    
    def clear_cache(self) -> None:
        """Clear the search cache"""
        self.search_cache.clear()
