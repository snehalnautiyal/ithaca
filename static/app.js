// Ithaca — main wiring (Shoelace)
document.addEventListener('DOMContentLoaded', () => {
  Ithaca.loadSessions();

  document.getElementById('new-chat').addEventListener('click', Ithaca.createSession);
  document.getElementById('send-btn').addEventListener('click', Ithaca.sendMessage);

  const input = document.getElementById('chat-input');
  // sl-textarea uses 'sl-input' event and .value property
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      Ithaca.sendMessage();
    }
  });

  // Settings
  document.getElementById('settings-btn').addEventListener('click', Ithaca.openSettings);
  document.getElementById('close-settings').addEventListener('click', () => {
    Ithaca.saveSettings();
    document.getElementById('settings-modal').hide();
  });
  document.getElementById('add-provider-btn').addEventListener('click', Ithaca.addProvider);
  document.getElementById('provider-select').addEventListener('sl-change', () => {
    Ithaca.saveSettings().then(() => Ithaca.loadModels());
  });

  // Pages
  document.getElementById('memory-btn').addEventListener('click', Ithaca.showMemoryPage);
  document.getElementById('docs-btn').addEventListener('click', Ithaca.showDocsPage);
  document.getElementById('agent-btn').addEventListener('click', Ithaca.showAgentPage);
  document.getElementById('research-btn').addEventListener('click', Ithaca.showResearchPage);
  document.getElementById('compare-btn').addEventListener('click', Ithaca.showComparePage);
  document.getElementById('cookbook-btn').addEventListener('click', Ithaca.showCookbookPage);
  document.getElementById('productivity-btn').addEventListener('click', Ithaca.showProductivityPage);
});
