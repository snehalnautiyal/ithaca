// Ithaca — Productivity (Calendar + Notes/Tasks)
window.Ithaca = window.Ithaca || {};

Ithaca.showProductivityPage = function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  ['memory-page','docs-page','agent-page','research-page','compare-page','cookbook-page'].forEach(id => {
    const el = document.getElementById(id); if (el) el.classList.add('hidden');
  });

  let page = document.getElementById('productivity-page');
  if (!page) {
    page = document.createElement('div');
    page.id = 'productivity-page';
    page.innerHTML = `
      <div class="prod-header">
        <h2>📋 Productivity</h2>
        <div class="prod-tabs">
          <button class="btn-ghost active" id="tab-notes" onclick="Ithaca.showProdTab('notes')">Notes</button>
          <button class="btn-ghost" id="tab-calendar" onclick="Ithaca.showProdTab('calendar')">Calendar</button>
        </div>
        <button class="btn-ghost" id="prod-back">← Back</button>
      </div>
      <div id="prod-notes" class="prod-content">
        <div class="prod-add"><input id="note-input" placeholder="Add a note or task..."><button class="btn-ghost" onclick="Ithaca.addNote()">Add</button></div>
        <div id="notes-list"></div>
      </div>
      <div id="prod-calendar" class="prod-content hidden">
        <div class="prod-add">
          <input id="event-title" placeholder="Event title">
          <input id="event-start" type="datetime-local">
          <button class="btn-ghost" onclick="Ithaca.addEvent()">Add</button>
        </div>
        <div id="events-list"></div>
      </div>
    `;
    document.getElementById('main').appendChild(page);
    document.getElementById('prod-back').addEventListener('click', Ithaca.hideProductivityPage);
  }
  page.classList.remove('hidden');
  Ithaca.loadNotes();
  Ithaca.loadEvents();
};

Ithaca.hideProductivityPage = function() {
  const p = document.getElementById('productivity-page'); if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) document.getElementById('chat-container').classList.remove('hidden');
  else document.getElementById('empty-state').classList.remove('hidden');
};

Ithaca.showProdTab = function(tab) {
  document.getElementById('prod-notes').classList.toggle('hidden', tab !== 'notes');
  document.getElementById('prod-calendar').classList.toggle('hidden', tab !== 'calendar');
  document.getElementById('tab-notes').classList.toggle('active', tab === 'notes');
  document.getElementById('tab-calendar').classList.toggle('active', tab === 'calendar');
};

Ithaca.loadNotes = async function() {
  const resp = await fetch('/api/notes');
  const notes = await resp.json();
  document.getElementById('notes-list').innerHTML = notes.map(n => `
    <div class="note-item ${n.done ? 'done' : ''}">
      <input type="checkbox" ${n.done ? 'checked' : ''} onchange="Ithaca.toggleNote('${n.id}')">
      <span>${Ithaca.escHtml(n.content)}</span>
      <button class="btn-icon" onclick="Ithaca.deleteNote('${n.id}')">✕</button>
    </div>
  `).join('') || '<p class="muted">No notes yet.</p>';
};

Ithaca.addNote = async function() {
  const input = document.getElementById('note-input');
  const content = input.value.trim();
  if (!content) return;
  await fetch('/api/notes', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({content, type:'task'})});
  input.value = '';
  Ithaca.loadNotes();
};

Ithaca.toggleNote = async function(id) {
  await fetch(`/api/notes/${id}/toggle`, {method:'POST'});
  Ithaca.loadNotes();
};

Ithaca.deleteNote = async function(id) {
  await fetch(`/api/notes/${id}`, {method:'DELETE'});
  Ithaca.loadNotes();
};

Ithaca.loadEvents = async function() {
  const resp = await fetch('/api/calendar');
  const events = await resp.json();
  document.getElementById('events-list').innerHTML = events.map(e => `
    <div class="event-item">
      <span class="event-time">${e.start ? e.start.slice(0,16).replace('T',' ') : ''}</span>
      <span>${Ithaca.escHtml(e.title)}</span>
      <button class="btn-icon" onclick="Ithaca.deleteEvent('${e.id}')">✕</button>
    </div>
  `).join('') || '<p class="muted">No events yet.</p>';
};

Ithaca.addEvent = async function() {
  const title = document.getElementById('event-title').value.trim();
  const start = document.getElementById('event-start').value;
  if (!title || !start) return;
  await fetch('/api/calendar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title, start})});
  document.getElementById('event-title').value = '';
  document.getElementById('event-start').value = '';
  Ithaca.loadEvents();
};

Ithaca.deleteEvent = async function(id) {
  await fetch(`/api/calendar/${id}`, {method:'DELETE'});
  Ithaca.loadEvents();
};
