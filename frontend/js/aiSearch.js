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
  const candidates = await fetch('/api/map_nodes?radius=100')
    .then(r => r.json()).then(r => r.users);
  const res = await fetch('/api/ai_search', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ query: q, candidates })
  }).then(r => r.json());
  document.getElementById('ai-feed').innerHTML =
    res.matches.map(m => 
      `<div class="ai-match">
         <img src="${m.avatar_url}" class="${m.locked ? 'blurred' : ''}" />
         <strong>${m.name}</strong><br/>
         <em>${m.roles.join(', ')}</em><br/>
         Handshakes: ${m.handshake_count}<br/>
         <p>${m.reason}</p>
         <button onclick="focusMap('${m.id}');focusGraph('${m.id}')">View</button>
         <button onclick="requestIntro('${m.id}')">Request Intro</button>
       </div>`).join('');
});