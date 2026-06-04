// Ithaca — chat logic
window.Ithaca = window.Ithaca || {};

Ithaca.renderMessages = function(msgs) {
  const container = document.getElementById('messages');
  container.innerHTML = '';
  msgs.forEach(m => Ithaca.appendMessage(m.role, m.content));
  container.scrollTop = container.scrollHeight;
};

Ithaca.appendMessage = function(role, content) {
  const container = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  if (role === 'assistant') {
    div.innerHTML = Ithaca.renderMarkdown(content);
  } else {
    div.textContent = content;
  }
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
};

Ithaca.sendMessage = async function() {
  const input = document.getElementById('chat-input');
  const content = input.value.trim();
  if (!content || !Ithaca.currentSession) return;

  input.value = '';
  Ithaca.appendMessage('user', content);

  // Create assistant bubble to stream into
  const assistantDiv = Ithaca.appendMessage('assistant', '');
  let fullText = '';

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: Ithaca.currentSession, content }),
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line

      for (const line of lines) {
        if (line.startsWith('event: error')) {
          const dataLine = lines[lines.indexOf(line) + 1];
          if (dataLine && dataLine.startsWith('data: ')) {
            const err = JSON.parse(dataLine.slice(6));
            assistantDiv.innerHTML = `<span class="error-msg">Error: ${Ithaca.escHtml(err.detail)}</span>`;
          }
          return;
        }
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '{}') continue; // done event
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              fullText += parsed.content;
              assistantDiv.innerHTML = Ithaca.renderMarkdown(fullText);
              document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
            }
          } catch(e) {}
        }
      }
    }
  } catch(e) {
    assistantDiv.innerHTML = `<span class="error-msg">Error: ${Ithaca.escHtml(e.message)}</span>`;
  }

  Ithaca.loadSessions(); // refresh title if changed
};
