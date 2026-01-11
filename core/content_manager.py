"""
Content Management System

Manages documents and folder organization with CRUD operations.

Time Complexity:
- Add document: O(1)
- Update document: O(1)
- Delete document: O(1)
- Get document: O(1)
- Move document: O(1)

Space Complexity: O(n) where n is number of documents
"""

from typing import Dict, List, Optional
from datetime import datetime
from data_structures.folder_tree import FolderTree
from core.search_engine import SearchEngine


class ContentManager:
    """Manages documents and folder organization"""
    
    def __init__(self, search_engine: SearchEngine = None):
        """
        Initialize content manager.
        
        Args:
            search_engine: SearchEngine instance for indexing
        """
        self.folder_tree = FolderTree()
        self.documents: Dict[str, Dict] = {}
        self.search_engine = search_engine or SearchEngine()
        self.next_id = 1
    
    def _generate_id(self) -> str:
        """Generate a unique document ID"""
        doc_id = f"doc_{self.next_id}"
        self.next_id += 1
        return doc_id
    
    def add_document(self, title: str, body: str, tags: List[str] = None, folder_path: str = "/") -> Dict:
        """
        Add a new document.
        
        Args:
            title: Document title
            body: Document content
            tags: Optional list of tags
            folder_path: Path to folder (default: root)
        
        Returns:
            Created document dictionary
        
        Time Complexity: O(n) where n is number of words (due to indexing)
        """
        if tags is None:
            tags = []
        
        doc_id = self._generate_id()
        now = datetime.now().isoformat()
        
        document = {
            "id": doc_id,
            "title": title,
            "body": body,
            "tags": tags,
            "created_at": now,
            "last_accessed": now,
            "folder_path": folder_path
        }
        
        self.documents[doc_id] = document
        
        # Index in search engine
        self.search_engine.index_document(doc_id, title, body, tags)
        
        # Add to folder
        self.folder_tree.add_folder(folder_path)
        self.folder_tree.add_document_to_folder(folder_path, doc_id)
        
        return document.copy()
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document dictionary or None if not found
        
        Time Complexity: O(1)
        """
        if document_id not in self.documents:
            return None
        
        doc = self.documents[document_id].copy()
        
        # Update last accessed
        doc["last_accessed"] = datetime.now().isoformat()
        self.documents[document_id]["last_accessed"] = doc["last_accessed"]
        
        # Record access in search engine
        self.search_engine.record_access(document_id)
        
        return doc
    
    def update_document(self, document_id: str, title: str = None, body: str = None, 
                       tags: List[str] = None) -> Optional[Dict]:
        """
        Update a document.
        
        Args:
            document_id: Document ID
            title: New title (optional)
            body: New body (optional)
            tags: New tags (optional)
        
        Returns:
            Updated document dictionary or None if not found
        
        Time Complexity: O(n) where n is number of words (due to re-indexing)
        """
        if document_id not in self.documents:
            return None
        
        doc = self.documents[document_id]
        
        new_title = title if title is not None else doc["title"]
        new_body = body if body is not None else doc["body"]
        new_tags = tags if tags is not None else doc["tags"]
        
        # Update document
        doc["title"] = new_title
        doc["body"] = new_body
        doc["tags"] = new_tags
        
        # Update search index
        self.search_engine.update_document(document_id, new_title, new_body, new_tags)
        
        return doc.copy()
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            True if deleted, False if not found
        
        Time Complexity: O(1)
        """
        if document_id not in self.documents:
            return False
        
        doc = self.documents[document_id]
        folder_path = doc.get("folder_path", "/")
        
        # Remove from folder
        self.folder_tree.remove_document_from_folder(folder_path, document_id)
        
        # Remove from search index
        self.search_engine.remove_document(document_id)
        
        # Remove document
        del self.documents[document_id]
        
        return True
    
    def move_document(self, document_id: str, new_folder_path: str) -> bool:
        """
        Move a document to a different folder.
        
        Args:
            document_id: Document ID
            new_folder_path: New folder path
        
        Returns:
            True if moved, False if not found
        
        Time Complexity: O(1)
        """
        if document_id not in self.documents:
            return False
        
        doc = self.documents[document_id]
        old_folder_path = doc.get("folder_path", "/")
        
        # Remove from old folder
        self.folder_tree.remove_document_from_folder(old_folder_path, document_id)
        
        # Add to new folder
        self.folder_tree.add_folder(new_folder_path)
        self.folder_tree.add_document_to_folder(new_folder_path, document_id)
        
        # Update document
        doc["folder_path"] = new_folder_path
        
        return True
    
    def list_documents(self, folder_path: str = None) -> List[Dict]:
        """
        List all documents, optionally filtered by folder.
        
        Args:
            folder_path: Optional folder path to filter by
        
        Returns:
            List of document dictionaries
        """
        if folder_path is None:
            return [doc.copy() for doc in self.documents.values()]
        
        doc_ids = self.folder_tree.get_documents_in_folder(folder_path)
        return [self.documents[doc_id].copy() for doc_id in doc_ids if doc_id in self.documents]
    
    def create_folder(self, path: str) -> bool:
        """
        Create a folder.
        
        Args:
            path: Folder path
        
        Returns:
            True if created
        """
        self.folder_tree.add_folder(path)
        return True
    
    def delete_folder(self, path: str) -> bool:
        """
        Delete a folder (and move its documents to parent).
        
        Args:
            path: Folder path
        
        Returns:
            True if deleted
        """
        folder = self.folder_tree.get_folder(path)
        if not folder:
            return False
        
        # Move documents to parent folder
        doc_ids = folder.document_ids.copy()
        parent_path = folder.parent.get_path() if folder.parent else "/"
        
        for doc_id in doc_ids:
            self.move_document(doc_id, parent_path)
        
        # Delete folder
        return self.folder_tree.delete_folder(path)
    
    def list_folders(self) -> List[Dict]:
        """List all folders"""
        return self.folder_tree.traverse_dfs()
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for documents.
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of ranked document results
        """
        return self.search_engine.search(query, top_k)
    
    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions.
        
        Args:
            prefix: Prefix to complete
            limit: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        return self.search_engine.autocomplete(prefix, limit)
