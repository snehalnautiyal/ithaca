// Ithaca — Compare (blind model A/B)
window.Ithaca = window.Ithaca || {};

Ithaca._compareReveal = null;
Ithaca._compareResponses = null;

Ithaca.showComparePage = function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  ['memory-page','docs-page','agent-page','research-page'].forEach(id => {
    const el = document.getElementById(id); if (el) el.classList.add('hidden');
  });

  let page = document.getElementById('compare-page');
  if (!page) {
    page = document.createElement('div');
    page.id = 'compare-page';
    page.innerHTML = `
      <div class="compare-header">
        <h2>⚖️ Compare Models</h2>
        <button class="btn-ghost" id="compare-back">← Back</button>
      </div>
      <div class="compare-input-area">
        <input id="compare-prompt" type="text" placeholder="Enter a prompt to compare across models...">
        <div class="compare-model-selects">
          <input id="cmp-m1" placeholder="Model 1 (e.g. llama3.2)" value="llama3.2">
          <input id="cmp-m2" placeholder="Model 2 (e.g. llama3.2)" value="llama3.2">
        </div>
        <button class="btn-ghost" id="compare-run">Compare</button>
      </div>
      <div id="compare-results" class="compare-results hidden"></div>
      <div id="compare-actions" class="compare-actions hidden">
        <button class="btn-ghost" id="compare-reveal">👁 Reveal Models</button>
        <button class="btn-ghost" id="compare-synth">✨ Synthesize</button>
      </div>
      <div id="compare-synthesis" class="compare-synthesis hidden"></div>
    `;
    document.getElementById('main').appendChild(page);
    document.getElementById('compare-back').addEventListener('click', Ithaca.hideComparePage);
    document.getElementById('compare-run').addEventListener('click', Ithaca.runCompare);
    document.getElementById('compare-reveal').addEventListener('click', Ithaca.revealModels);
    document.getElementById('compare-synth').addEventListener('click', Ithaca.synthesizeCompare);
  }
  page.classList.remove('hidden');
};

Ithaca.hideComparePage = function() {
  const p = document.getElementById('compare-page'); if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) document.getElementById('chat-container').classList.remove('hidden');
  else document.getElementById('empty-state').classList.remove('hidden');
};

Ithaca.runCompare = async function() {
  const prompt = document.getElementById('compare-prompt').value.trim();
  const m1 = document.getElementById('cmp-m1').value.trim();
  const m2 = document.getElementById('cmp-m2').value.trim();
  if (!prompt || !m1 || !m2) return;

  const settings = await (await fetch('/api/models/settings')).json();
  const provName = settings.active_provider;

  const models = [{provider: provName, model: m1}, {provider: provName, model: m2}];

  document.getElementById('compare-results').innerHTML = '<p class="muted">Running comparison...</p>';
  document.getElementById('compare-results').classList.remove('hidden');
  document.getElementById('compare-actions').classList.add('hidden');
  document.getElementById('compare-synthesis').classList.add('hidden');

  const resp = await fetch('/api/compare', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt, models}),
  });
  const data = await resp.json();

  if (data.error) { document.getElementById('compare-results').innerHTML = `<p class="error-msg">${data.error}</p>`; return; }

  Ithaca._compareReveal = data.reveal;
  Ithaca._compareResponses = data.responses;

  const resultsDiv = document.getElementById('compare-results');
  resultsDiv.innerHTML = data.responses.map(r => `
    <div class="compare-card">
      <div class="compare-card-header"><span class="blind-label">${r.label}</span><span class="real-label hidden"></span></div>
      <div class="compare-card-body">${Ithaca.renderMarkdown(r.content)}</div>
    </div>
  `).join('');
  document.getElementById('compare-actions').classList.remove('hidden');
};

Ithaca.revealModels = function() {
  if (!Ithaca._compareReveal) return;
  const cards = document.querySelectorAll('.compare-card-header');
  cards.forEach(card => {
    const blind = card.querySelector('.blind-label').textContent;
    const real = Ithaca._compareReveal[blind] || '?';
    card.querySelector('.real-label').textContent = ` → ${real}`;
    card.querySelector('.real-label').classList.remove('hidden');
  });
};

Ithaca.synthesizeCompare = async function() {
  if (!Ithaca._compareResponses) return;
  const prompt = document.getElementById('compare-prompt').value.trim();
  const responses = Ithaca._compareResponses.map(r => r.content);

  const synthDiv = document.getElementById('compare-synthesis');
  synthDiv.classList.remove('hidden');
  synthDiv.innerHTML = '<p class="muted">Synthesizing...</p>';

  const resp = await fetch('/api/compare/synthesize', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt, responses}),
  });
  const data = await resp.json();
  synthDiv.innerHTML = `<h3>✨ Synthesis</h3>${Ithaca.renderMarkdown(data.synthesis)}`;
};
