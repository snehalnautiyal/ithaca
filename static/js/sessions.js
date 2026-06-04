// Ithaca — sessions sidebar
window.Ithaca = window.Ithaca || {};

Ithaca.currentSession = null;

Ithaca.loadSessions = async function() {
  const resp = await fetch('/api/sessions');
  const sessions = await resp.json();
  const list = document.getElementById('session-list');
  list.innerHTML = '';
  sessions.forEach(s => {
    const li = document.createElement('li');
    li.className = 'session-item' + (s.id === Ithaca.currentSession ? ' active' : '');
    li.innerHTML = `<span class="session-title">${Ithaca.escHtml(s.title)}</span>
      <button class="btn-icon session-del" data-id="${s.id}" title="Delete">✕</button>`;
    li.addEventListener('click', (e) => {
      if (e.target.classList.contains('session-del')) return;
      Ithaca.openSession(s.id);
    });
    li.querySelector('.session-del').addEventListener('click', () => Ithaca.deleteSession(s.id));
    list.appendChild(li);
  });
};

Ithaca.createSession = async function() {
  const resp = await fetch('/api/sessions', { method: 'POST' });
  const s = await resp.json();
  Ithaca.openSession(s.id);
  Ithaca.loadSessions();
};

Ithaca.openSession = async function(id) {
  Ithaca.currentSession = id;
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('chat-container').classList.remove('hidden');
  const resp = await fetch(`/api/sessions/${id}/messages`);
  const msgs = await resp.json();
  Ithaca.renderMessages(msgs);
  Ithaca.loadSessions(); // refresh active highlight
};

Ithaca.deleteSession = async function(id) {
  await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
  if (Ithaca.currentSession === id) {
    Ithaca.currentSession = null;
    document.getElementById('chat-container').classList.add('hidden');
    document.getElementById('empty-state').classList.remove('hidden');
    document.getElementById('messages').innerHTML = '';
  }
  Ithaca.loadSessions();
};

Ithaca.escHtml = function(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
};
