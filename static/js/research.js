// Ithaca — Research UI
window.Ithaca = window.Ithaca || {};

Ithaca.showResearchPage = function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  ['memory-page','docs-page','agent-page'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });

  let page = document.getElementById('research-page');
  if (!page) {
    page = document.createElement('div');
    page.id = 'research-page';
    page.innerHTML = `
      <div class="research-header">
        <h2>🔬 Deep Research</h2>
        <button class="btn-ghost" id="research-back">← Back</button>
      </div>
      <div class="research-input-area">
        <input id="research-input" type="text" placeholder="Ask a research question...">
        <button class="btn-ghost" id="research-run">Research</button>
      </div>
      <div id="research-progress" class="research-progress"></div>
      <div id="research-report" class="research-report hidden"></div>
    `;
    document.getElementById('main').appendChild(page);
    document.getElementById('research-back').addEventListener('click', Ithaca.hideResearchPage);
    document.getElementById('research-run').addEventListener('click', Ithaca.runResearch);
    document.getElementById('research-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') Ithaca.runResearch();
    });
  }
  page.classList.remove('hidden');
};

Ithaca.hideResearchPage = function() {
  const p = document.getElementById('research-page');
  if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) {
    document.getElementById('chat-container').classList.remove('hidden');
  } else {
    document.getElementById('empty-state').classList.remove('hidden');
  }
};

Ithaca.runResearch = async function() {
  const input = document.getElementById('research-input');
  const query = input.value.trim();
  if (!query) return;

  const progress = document.getElementById('research-progress');
  const report = document.getElementById('research-report');
  progress.innerHTML = '<div class="research-step">Starting research...</div>';
  report.classList.add('hidden');
  report.innerHTML = '';

  try {
    const resp = await fetch('/api/research', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query}),
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});
      const lines = buffer.split('\n');
      buffer = lines.pop();

      let currentEvent = '';
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7);
        } else if (line.startsWith('data: ') && currentEvent) {
          const data = JSON.parse(line.slice(6));
          Ithaca.handleResearchEvent(currentEvent, data);
          currentEvent = '';
        }
      }
    }
  } catch(e) {
    progress.innerHTML += `<div class="research-step error">Error: ${e.message}</div>`;
  }
};

Ithaca.handleResearchEvent = function(event, data) {
  const progress = document.getElementById('research-progress');
  const report = document.getElementById('research-report');

  switch(event) {
    case 'status':
      progress.innerHTML += `<div class="research-step">⏳ ${Ithaca.escHtml(data.message)}</div>`;
      break;
    case 'queries':
      progress.innerHTML += `<div class="research-step">🔍 Sub-queries: ${data.queries.map(q => `<em>${Ithaca.escHtml(q)}</em>`).join(', ')}</div>`;
      break;
    case 'sources':
      progress.innerHTML += `<div class="research-step">📚 Found ${data.count} sources</div>`;
      break;
    case 'report':
      report.classList.remove('hidden');
      report.innerHTML = Ithaca.renderMarkdown(data.content);
      progress.innerHTML += `<div class="research-step done">✅ Report complete (saved to Docs)</div>`;
      break;
    case 'done':
      break;
  }
  progress.scrollTop = progress.scrollHeight;
};
