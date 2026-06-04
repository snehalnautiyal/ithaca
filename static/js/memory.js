// Ithaca — Memory page
window.Ithaca = window.Ithaca || {};

Ithaca.showMemoryPage = async function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  const main = document.getElementById('main');

  // Create or show memory page
  let memPage = document.getElementById('memory-page');
  if (!memPage) {
    memPage = document.createElement('div');
    memPage.id = 'memory-page';
    memPage.innerHTML = `
      <div class="memory-header">
        <h2>Memories</h2>
        <div class="memory-actions">
          <button class="btn-ghost" id="mem-export">Export</button>
          <label class="btn-ghost" style="cursor:pointer">Import<input type="file" id="mem-import-file" accept=".json" hidden></label>
          <button class="btn-ghost" id="mem-back">← Back</button>
        </div>
      </div>
      <div class="memory-search">
        <input id="mem-search-input" type="text" placeholder="Search memories...">
        <button class="btn-ghost" id="mem-search-btn">Search</button>
      </div>
      <div id="memory-list"></div>
      <div class="memory-add">
        <input id="mem-add-input" type="text" placeholder="Add a memory manually...">
        <button class="btn-ghost" id="mem-add-btn">Add</button>
      </div>
    `;
    main.appendChild(memPage);

    document.getElementById('mem-back').addEventListener('click', Ithaca.hideMemoryPage);
    document.getElementById('mem-search-btn').addEventListener('click', Ithaca.searchMemories);
    document.getElementById('mem-search-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') Ithaca.searchMemories();
    });
    document.getElementById('mem-add-btn').addEventListener('click', Ithaca.addMemoryManual);
    document.getElementById('mem-export').addEventListener('click', Ithaca.exportMemories);
    document.getElementById('mem-import-file').addEventListener('change', Ithaca.importMemories);
  }

  memPage.classList.remove('hidden');
  Ithaca.loadMemories();
};

Ithaca.hideMemoryPage = function() {
  const memPage = document.getElementById('memory-page');
  if (memPage) memPage.classList.add('hidden');
  if (Ithaca.currentSession) {
    document.getElementById('chat-container').classList.remove('hidden');
  } else {
    document.getElementById('empty-state').classList.remove('hidden');
  }
};

Ithaca.loadMemories = async function() {
  const resp = await fetch('/api/memories?limit=200');
  const memories = await resp.json();
  Ithaca.renderMemoryList(memories);
};

Ithaca.searchMemories = async function() {
  const q = document.getElementById('mem-search-input').value.trim();
  if (!q) { Ithaca.loadMemories(); return; }
  const resp = await fetch(`/api/memories/search?q=${encodeURIComponent(q)}&n=20`);
  const results = await resp.json();
  Ithaca.renderMemoryList(results);
};

Ithaca.renderMemoryList = function(memories) {
  const list = document.getElementById('memory-list');
  if (!memories.length) {
    list.innerHTML = '<p class="muted">No memories yet.</p>';
    return;
  }
  list.innerHTML = memories.map(m => `
    <div class="memory-item" data-id="${m.id}">
      <span class="memory-content">${Ithaca.escHtml(m.content)}</span>
      <div class="memory-item-actions">
        <button class="btn-icon mem-edit" data-id="${m.id}" title="Edit">✎</button>
        <button class="btn-icon mem-del" data-id="${m.id}" title="Delete">✕</button>
      </div>
    </div>
  `).join('');

  list.querySelectorAll('.mem-del').forEach(btn => {
    btn.addEventListener('click', () => Ithaca.deleteMemoryUI(btn.dataset.id));
  });
  list.querySelectorAll('.mem-edit').forEach(btn => {
    btn.addEventListener('click', () => Ithaca.editMemoryUI(btn.dataset.id));
  });
};

Ithaca.deleteMemoryUI = async function(id) {
  await fetch(`/api/memories/${id}`, { method: 'DELETE' });
  Ithaca.loadMemories();
};

Ithaca.editMemoryUI = async function(id) {
  const item = document.querySelector(`.memory-item[data-id="${id}"] .memory-content`);
  const current = item.textContent;
  const newContent = prompt('Edit memory:', current);
  if (newContent && newContent !== current) {
    await fetch(`/api/memories/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newContent }),
    });
    Ithaca.loadMemories();
  }
};

Ithaca.addMemoryManual = async function() {
  const input = document.getElementById('mem-add-input');
  const content = input.value.trim();
  if (!content) return;
  await fetch('/api/memories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, type: 'manual' }),
  });
  input.value = '';
  Ithaca.loadMemories();
};

Ithaca.exportMemories = async function() {
  const resp = await fetch('/api/memories/export');
  const data = await resp.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'ithaca-memories.json'; a.click();
  URL.revokeObjectURL(url);
};

Ithaca.importMemories = async function(e) {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  const memories = JSON.parse(text);
  await fetch('/api/memories/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memories: Array.isArray(memories) ? memories : memories.memories || [] }),
  });
  Ithaca.loadMemories();
  e.target.value = '';
};
