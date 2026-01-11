"""
LRU (Least Recently Used) Cache Implementation

Uses HashMap + Doubly Linked List for O(1) get and put operations.

Time Complexity:
- get: O(1)
- put: O(1)

Space Complexity: O(capacity)
"""


class DoublyLinkedListNode:
    """Node in a doubly linked list"""
    
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache implementation using HashMap and Doubly Linked List.
    
    The cache maintains:
    - A HashMap for O(1) key lookup
    - A Doubly Linked List to track access order (most recent at head)
    """
    
    def __init__(self, capacity: int = 100):
        """
        Initialize LRU Cache.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # HashMap: key -> DoublyLinkedListNode
        
        # Dummy head and tail nodes for easier list manipulation
        self.head = DoublyLinkedListNode()
        self.tail = DoublyLinkedListNode()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node: DoublyLinkedListNode) -> None:
        """Add node right after head (most recently used)"""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: DoublyLinkedListNode) -> None:
        """Remove a node from the doubly linked list"""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node: DoublyLinkedListNode) -> None:
        """Move node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self) -> DoublyLinkedListNode:
        """Remove and return the least recently used node (before tail)"""
        last_node = self.tail.prev
        self._remove_node(last_node)
        return last_node
    
    def get(self, key: str) -> any:
        """
        Get value by key. Moves item to head (most recently used).
        
        Args:
            key: The key to look up
        
        Returns:
            The value associated with key, or None if not found
        
        Time Complexity: O(1)
        """
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: str, value: any) -> None:
        """
        Insert or update a key-value pair.
        
        Args:
            key: The key
            value: The value to store
        
        Time Complexity: O(1)
        """
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new node
            if len(self.cache) >= self.capacity:
                # Evict least recently used
                tail = self._pop_tail()
                del self.cache[tail.key]
            
            new_node = DoublyLinkedListNode(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache
    
    def clear(self) -> None:
        """Clear all entries from cache"""
        self.cache.clear()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def get_all_keys(self) -> list:
        """Get all keys in the cache (for debugging)"""
        return list(self.cache.keys())
