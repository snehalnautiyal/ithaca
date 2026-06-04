// Ithaca — Agent UI
window.Ithaca = window.Ithaca || {};

Ithaca.showAgentPage = function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  const memPage = document.getElementById('memory-page');
  if (memPage) memPage.classList.add('hidden');
  const docsPage = document.getElementById('docs-page');
  if (docsPage) docsPage.classList.add('hidden');

  let agentPage = document.getElementById('agent-page');
  if (!agentPage) {
    agentPage = document.createElement('div');
    agentPage.id = 'agent-page';
    agentPage.innerHTML = `
      <div class="agent-header">
        <h2>🤖 Agent</h2>
        <button class="btn-ghost" id="agent-back">← Back</button>
      </div>
      <div id="agent-trace" class="agent-trace"></div>
      <div class="agent-input-area">
        <textarea id="agent-input" placeholder="Describe a task for the agent..." rows="2"></textarea>
        <div class="agent-confirm-opts">
          <label><input type="checkbox" id="confirm-shell" checked> Allow shell</label>
          <label><input type="checkbox" id="confirm-file" checked> Allow file write</label>
        </div>
        <button class="btn-ghost" id="agent-run">Run Agent</button>
      </div>
    `;
    document.getElementById('main').appendChild(agentPage);
    document.getElementById('agent-back').addEventListener('click', Ithaca.hideAgentPage);
    document.getElementById('agent-run').addEventListener('click', Ithaca.runAgent);
    document.getElementById('agent-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); Ithaca.runAgent(); }
    });
  }
  agentPage.classList.remove('hidden');
};

Ithaca.hideAgentPage = function() {
  const p = document.getElementById('agent-page');
  if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) {
    document.getElementById('chat-container').classList.remove('hidden');
  } else {
    document.getElementById('empty-state').classList.remove('hidden');
  }
};

Ithaca.runAgent = async function() {
  const input = document.getElementById('agent-input');
  const task = input.value.trim();
  if (!task) return;

  const confirmed = [];
  if (document.getElementById('confirm-shell').checked) confirmed.push('shell_exec');
  if (document.getElementById('confirm-file').checked) confirmed.push('file_write');

  const trace = document.getElementById('agent-trace');
  trace.innerHTML = '<div class="trace-step muted">Starting agent...</div>';
  input.value = '';

  try {
    const resp = await fetch('/api/agent', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({task, confirmed_tools: confirmed}),
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
          Ithaca.addTraceStep(currentEvent, data);
          currentEvent = '';
        }
      }
    }
  } catch(e) {
    trace.innerHTML += `<div class="trace-step trace-error">Error: ${Ithaca.escHtml(e.message)}</div>`;
  }
};

Ithaca.addTraceStep = function(event, data) {
  const trace = document.getElementById('agent-trace');
  let html = '';

  switch(event) {
    case 'thinking':
      html = `<div class="trace-step trace-thinking">🧠 Step ${data.step}: Thinking...</div>`;
      break;
    case 'tool_call':
      html = `<details class="trace-step trace-tool"><summary>🔧 Tool: ${Ithaca.escHtml(data.tool)} (step ${data.step})</summary><pre>${Ithaca.escHtml(JSON.stringify(data.args, null, 2))}</pre></details>`;
      break;
    case 'tool_result':
      html = `<details class="trace-step trace-result"><summary>📋 Result: ${Ithaca.escHtml(data.tool)} (step ${data.step})</summary><pre>${Ithaca.escHtml(data.result)}</pre></details>`;
      break;
    case 'confirm_required':
      html = `<div class="trace-step trace-warn">⚠️ ${data.tool} requires confirmation (denied in this run)</div>`;
      break;
    case 'answer':
      html = `<div class="trace-step trace-answer">${Ithaca.renderMarkdown(data.content)}</div>`;
      break;
    case 'error':
      html = `<div class="trace-step trace-error">❌ ${Ithaca.escHtml(data.detail)}</div>`;
      break;
  }
  trace.innerHTML += html;
  trace.scrollTop = trace.scrollHeight;
};
