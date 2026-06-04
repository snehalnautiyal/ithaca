// Ithaca — markdown rendering
window.Ithaca = window.Ithaca || {};

Ithaca.renderMarkdown = function(text) {
  marked.setOptions({
    highlight: function(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    },
    breaks: true,
  });
  let html = marked.parse(text);
  // Add copy buttons to code blocks
  html = html.replace(/<pre><code([^>]*)>/g, function(match, attrs) {
    return '<div class="code-block"><button class="copy-btn" onclick="Ithaca.copyCode(this)">Copy</button><pre><code' + attrs + '>';
  });
  html = html.replace(/<\/code><\/pre>/g, '</code></pre></div>');
  return html;
};

Ithaca.copyCode = function(btn) {
  const code = btn.parentElement.querySelector('code');
  navigator.clipboard.writeText(code.textContent).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 1500);
  });
};
