// frontend/js/aiSearch.js
// Toggles AI pane and sends queries to the /api/ai_search endpoint
document.getElementById('ai-toggle').addEventListener('click', () => {
  const pane = document.getElementById('ai-feed');
  pane.style.display = pane.style.display === 'block' ? 'none' : 'block';
});
document.getElementById('ai-search').addEventListener('keydown', async (e) => {
  if (e.key !== 'Enter') return;
  const q = e.target.value.trim();
  if (!q) return;
  // Send query to AI endpoint
  const response = await fetch('/api/ai_search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: q })
  });
  const data = await response.json();
  // Render results
  const feed = document.getElementById('ai-feed');
  feed.innerHTML = '';
  (data.results || []).forEach(item => {
    const div = document.createElement('div');
    div.className = 'ai-result';
    div.textContent = JSON.stringify(item);
    feed.appendChild(div);
  });
});