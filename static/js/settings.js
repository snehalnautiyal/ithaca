// Ithaca — settings modal
window.Ithaca = window.Ithaca || {};

Ithaca.openSettings = async function() {
  document.getElementById('settings-modal').classList.remove('hidden');
  const resp = await fetch('/api/models/settings');
  const settings = await resp.json();

  // Populate provider select
  const provSelect = document.getElementById('provider-select');
  provSelect.innerHTML = '';
  (settings.providers || []).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.name;
    opt.textContent = p.name;
    if (p.name === settings.active_provider) opt.selected = true;
    provSelect.appendChild(opt);
  });

  // Load models for active provider
  Ithaca.loadModels(settings.active_model);

  // Show provider list
  const list = document.getElementById('provider-list');
  list.innerHTML = '';
  (settings.providers || []).forEach(p => {
    const div = document.createElement('div');
    div.className = 'provider-item';
    div.textContent = `${p.name} — ${p.base_url}`;
    list.appendChild(div);
  });
};

Ithaca.loadModels = async function(activeModel) {
  const resp = await fetch('/api/models');
  const data = await resp.json();
  const modelSelect = document.getElementById('model-select');
  modelSelect.innerHTML = '';
  (data.models || []).forEach(m => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    if (m === (activeModel || data.active_model)) opt.selected = true;
    modelSelect.appendChild(opt);
  });
};

Ithaca.saveSettings = async function() {
  const provider = document.getElementById('provider-select').value;
  const model = document.getElementById('model-select').value;
  await fetch('/api/models/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ active_provider: provider, active_model: model }),
  });
};

Ithaca.addProvider = async function() {
  const name = document.getElementById('prov-name').value.trim();
  const url = document.getElementById('prov-url').value.trim();
  const key = document.getElementById('prov-key').value.trim() || null;
  if (!name || !url) return;

  const resp = await fetch('/api/models/settings');
  const settings = await resp.json();
  settings.providers.push({ name, base_url: url, api_key: key });
  await fetch('/api/models/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ providers: settings.providers }),
  });
  document.getElementById('prov-name').value = '';
  document.getElementById('prov-url').value = '';
  document.getElementById('prov-key').value = '';
  Ithaca.openSettings();
};
