// Ithaca — Cookbook (Model Manager)
window.Ithaca = window.Ithaca || {};

Ithaca.showCookbookPage = function() {
  document.getElementById('chat-container').classList.add('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  ['memory-page','docs-page','agent-page','research-page','compare-page'].forEach(id => {
    const el = document.getElementById(id); if (el) el.classList.add('hidden');
  });

  let page = document.getElementById('cookbook-page');
  if (!page) {
    page = document.createElement('div');
    page.id = 'cookbook-page';
    page.innerHTML = `
      <div class="cookbook-header"><h2>📦 Cookbook</h2><button class="btn-ghost" id="cookbook-back">← Back</button></div>
      <div id="hw-info" class="hw-info"></div>
      <h3>Installed Models</h3>
      <div id="installed-models"></div>
      <h3>Model Catalog</h3>
      <div id="model-catalog"></div>
    `;
    document.getElementById('main').appendChild(page);
    document.getElementById('cookbook-back').addEventListener('click', Ithaca.hideCookbookPage);
  }
  page.classList.remove('hidden');
  Ithaca.loadCookbook();
};

Ithaca.hideCookbookPage = function() {
  const p = document.getElementById('cookbook-page'); if (p) p.classList.add('hidden');
  if (Ithaca.currentSession) document.getElementById('chat-container').classList.remove('hidden');
  else document.getElementById('empty-state').classList.remove('hidden');
};

Ithaca.loadCookbook = async function() {
  const [hwResp, catResp, instResp] = await Promise.all([
    fetch('/api/cookbook/hardware'), fetch('/api/cookbook/catalog'), fetch('/api/cookbook/installed')
  ]);
  const hw = await hwResp.json();
  const catalog = await catResp.json();
  const installed = await instResp.json();

  document.getElementById('hw-info').innerHTML = `
    <span>💻 ${hw.cpu}</span> <span>🧠 ${hw.ram_gb} GB ${hw.unified_memory ? '(unified)' : ''}</span>
    <span>🎮 ${hw.gpu}</span> <span>${hw.metal ? '✅ Metal' : ''}</span>
  `;

  const instIds = installed.map(m => m.id);
  document.getElementById('installed-models').innerHTML = installed.length
    ? installed.map(m => `<div class="model-card installed"><span>${m.id}</span><span class="model-size">${m.size}</span>
        <button class="btn-ghost btn-sm" onclick="Ithaca.deleteModel('${m.id}')">Remove</button></div>`).join('')
    : '<p class="muted">No models installed yet.</p>';

  document.getElementById('model-catalog').innerHTML = catalog.map(m => {
    const isInstalled = instIds.some(id => id.startsWith(m.id));
    return `<div class="model-card score-${m.score}">
      <div><strong>${m.name}</strong> <span class="model-meta">${m.params} · ${m.ram_needed_gb}GB RAM</span></div>
      <div class="model-card-actions">
        <span class="fit-badge ${m.score}">${m.score}</span>
        ${isInstalled ? '<span class="muted">installed</span>' : m.can_run ? `<button class="btn-ghost btn-sm" onclick="Ithaca.pullModel('${m.id}')">Pull</button>` : '<span class="muted">too large</span>'}
      </div>
    </div>`;
  }).join('');
};

Ithaca.pullModel = async function(id) {
  await fetch(`/api/cookbook/pull/${encodeURIComponent(id)}`, {method:'POST'});
  alert(`Pulling ${id}... This runs in the background. Refresh in a minute.`);
};

Ithaca.deleteModel = async function(id) {
  await fetch(`/api/cookbook/models/${encodeURIComponent(id)}`, {method:'DELETE'});
  Ithaca.loadCookbook();
};
