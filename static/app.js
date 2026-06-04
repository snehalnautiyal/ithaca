// Ithaca — main wiring
document.addEventListener('DOMContentLoaded', () => {
  Ithaca.loadSessions();

  document.getElementById('new-chat').addEventListener('click', Ithaca.createSession);

  document.getElementById('send-btn').addEventListener('click', Ithaca.sendMessage);

  const input = document.getElementById('chat-input');
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      Ithaca.sendMessage();
    }
  });
  // Auto-resize textarea
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 200) + 'px';
  });

  // Settings modal
  document.getElementById('settings-btn').addEventListener('click', Ithaca.openSettings);
  // Memory page
  document.getElementById('memory-btn').addEventListener('click', Ithaca.showMemoryPage);
  // Documents page
  document.getElementById('docs-btn').addEventListener('click', Ithaca.showDocsPage);
  // Agent page
  document.getElementById('agent-btn').addEventListener('click', Ithaca.showAgentPage);
  document.getElementById('close-settings').addEventListener('click', () => {
    Ithaca.saveSettings();
    document.getElementById('settings-modal').classList.add('hidden');
  });
  document.getElementById('add-provider-btn').addEventListener('click', Ithaca.addProvider);
  document.getElementById('provider-select').addEventListener('change', () => {
    Ithaca.saveSettings().then(() => Ithaca.loadModels());
  });
});
