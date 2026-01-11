// API Base URL
const API_BASE = 'http://localhost:8000/api';

// State
let currentDocuments = [];
let currentFolders = [];
let allTags = new Set();
let currentEditingDocId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadDocuments();
    loadFolders();
    updateStatistics();
});

// Event Listeners
function setupEventListeners() {
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.closest('.tab-btn').dataset.tab;
            switchTab(tabName);
        });
    });

    // Search
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    searchInput.addEventListener('input', handleAutocomplete);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    searchBtn.addEventListener('click', performSearch);

    // Create document form
    document.getElementById('createDocumentForm').addEventListener('submit', handleCreateDocument);

    // Edit document form
    document.getElementById('editDocumentForm').addEventListener('submit', handleUpdateDocument);

    // Filters
    document.getElementById('folderFilter').addEventListener('change', applyFilters);
    document.getElementById('tagFilter').addEventListener('change', applyFilters);
    document.getElementById('sortFilter').addEventListener('change', applyFilters);
    document.getElementById('clearFiltersBtn').addEventListener('click', clearFilters);

    // Folder operations
    document.getElementById('createFolderBtn').addEventListener('click', handleCreateFolder);

    // Modal actions
    document.getElementById('editDocBtn').addEventListener('click', enableEditMode);
    document.getElementById('deleteDocBtn').addEventListener('click', handleDeleteDocument);
    document.getElementById('cancelEditBtn').addEventListener('click', disableEditMode);
    document.querySelector('.close').addEventListener('click', closeModal);

    window.addEventListener('click', (e) => {
        const modal = document.getElementById('documentModal');
        if (e.target === modal) {
            closeModal();
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
        }
    });
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const tabBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabBtn) {
        tabBtn.classList.add('active');
    }
    
    const tabContent = document.getElementById(`${tabName}Tab`);
    if (tabContent) {
        tabContent.classList.add('active');
    }

    // Scroll to section for Create, Folders, and Statistics tabs
    if (tabName === 'create') {
        scrollToSection('createSection');
    } else if (tabName === 'folders') {
        scrollToSection('foldersSection');
    } else if (tabName === 'stats') {
        scrollToSection('statsSection');
        updateStatistics();
    }
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const offset = 100; // Offset from top to account for fixed headers
        const elementPosition = section.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

// Autocomplete
let autocompleteTimeout;
async function handleAutocomplete(e) {
    const prefix = e.target.value.trim();
    
    clearTimeout(autocompleteTimeout);
    
    if (prefix.length < 2) {
        document.getElementById('autocompleteResults').style.display = 'none';
        return;
    }

    autocompleteTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE}/autocomplete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prefix, limit: 10 })
            });
            const data = await response.json();
            
            if (data.success && data.suggestions.length > 0) {
                displayAutocomplete(data.suggestions);
            } else {
                document.getElementById('autocompleteResults').style.display = 'none';
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
        }
    }, 300);
}

function displayAutocomplete(suggestions) {
    const container = document.getElementById('autocompleteResults');
    container.innerHTML = suggestions.map(suggestion => 
        `<div class="autocomplete-item" onclick="selectAutocomplete('${escapeHtml(suggestion)}')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
            </svg>
            ${escapeHtml(suggestion)}
        </div>`
    ).join('');
    container.style.display = 'block';
}

function selectAutocomplete(suggestion) {
    document.getElementById('searchInput').value = suggestion;
    document.getElementById('autocompleteResults').style.display = 'none';
    performSearch();
}

// Search
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    document.getElementById('autocompleteResults').style.display = 'none';
    
    showToast('Searching...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: 10 })
        });
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results, query);
            showToast(`Found ${data.results.length} results`, 'success');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed. Make sure the API server is running.', 'error');
    }
}

function displaySearchResults(results, query) {
    const container = document.getElementById('searchResults');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">No results found for "${escapeHtml(query)}"</div>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <h3>Search Results for "${escapeHtml(query)}" (${results.length})</h3>
        ${results.map(result => `
            <div class="result-item" onclick="showDocumentDetails('${result.id}')">
                <div class="result-title">${escapeHtml(result.title)}</div>
                <div class="result-body">${escapeHtml(result.body.substring(0, 150))}...</div>
                <div class="result-meta">
                    <span class="result-score">⭐ Relevance: ${result.relevance_score}</span>
                    <span>🏷️ ${result.tags && result.tags.length > 0 ? result.tags.join(', ') : 'No tags'}</span>
                    <span>📁 ${result.folder_path || '/'}</span>
                </div>
            </div>
        `).join('')}
    `;
}

// Documents
async function loadDocuments(folderPath = null) {
    try {
        const url = folderPath 
            ? `${API_BASE}/documents?folder_path=${encodeURIComponent(folderPath)}`
            : `${API_BASE}/documents`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentDocuments = data.documents;
            extractTags(data.documents);
            applyFilters();
            updateHeaderStats();
        }
    } catch (error) {
        console.error('Load documents error:', error);
        showToast('Failed to load documents. Make sure the API server is running.', 'error');
    }
}

function extractTags(documents) {
    allTags.clear();
    documents.forEach(doc => {
        if (doc.tags && doc.tags.length > 0) {
            doc.tags.forEach(tag => allTags.add(tag));
        }
    });
    updateTagFilter();
}

function updateTagFilter() {
    const tagFilter = document.getElementById('tagFilter');
    const currentValue = tagFilter.value;
    
    tagFilter.innerHTML = '<option value="">All tags</option>' +
        Array.from(allTags).sort().map(tag => 
            `<option value="${escapeHtml(tag)}">${escapeHtml(tag)}</option>`
        ).join('');
    
    tagFilter.value = currentValue;
}

function applyFilters() {
    const folderFilter = document.getElementById('folderFilter').value;
    const tagFilter = document.getElementById('tagFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    
    let filtered = [...currentDocuments];
    
    // Filter by folder
    if (folderFilter) {
        filtered = filtered.filter(doc => doc.folder_path === folderFilter);
    }
    
    // Filter by tag
    if (tagFilter) {
        filtered = filtered.filter(doc => 
            doc.tags && doc.tags.includes(tagFilter)
        );
    }
    
    // Sort
    filtered.sort((a, b) => {
        switch(sortFilter) {
            case 'recent':
                return new Date(b.last_accessed || b.created_at) - new Date(a.last_accessed || a.created_at);
            case 'oldest':
                return new Date(a.created_at) - new Date(b.created_at);
            case 'title':
                return a.title.localeCompare(b.title);
            default:
                return 0;
        }
    });
    
    displayDocuments(filtered);
}

function clearFilters() {
    document.getElementById('folderFilter').value = '';
    document.getElementById('tagFilter').value = '';
    document.getElementById('sortFilter').value = 'recent';
    applyFilters();
}

function displayDocuments(documents) {
    const container = document.getElementById('documentsList');
    
    if (documents.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">📄</div>
                <div class="empty-state-text">No documents found</div>
            </div>
        `;
        return;
    }

    container.innerHTML = documents.map(doc => `
        <div class="document-card">
            <div class="document-card-actions">
                <button class="card-action-btn edit" onclick="event.stopPropagation(); editDocument('${doc.id}')" title="Edit">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </button>
                <button class="card-action-btn delete" onclick="event.stopPropagation(); confirmDeleteDocument('${doc.id}')" title="Delete">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
            <div class="document-title" onclick="showDocumentDetails('${doc.id}')">${escapeHtml(doc.title)}</div>
            <div class="document-preview" onclick="showDocumentDetails('${doc.id}')">${escapeHtml(doc.body.substring(0, 100))}...</div>
            ${doc.tags && doc.tags.length > 0 ? `
                <div class="document-tags">
                    ${doc.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
            <div class="document-meta">
                <span>📁 ${escapeHtml(doc.folder_path || '/')}</span>
                <span>📅 ${formatDate(doc.created_at)}</span>
            </div>
        </div>
    `).join('');
}

// Folders
async function loadFolders() {
    try {
        const response = await fetch(`${API_BASE}/folders`);
        const data = await response.json();
        
        if (data.success) {
            currentFolders = data.folders;
            displayFolders(data.folders);
            updateFolderFilter(data.folders);
            updateHeaderStats();
        }
    } catch (error) {
        console.error('Load folders error:', error);
    }
}

function displayFolders(folders) {
    const container = document.getElementById('foldersList');
    
    if (folders.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📁</div><div class="empty-state-text">No folders found</div></div>';
        return;
    }

    container.innerHTML = folders.map(folder => `
        <div class="folder-item">
            <div>
                <div class="folder-path">${escapeHtml(folder.path)}</div>
                <div class="folder-info">
                    ${folder.document_count} documents, ${folder.children_count} subfolders
                </div>
            </div>
            ${folder.path !== '/' ? `
                <div class="folder-actions-btn">
                    <button class="btn-danger" onclick="deleteFolder('${folder.path}')">Delete</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function updateFolderFilter(folders) {
    const select = document.getElementById('folderFilter');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">All folders</option>' +
        folders.map(f => `<option value="${f.path}">${f.path}</option>`).join('');
    
    select.value = currentValue;
}

// Create Document
async function handleCreateDocument(e) {
    e.preventDefault();
    
    const title = document.getElementById('docTitle').value;
    const body = document.getElementById('docBody').value;
    const tags = document.getElementById('docTags').value
        .split(',')
        .map(t => t.trim())
        .filter(t => t);
    const folderPath = document.getElementById('docFolder').value || '/';
    
    try {
        const response = await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, body, tags, folder_path: folderPath })
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Document created successfully!', 'success');
            document.getElementById('createDocumentForm').reset();
            document.getElementById('docFolder').value = '/';
            loadDocuments();
            loadFolders();
            switchTab('documents');
        }
    } catch (error) {
        console.error('Create document error:', error);
        showToast('Failed to create document.', 'error');
    }
}

// Update Document
async function handleUpdateDocument(e) {
    e.preventDefault();
    
    if (!currentEditingDocId) return;
    
    const title = document.getElementById('editDocTitle').value;
    const body = document.getElementById('editDocBody').value;
    const tags = document.getElementById('editDocTags').value
        .split(',')
        .map(t => t.trim())
        .filter(t => t);
    
    try {
        const response = await fetch(`${API_BASE}/documents/${currentEditingDocId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, body, tags })
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Document updated successfully!', 'success');
            disableEditMode();
            showDocumentDetails(currentEditingDocId);
            loadDocuments();
        }
    } catch (error) {
        console.error('Update document error:', error);
        showToast('Failed to update document.', 'error');
    }
}

// Delete Document
async function handleDeleteDocument() {
    if (!currentEditingDocId) return;
    
    if (!confirm(`Are you sure you want to delete this document? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/${currentEditingDocId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Document deleted successfully!', 'success');
            closeModal();
            loadDocuments();
            loadFolders();
        }
    } catch (error) {
        console.error('Delete document error:', error);
        showToast('Failed to delete document.', 'error');
    }
}

function confirmDeleteDocument(docId) {
    if (!confirm(`Are you sure you want to delete this document? This action cannot be undone.`)) {
        return;
    }
    
    handleDeleteDocumentById(docId);
}

async function handleDeleteDocumentById(docId) {
    try {
        const response = await fetch(`${API_BASE}/documents/${docId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Document deleted successfully!', 'success');
            loadDocuments();
            loadFolders();
        }
    } catch (error) {
        console.error('Delete document error:', error);
        showToast('Failed to delete document.', 'error');
    }
}

// Create Folder
async function handleCreateFolder() {
    const path = document.getElementById('newFolderPath').value.trim();
    if (!path) {
        showToast('Please enter a folder path', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/folders?path=${encodeURIComponent(path)}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Folder created successfully!', 'success');
            document.getElementById('newFolderPath').value = '';
            loadFolders();
        }
    } catch (error) {
        console.error('Create folder error:', error);
        showToast('Failed to create folder.', 'error');
    }
}

// Delete Folder
async function deleteFolder(path) {
    if (!confirm(`Delete folder "${path}"? Documents will be moved to parent folder.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/folders?path=${encodeURIComponent(path)}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Folder deleted successfully!', 'success');
            loadFolders();
            loadDocuments();
        }
    } catch (error) {
        console.error('Delete folder error:', error);
        showToast('Failed to delete folder.', 'error');
    }
}

// Show Document Details
async function showDocumentDetails(docId) {
    try {
        const response = await fetch(`${API_BASE}/documents/${docId}`);
        const data = await response.json();
        
        if (data.success) {
            const doc = data.document;
            currentEditingDocId = doc.id;
            
            document.getElementById('modalTitle').textContent = doc.title;
            document.getElementById('modalBody').innerHTML = `
                <div class="modal-detail">
                    <label>Content:</label>
                    <div class="modal-detail-content">${escapeHtml(doc.body).replace(/\n/g, '<br>')}</div>
                </div>
                <div class="modal-detail">
                    <label>Tags:</label>
                    <div class="modal-detail-content">
                        ${doc.tags && doc.tags.length > 0 ? doc.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ') : '<span style="color: var(--text-tertiary);">No tags</span>'}
                    </div>
                </div>
                <div class="modal-detail">
                    <label>Folder:</label>
                    <div class="modal-detail-content">${escapeHtml(doc.folder_path || '/')}</div>
                </div>
                <div class="modal-detail">
                    <label>Created:</label>
                    <div class="modal-detail-content">${formatDate(doc.created_at)}</div>
                </div>
                <div class="modal-detail">
                    <label>Last Accessed:</label>
                    <div class="modal-detail-content">${formatDate(doc.last_accessed)}</div>
                </div>
            `;
            
            // Populate edit form
            document.getElementById('editDocTitle').value = doc.title;
            document.getElementById('editDocBody').value = doc.body;
            document.getElementById('editDocTags').value = doc.tags ? doc.tags.join(', ') : '';
            document.getElementById('editDocFolder').value = doc.folder_path || '/';
            
            disableEditMode();
            document.getElementById('documentModal').style.display = 'block';
            loadDocuments(); // Refresh to update last_accessed
        }
    } catch (error) {
        console.error('Get document error:', error);
        showToast('Failed to load document details.', 'error');
    }
}

function editDocument(docId) {
    showDocumentDetails(docId);
    setTimeout(() => enableEditMode(), 100);
}

function enableEditMode() {
    document.getElementById('modalBody').style.display = 'none';
    document.getElementById('modalEditForm').style.display = 'block';
}

function disableEditMode() {
    document.getElementById('modalBody').style.display = 'block';
    document.getElementById('modalEditForm').style.display = 'none';
}

function closeModal() {
    document.getElementById('documentModal').style.display = 'none';
    currentEditingDocId = null;
    disableEditMode();
}

// Statistics
async function updateStatistics() {
    try {
        const docsResponse = await fetch(`${API_BASE}/documents`);
        const docsData = await docsResponse.json();
        
        const foldersResponse = await fetch(`${API_BASE}/folders`);
        const foldersData = await foldersResponse.json();
        
        if (docsData.success && foldersData.success) {
            const documents = docsData.documents;
            const folders = foldersData.folders;
            
            // Update stat cards
            document.getElementById('statTotalDocs').textContent = documents.length;
            document.getElementById('statTotalFolders').textContent = folders.length;
            
            // Count unique tags
            const tags = new Set();
            documents.forEach(doc => {
                if (doc.tags) {
                    doc.tags.forEach(tag => tags.add(tag));
                }
            });
            document.getElementById('statTotalTags').textContent = tags.size;
            
            // Cache size (we don't have an endpoint for this, so we'll estimate)
            document.getElementById('statCacheSize').textContent = '~' + Math.min(100, Math.floor(documents.length / 10));
            
            // Show recent documents
            const recentDocs = documents
                .sort((a, b) => new Date(b.last_accessed || b.created_at) - new Date(a.last_accessed || a.created_at))
                .slice(0, 5);
            
            displayRecentDocuments(recentDocs);
        }
    } catch (error) {
        console.error('Update statistics error:', error);
    }
}

function displayRecentDocuments(docs) {
    const container = document.getElementById('recentDocuments');
    
    if (docs.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-text">No recent documents</div></div>';
        return;
    }
    
    container.innerHTML = docs.map(doc => `
        <div class="recent-doc-item" onclick="showDocumentDetails('${doc.id}')">
            <div style="font-weight: 600; margin-bottom: 4px;">${escapeHtml(doc.title)}</div>
            <div style="font-size: 0.85em; color: var(--text-tertiary);">
                ${formatDate(doc.last_accessed || doc.created_at)} • ${escapeHtml(doc.folder_path || '/')}
            </div>
        </div>
    `).join('');
}

function updateHeaderStats() {
    document.getElementById('totalDocs').textContent = currentDocuments.length;
    document.getElementById('totalFolders').textContent = currentFolders.length;
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 7) {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, type === 'error' ? 5000 : 3000);
}
