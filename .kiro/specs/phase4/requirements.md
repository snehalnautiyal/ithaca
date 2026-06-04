# Phase 4 Requirements — Documents Editor

## REQ-1: Document persistence
- Documents persist in the DB (metadata) and to `data/personal_docs/` (content files).
- Each document has: id, title, content_type (markdown|html|csv), created_at, updated_at.

## REQ-2: Multi-tab editor
- The UI supports multiple open documents as tabs.
- Syntax highlighting appropriate to the content type.

## REQ-3: AI assist
- The user can select text and request: suggest edits, continue writing, or rewrite selection.
- AI assists the author — never auto-overwrites without confirm.
- The AI suggestion is shown as an inline diff preview before applying.

## REQ-4: Diff preview
- WHEN AI suggests an edit, THEN show a before/after diff inline.
- The user MUST explicitly accept or reject the suggestion.

## REQ-5: CRUD
- Create, read, update, delete documents via `/api/documents`.
- List all documents with title and type.
