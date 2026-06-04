# Phase 4 Design — Documents Editor

## Backend

### DB model: Document
| column | type | notes |
|--------|------|-------|
| id | String PK | uuid4 |
| title | String | |
| content_type | String | markdown, html, csv |
| created_at | DateTime | |
| updated_at | DateTime | |

Content stored as files: `data/personal_docs/{id}.{ext}`

### services/docs.py
- `create_doc(title, content_type, content)` → id
- `get_doc(id)` → metadata + content
- `update_doc(id, title?, content?)` 
- `delete_doc(id)` → removes DB row + file
- `list_docs()` → metadata list

### routes/document.py
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/documents | List all |
| POST | /api/documents | Create |
| GET | /api/documents/{id} | Get with content |
| PUT | /api/documents/{id} | Update |
| DELETE | /api/documents/{id} | Delete |
| POST | /api/documents/assist | AI assist (suggest/continue/rewrite) |

### AI assist endpoint
Request: `{doc_id, selection, action: "suggest"|"continue"|"rewrite", context?}`
Response: `{original, suggestion}` — frontend shows diff

## Frontend

### static/js/documents.js
- Tab bar with open documents
- Textarea editor with basic syntax highlighting (CSS classes by content_type)
- AI assist panel: select text → choose action → see diff → accept/reject
- Diff shown as side-by-side or inline (deletions red, additions green)

### Navigation
- "Docs" button in header → documents page
- Document list sidebar within the docs page
