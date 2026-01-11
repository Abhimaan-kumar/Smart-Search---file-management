# Personal Smart Search & Organizer System

A production-ready, interview-grade content management system with advanced Data Structures & Algorithms implementation. This system provides fast, intelligent search with autocomplete, ranking, and caching capabilities.

## 🎯 Project Overview

This system allows users to:
- Store and manage personal documents/notes
- Organize content in hierarchical folders
- Perform fast, intelligent search with real-time autocomplete
- Get ranked search results based on relevance, recency, and usage history
- Benefit from LRU caching for optimal performance

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  (HTML/CSS/JS - User Interface)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  - Document CRUD endpoints                                   │
│  - Search & Autocomplete endpoints                           │
│  - Folder management endpoints                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Content Manager Layer                       │
│  - Document lifecycle management                             │
│  - Folder organization                                       │
│  - Integration with Search Engine                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Search Engine Core                         │
│  - Tokenization & Indexing                                   │
│  - Ranking Algorithm                                         │
│  - Autocomplete                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Data Structures Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Trie   │  │LRU Cache │  │  Heap    │  │  Tree    │   │
│  │(Autocomp)│  │(Caching) │  │(Ranking) │  │(Folders) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐                                │
│  │ HashMap  │  │ DFS/BFS  │                                │
│  │(Indexing)│  │(Traverse)│                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Data Structures & Algorithms

### 1. **Trie (Prefix Tree)**
- **Purpose**: Real-time autocomplete suggestions
- **Location**: `data_structures/trie.py`
- **Operations**:
  - `insert(word)`: O(m) where m is word length
  - `search(word)`: O(m)
  - `autocomplete(prefix)`: O(m + k) where k is number of suggestions
- **Space Complexity**: O(ALPHABET_SIZE × N × M) where N is number of words, M is average length

**Implementation Details**:
- Each node stores a HashMap of children (char → TrieNode)
- DFS traversal for collecting all words with a given prefix
- Case-insensitive word storage

### 2. **LRU Cache (Least Recently Used)**
- **Purpose**: Cache search results for O(1) retrieval
- **Location**: `data_structures/lru_cache.py`
- **Data Structure**: HashMap + Doubly Linked List
- **Operations**:
  - `get(key)`: O(1) - Moves item to head
  - `put(key, value)`: O(1) - Evicts tail if at capacity
- **Space Complexity**: O(capacity)

**Implementation Details**:
- HashMap provides O(1) key lookup
- Doubly Linked List maintains access order
- Head = most recently used, Tail = least recently used
- Automatic eviction when capacity exceeded

### 3. **Priority Queue (Heap)**
- **Purpose**: Rank search results efficiently
- **Location**: Uses Python's `heapq` module
- **Operations**:
  - `heappush`: O(log k) where k is heap size
  - `heappop`: O(log k)
  - Top-K selection: O(k × log k)
- **Space Complexity**: O(k) where k is number of results

**Implementation Details**:
- Min-heap used to maintain top-K results
- Negative scores used (heapq is min-heap, we want max)
- Efficiently maintains only the best K results

### 4. **Tree (Folder Hierarchy)**
- **Purpose**: Hierarchical folder organization
- **Location**: `data_structures/folder_tree.py`
- **Operations**:
  - `add_folder(path)`: O(h) where h is path depth
  - `get_folder(path)`: O(h)
  - `delete_folder(path)`: O(h + n) where n is descendants
  - `traverse_dfs()`: O(n) where n is total nodes
  - `traverse_bfs()`: O(n)
- **Space Complexity**: O(n) where n is number of folders

**Implementation Details**:
- Each node represents a folder
- HashMap (`folders_by_path`) for O(1) path lookup
- DFS and BFS traversal support
- Automatic parent folder creation

### 5. **HashMap (Keyword Index)**
- **Purpose**: Fast keyword-to-documents lookup
- **Location**: `core/search_engine.py`
- **Structure**: `keyword → set(document_ids)`
- **Operations**:
  - Insert: O(1) average case
  - Lookup: O(1) average case
  - Intersection (AND search): O(min(n1, n2))
- **Space Complexity**: O(V + D) where V is vocabulary size, D is documents

### 6. **DFS/BFS Traversal**
- **Purpose**: Folder tree traversal
- **Location**: `data_structures/folder_tree.py`
- **Time Complexity**: O(n) where n is number of nodes
- **Use Cases**:
  - DFS: Listing all folders in depth-first order
  - BFS: Listing folders level by level

## 🔍 Search & Ranking Algorithm

### Ranking Formula

The relevance score combines three factors:

```
Relevance = (0.5 × TF) + (0.3 × Recency) + (0.2 × Usage)
```

Where:
- **TF (Term Frequency)**: Normalized keyword frequency in document
- **Recency**: Score based on last access time (exponential decay)
- **Usage**: Score based on access frequency

### Search Process

1. **Tokenization**: Split query into lowercase keywords
2. **Index Lookup**: Find documents containing keywords (AND/OR logic)
3. **Ranking**: Calculate relevance score for each document
4. **Top-K Selection**: Use heap to select top K results
5. **Caching**: Store results in LRU cache

**Time Complexity**: O(k × log(k)) where k is number of matching documents

## 📁 Project Structure

```
smart search/
├── data_structures/
│   ├── __init__.py
│   ├── trie.py              # Trie for autocomplete
│   ├── lru_cache.py         # LRU Cache implementation
│   └── folder_tree.py       # Tree for folder hierarchy
├── core/
│   ├── __init__.py
│   ├── search_engine.py     # Search engine with ranking
│   └── content_manager.py   # Document & folder management
├── api/
│   └── main.py              # FastAPI REST endpoints
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Styling
│   └── app.js               # Frontend logic
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the backend server**:
```bash
cd api
python main.py
```

The API will be available at `http://localhost:8000`

4. **Open the frontend**:
   - Open `frontend/index.html` in a web browser
   - Or serve it using a local web server:
   ```bash
   # Using Python
   cd frontend
   python -m http.server 8080
   ```
   Then open `http://localhost:8080` in your browser

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Documents

- `POST /api/documents` - Create a document
- `GET /api/documents/{id}` - Get a document
- `PUT /api/documents/{id}` - Update a document
- `DELETE /api/documents/{id}` - Delete a document
- `GET /api/documents` - List all documents (optional `folder_path` query param)
- `POST /api/documents/{id}/move` - Move document to different folder

### Folders

- `POST /api/folders?path={path}` - Create a folder
- `DELETE /api/folders?path={path}` - Delete a folder
- `GET /api/folders` - List all folders

### Search

- `POST /api/search` - Search documents
- `POST /api/autocomplete` - Get autocomplete suggestions
- `POST /api/cache/clear` - Clear search cache

## 📝 Sample API Calls

### Create a Document

```bash
curl -X POST "http://localhost:8000/api/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Best Practices",
    "body": "Always use type hints and docstrings. Follow PEP 8 style guide.",
    "tags": ["python", "programming", "best-practices"],
    "folder_path": "/programming/python"
  }'
```

### Search Documents

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "top_k": 10
  }'
```

### Autocomplete

```bash
curl -X POST "http://localhost:8000/api/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "pyth",
    "limit": 5
  }'
```

### Create Folder

```bash
curl -X POST "http://localhost:8000/api/folders?path=/work/projects"
```

## 🧪 Testing

### Using Postman

1. Import the API endpoints into Postman
2. Test each endpoint with sample data
3. Verify responses and error handling

### Manual Testing

1. Create several documents with different content
2. Test search with various queries
3. Verify autocomplete suggestions
4. Test folder creation and organization
5. Verify ranking changes based on access patterns

## ⚡ Performance Characteristics

### Time Complexities

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Add Document | O(n) | n = number of words in document |
| Search | O(k × log(k)) | k = number of matching documents |
| Autocomplete | O(m + s) | m = prefix length, s = suggestions |
| Get Document | O(1) | HashMap lookup |
| Create Folder | O(h) | h = path depth |
| Cache Get/Put | O(1) | LRU Cache operations |

### Space Complexities

| Component | Space Complexity | Notes |
|-----------|------------------|-------|
| Trie | O(V × M) | V = vocabulary, M = avg word length |
| LRU Cache | O(capacity) | Fixed capacity |
| Keyword Index | O(V + D) | V = vocabulary, D = documents |
| Folder Tree | O(n) | n = number of folders |

## Explanations

### Why Trie for Autocomplete?

- **Fast prefix matching**: O(m) to navigate to prefix node
- **Efficient suggestions**: DFS from prefix node collects all matches
- **Space efficient**: Shared prefixes stored once
- **Scalable**: Handles large vocabularies efficiently

### Why LRU Cache?

- **O(1) operations**: HashMap + Doubly Linked List combination
- **Automatic eviction**: Removes least recently used when full
- **Memory bounded**: Fixed capacity prevents unbounded growth
- **Real-world pattern**: Used in production systems (Redis, Memcached)

### Why Heap for Ranking?

- **Efficient top-K**: Maintains only K best results, not all
- **O(k log k) complexity**: Better than sorting all results O(n log n)
- **Memory efficient**: Only stores top-K in memory
- **Standard approach**: Used in search engines (Elasticsearch, Solr)

### Why Tree for Folders?

- **Natural hierarchy**: Mirrors real-world folder structure
- **Efficient navigation**: O(h) path operations
- **Traversal support**: DFS/BFS for listing operations
- **Scalable**: Handles deep hierarchies efficiently

## 🔧 Future Enhancements

- [ ] Persistence layer (SQLite/MongoDB)
- [ ] Full-text search with stemming
- [ ] Document versioning
- [ ] User authentication
- [ ] Advanced ranking (BM25, TF-IDF)
- [ ] Search analytics
- [ ] Export/import functionality



## 👨‍💻 Author

Abhimaan Kumar

---
