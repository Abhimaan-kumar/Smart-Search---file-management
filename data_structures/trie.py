"""
Trie Data Structure for Prefix-based Autocomplete

Time Complexity:
- Insert: O(m) where m is the length of the word
- Search: O(m) where m is the length of the word
- Prefix Search: O(m + k) where m is prefix length, k is number of results

Space Complexity: O(ALPHABET_SIZE * N * M) where N is number of words, M is average length
"""


class TrieNode:
    """Node in the Trie data structure"""
    
    def __init__(self):
        self.children = {}  # HashMap: char -> TrieNode
        self.is_end_of_word = False
        self.word_count = 0  # Number of words ending at this node
        self.words = []  # Store actual words for autocomplete suggestions


class Trie:
    """Trie implementation for efficient prefix search and autocomplete"""
    
    def __init__(self):
        self.root = TrieNode()
        self.total_words = 0
    
    def insert(self, word: str) -> None:
        """
        Insert a word into the Trie.
        
        Args:
            word: The word to insert (case-insensitive)
        
        Time Complexity: O(m) where m is the length of the word
        """
        if not word:
            return
        
        word = word.lower()
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        if not node.is_end_of_word:
            node.is_end_of_word = True
            self.total_words += 1
        
        node.word_count += 1
        if word not in node.words:
            node.words.append(word)
    
    def search(self, word: str) -> bool:
        """
        Check if a word exists in the Trie.
        
        Args:
            word: The word to search for
        
        Returns:
            True if word exists, False otherwise
        
        Time Complexity: O(m) where m is the length of the word
        """
        if not word:
            return False
        
        word = word.lower()
        node = self.root
        
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        
        return node.is_end_of_word
    
    def _dfs_collect_words(self, node: TrieNode, prefix: str, results: list, limit: int) -> None:
        """
        DFS traversal to collect all words with given prefix.
        
        Args:
            node: Current Trie node
            prefix: Current prefix string
            results: List to store results
            limit: Maximum number of results to collect
        """
        if len(results) >= limit:
            return
        
        if node.is_end_of_word:
            for word in node.words:
                if word not in results:
                    results.append(word)
                if len(results) >= limit:
                    return
        
        for char, child_node in sorted(node.children.items()):
            if len(results) >= limit:
                break
            self._dfs_collect_words(child_node, prefix + char, results, limit)
    
    def autocomplete(self, prefix: str, limit: int = 10) -> list:
        """
        Get autocomplete suggestions for a given prefix.
        
        Args:
            prefix: The prefix to search for
            limit: Maximum number of suggestions to return
        
        Returns:
            List of autocomplete suggestions
        
        Time Complexity: O(m + k) where m is prefix length, k is number of results
        """
        if not prefix:
            return []
        
        prefix = prefix.lower()
        node = self.root
        
        # Navigate to the prefix node
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words with this prefix using DFS
        results = []
        self._dfs_collect_words(node, prefix, results, limit)
        
        return results
    
    def get_all_words(self) -> list:
        """Get all words stored in the Trie"""
        results = []
        self._dfs_collect_words(self.root, "", results, float('inf'))
        return results
