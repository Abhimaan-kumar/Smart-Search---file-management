"""
Tree Data Structure for Hierarchical Folder Organization

Uses a tree structure where each node represents a folder.
Supports DFS and BFS traversal for folder operations.

Time Complexity:
- Add folder: O(h) where h is the depth of the path
- Get folder: O(h)
- Delete folder: O(h + n) where n is number of descendants
- Traverse: O(n) where n is total nodes

Space Complexity: O(n) where n is number of folders
"""

from typing import Optional, List, Dict, Any


class FolderNode:
    """Node in the folder tree structure"""
    
    def __init__(self, name: str, parent: Optional['FolderNode'] = None):
        self.name = name
        self.parent = parent
        self.children: Dict[str, 'FolderNode'] = {}  # HashMap: folder_name -> FolderNode
        self.document_ids: set = set()  # Set of document IDs in this folder
        self.created_at: Optional[str] = None
    
    def get_path(self) -> str:
        """Get full path of this folder (e.g., '/root/folder1/subfolder')"""
        path_parts = []
        node = self
        while node:
            path_parts.append(node.name)
            node = node.parent
        return '/'.join(reversed(path_parts))
    
    def add_child(self, name: str) -> 'FolderNode':
        """Add a child folder"""
        if name in self.children:
            return self.children[name]
        child = FolderNode(name, self)
        self.children[name] = child
        return child
    
    def remove_child(self, name: str) -> bool:
        """Remove a child folder"""
        if name in self.children:
            del self.children[name]
            return True
        return False


class FolderTree:
    """Tree structure for managing hierarchical folder organization"""
    
    def __init__(self):
        self.root = FolderNode("root")
        self.folders_by_path: Dict[str, FolderNode] = {"/": self.root}  # HashMap for fast lookup
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path (remove trailing slashes, handle root)"""
        if not path or path == "/":
            return "/"
        path = path.strip("/")
        return "/" + path
    
    def _split_path(self, path: str) -> List[str]:
        """Split path into folder names"""
        normalized = self._normalize_path(path)
        if normalized == "/":
            return []
        return normalized.split("/")[1:]  # Remove leading empty string
    
    def add_folder(self, path: str) -> FolderNode:
        """
        Add a folder at the given path. Creates parent folders if needed.
        
        Args:
            path: Full path of the folder (e.g., "/root/folder1/subfolder")
        
        Returns:
            The created or existing FolderNode
        
        Time Complexity: O(h) where h is the depth of the path
        """
        normalized_path = self._normalize_path(path)
        if normalized_path in self.folders_by_path:
            return self.folders_by_path[normalized_path]
        
        parts = self._split_path(normalized_path)
        current = self.root
        
        # Navigate/create path
        current_path = "/"
        for part in parts:
            if current_path == "/":
                current_path = "/" + part
            else:
                current_path = current_path + "/" + part
            
            if part in current.children:
                current = current.children[part]
            else:
                current = current.add_child(part)
                self.folders_by_path[current_path] = current
        
        return current
    
    def get_folder(self, path: str) -> Optional[FolderNode]:
        """
        Get folder node at the given path.
        
        Args:
            path: Full path of the folder
        
        Returns:
            FolderNode if found, None otherwise
        
        Time Complexity: O(h) where h is the depth of the path
        """
        normalized_path = self._normalize_path(path)
        return self.folders_by_path.get(normalized_path)
    
    def delete_folder(self, path: str) -> bool:
        """
        Delete a folder and all its descendants.
        
        Args:
            path: Full path of the folder to delete
        
        Returns:
            True if deleted, False if not found
        
        Time Complexity: O(h + n) where h is depth, n is number of descendants
        """
        normalized_path = self._normalize_path(path)
        if normalized_path == "/":
            return False  # Cannot delete root
        
        folder = self.folders_by_path.get(normalized_path)
        if not folder:
            return False
        
        # Remove from parent
        if folder.parent:
            folder.parent.remove_child(folder.name)
        
        # Remove all descendants from folders_by_path using DFS
        def remove_descendants(node: FolderNode):
            current_path = node.get_path()
            if current_path in self.folders_by_path:
                del self.folders_by_path[current_path]
            for child in node.children.values():
                remove_descendants(child)
        
        remove_descendants(folder)
        return True
    
    def add_document_to_folder(self, path: str, document_id: str) -> bool:
        """Add a document ID to a folder"""
        folder = self.get_folder(path)
        if folder:
            folder.document_ids.add(document_id)
            return True
        return False
    
    def remove_document_from_folder(self, path: str, document_id: str) -> bool:
        """Remove a document ID from a folder"""
        folder = self.get_folder(path)
        if folder:
            folder.document_ids.discard(document_id)
            return True
        return False
    
    def get_documents_in_folder(self, path: str) -> set:
        """Get all document IDs in a folder"""
        folder = self.get_folder(path)
        if folder:
            return folder.document_ids.copy()
        return set()
    
    def traverse_dfs(self, node: Optional[FolderNode] = None, result: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        DFS traversal of the folder tree.
        
        Returns:
            List of folder information dictionaries
        """
        if result is None:
            result = []
        if node is None:
            node = self.root
        
        result.append({
            "path": node.get_path(),
            "name": node.name,
            "document_count": len(node.document_ids),
            "children_count": len(node.children)
        })
        
        for child in node.children.values():
            self.traverse_dfs(child, result)
        
        return result
    
    def traverse_bfs(self) -> List[Dict[str, Any]]:
        """
        BFS traversal of the folder tree.
        
        Returns:
            List of folder information dictionaries
        """
        from collections import deque
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append({
                "path": node.get_path(),
                "name": node.name,
                "document_count": len(node.document_ids),
                "children_count": len(node.children)
            })
            
            for child in node.children.values():
                queue.append(child)
        
        return result
