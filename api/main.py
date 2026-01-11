"""
FastAPI Backend for Personal Smart Search & Organizer System

REST API endpoints for content management, search, and folder operations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from core.content_manager import ContentManager
from core.search_engine import SearchEngine

# Initialize FastAPI app
app = FastAPI(
    title="Personal Smart Search & Organizer API",
    description="A production-ready search and organization system with advanced DSA",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize content manager with search engine
search_engine = SearchEngine(cache_capacity=100)
content_manager = ContentManager(search_engine)


# Pydantic models for request/response
class DocumentCreate(BaseModel):
    title: str
    body: str
    tags: Optional[List[str]] = []
    folder_path: str = "/"


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentMove(BaseModel):
    new_folder_path: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


class AutocompleteRequest(BaseModel):
    prefix: str
    limit: int = 10


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Personal Smart Search & Organizer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Document endpoints
@app.post("/api/documents", response_model=dict)
async def create_document(doc: DocumentCreate):
    """
    Create a new document.
    
    Time Complexity: O(n) where n is number of words in document
    """
    try:
        document = content_manager.add_document(
            title=doc.title,
            body=doc.body,
            tags=doc.tags,
            folder_path=doc.folder_path
        )
        return {"success": True, "document": document}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}", response_model=dict)
async def get_document(document_id: str):
    """
    Get a document by ID.
    
    Time Complexity: O(1)
    """
    document = content_manager.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "document": document}


@app.put("/api/documents/{document_id}", response_model=dict)
async def update_document(document_id: str, doc: DocumentUpdate):
    """
    Update a document.
    
    Time Complexity: O(n) where n is number of words in document
    """
    document = content_manager.update_document(
        document_id=document_id,
        title=doc.title,
        body=doc.body,
        tags=doc.tags
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "document": document}


@app.delete("/api/documents/{document_id}", response_model=dict)
async def delete_document(document_id: str):
    """
    Delete a document.
    
    Time Complexity: O(1)
    """
    success = content_manager.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "message": "Document deleted"}


@app.get("/api/documents", response_model=dict)
async def list_documents(folder_path: Optional[str] = None):
    """
    List all documents, optionally filtered by folder.
    
    Time Complexity: O(d) where d is number of documents
    """
    documents = content_manager.list_documents(folder_path)
    return {"success": True, "documents": documents, "count": len(documents)}


@app.post("/api/documents/{document_id}/move", response_model=dict)
async def move_document(document_id: str, move: DocumentMove):
    """
    Move a document to a different folder.
    
    Time Complexity: O(1)
    """
    success = content_manager.move_document(document_id, move.new_folder_path)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "message": "Document moved"}


# Folder endpoints
@app.post("/api/folders", response_model=dict)
async def create_folder(path: str):
    """
    Create a folder.
    
    Time Complexity: O(h) where h is depth of path
    """
    success = content_manager.create_folder(path)
    return {"success": True, "message": "Folder created"}


@app.delete("/api/folders", response_model=dict)
async def delete_folder(path: str):
    """
    Delete a folder.
    
    Time Complexity: O(h + n) where h is depth, n is number of descendants
    """
    success = content_manager.delete_folder(path)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"success": True, "message": "Folder deleted"}


@app.get("/api/folders", response_model=dict)
async def list_folders():
    """
    List all folders.
    
    Time Complexity: O(n) where n is number of folders
    """
    folders = content_manager.list_folders()
    return {"success": True, "folders": folders, "count": len(folders)}


# Search endpoints
@app.post("/api/search", response_model=dict)
async def search(request: SearchRequest):
    """
    Search for documents.
    
    Time Complexity: O(k * log(k)) where k is number of matching documents
    """
    results = content_manager.search(request.query, request.top_k)
    return {
        "success": True,
        "query": request.query,
        "results": results,
        "count": len(results)
    }


@app.post("/api/autocomplete", response_model=dict)
async def autocomplete(request: AutocompleteRequest):
    """
    Get autocomplete suggestions.
    
    Time Complexity: O(m + s) where m is prefix length, s is number of suggestions
    """
    suggestions = content_manager.autocomplete(request.prefix, request.limit)
    return {
        "success": True,
        "prefix": request.prefix,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@app.post("/api/cache/clear", response_model=dict)
async def clear_cache():
    """Clear the search cache"""
    content_manager.search_engine.clear_cache()
    return {"success": True, "message": "Cache cleared"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
