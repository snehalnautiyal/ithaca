// Ithaca — Documents page
window.Ithaca = window.Ithaca || {};

Ithaca.openDocs = [];  // [{id, title, content_type}]
Ithaca.activeDoc = null;

Ithaca.showDocsPage = async function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  const memPage = document.getElementById('memory-page');
  if (memPage) memPage.classList.add('hidden');

  let docsPage = document.getElementById('docs-page');
  if (!docsPage) {
    docsPage = document.createElement('div');
    docsPage.id = 'docs-page';
    docsPage.innerHTML = `
      <div class="docs-header">
        <h2>Documents</h2>
        <div class="docs-actions">
          <select id="doc-type-select"><option value="markdown">Markdown</option><option value="html">HTML</option><option value="csv">CSV</option></select>
          <button class="btn-ghost" id="doc-new">+ New</button>
          <button class="btn-ghost" id="doc-back">← Back</button>
        </div>
      </div>
      <div class="docs-layout">
        <div class="docs-sidebar">
          <ul id="doc-list"></ul>
        </div>
        <div class="docs-editor-area">
          <div id="doc-tabs" class="doc-tabs"></div>
          <textarea id="doc-editor" class="doc-editor hidden" placeholder="Start writing..."></textarea>
          <div id="doc-assist-bar" class="doc-assist-bar hidden">
            <select id="assist-action"><option value="suggest">Suggest edits</option><option value="continue">Continue</option><option value="rewrite">Rewrite</option></select>
            <button class="btn-ghost" id="assist-run">AI Assist</button>
          </div>
          <div id="doc-diff" class="doc-diff hidden"></div>
          <div id="doc-empty" class="muted">Select or create a document.</div>
        </div>
      </div>
    `;
    document.getElementById('main').appendChild(docsPage);

    document.getElementById('doc-back').addEventListener('click', Ithaca.hideDocsPage);
    document.getElementById('doc-new').addEventListener('click', Ithaca.createDoc);
    document.getElementById('doc-editor').addEventListener('input', Ithaca.autoSaveDoc);
    document.getElementById('assist-run').addEventListener('click', Ithaca.runAssist);
  }
  docsPage.classList.remove('hidden');
  Ithaca.loadDocList();
};

Ithaca.hideDocsPage = function() {
  const p = document.getElementById('docs-page');
  if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) {
    document.getElementById('chat-container').classList.remove('hidden');
  } else {
    document.getElementById('empty-state').classList.remove('hidden');
  }
};

Ithaca.loadDocList = async function() {
  const resp = await fetch('/api/documents');
  const docs = await resp.json();
  const list = document.getElementById('doc-list');
  list.innerHTML = docs.map(d => `
    <li class="doc-item${d.id === Ithaca.activeDoc ? ' active' : ''}" data-id="${d.id}">
      <span>${Ithaca.escHtml(d.title)}</span>
      <button class="btn-icon doc-del" data-id="${d.id}">✕</button>
    </li>`).join('');
  list.querySelectorAll('.doc-item').forEach(li => {
    li.addEventListener('click', (e) => {
      if (e.target.classList.contains('doc-del')) return;
      Ithaca.openDoc(li.dataset.id);
    });
  });
  list.querySelectorAll('.doc-del').forEach(btn => {
    btn.addEventListener('click', () => Ithaca.deleteDoc(btn.dataset.id));
  });
};

Ithaca.createDoc = async function() {
  const type = document.getElementById('doc-type-select').value;
  const resp = await fetch('/api/documents', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: 'Untitled', content_type: type}),
  });
  const doc = await resp.json();
  Ithaca.openDoc(doc.id);
  Ithaca.loadDocList();
};

Ithaca.openDoc = async function(id) {
  const resp = await fetch(`/api/documents/${id}`);
  const doc = await resp.json();
  Ithaca.activeDoc = id;
  document.getElementById('doc-editor').value = doc.content;
  document.getElementById('doc-editor').classList.remove('hidden');
  document.getElementById('doc-assist-bar').classList.remove('hidden');
  document.getElementById('doc-diff').classList.add('hidden');
  document.getElementById('doc-empty').classList.add('hidden');
  Ithaca.loadDocList();
};

Ithaca._saveTimeout = null;
Ithaca.autoSaveDoc = function() {
  clearTimeout(Ithaca._saveTimeout);
  Ithaca._saveTimeout = setTimeout(async () => {
    if (!Ithaca.activeDoc) return;
    const content = document.getElementById('doc-editor').value;
    await fetch(`/api/documents/${Ithaca.activeDoc}`, {
      method: 'PUT', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({content}),
    });
  }, 1000);
};

Ithaca.deleteDoc = async function(id) {
  await fetch(`/api/documents/${id}`, {method: 'DELETE'});
  if (Ithaca.activeDoc === id) {
    Ithaca.activeDoc = null;
    document.getElementById('doc-editor').classList.add('hidden');
    document.getElementById('doc-assist-bar').classList.add('hidden');
    document.getElementById('doc-empty').classList.remove('hidden');
  }
  Ithaca.loadDocList();
};

Ithaca.runAssist = async function() {
  const editor = document.getElementById('doc-editor');
  const selection = editor.value.substring(editor.selectionStart, editor.selectionEnd);
  if (!selection) { alert('Select some text first.'); return; }
  const action = document.getElementById('assist-action').value;

  const resp = await fetch('/api/documents/assist', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({doc_id: Ithaca.activeDoc, selection, action}),
  });
  if (!resp.ok) { alert('AI assist failed.'); return; }
  const data = await resp.json();
  Ithaca.showDiff(data.original, data.suggestion, editor.selectionStart, editor.selectionEnd);
};

Ithaca.showDiff = function(original, suggestion, start, end) {
  const diffDiv = document.getElementById('doc-diff');
  diffDiv.classList.remove('hidden');
  diffDiv.innerHTML = `
    <div class="diff-header">AI Suggestion <button class="btn-ghost diff-accept">✓ Accept</button> <button class="btn-ghost diff-reject">✗ Reject</button></div>
    <div class="diff-content">
      <div class="diff-del">${Ithaca.escHtml(original)}</div>
      <div class="diff-add">${Ithaca.escHtml(suggestion)}</div>
    </div>`;
  diffDiv.querySelector('.diff-accept').addEventListener('click', () => {
    const editor = document.getElementById('doc-editor');
    const val = editor.value;
    editor.value = val.substring(0, start) + suggestion + val.substring(end);
    diffDiv.classList.add('hidden');
    Ithaca.autoSaveDoc();
  });
  diffDiv.querySelector('.diff-reject').addEventListener('click', () => {
    diffDiv.classList.add('hidden');
  });
};
