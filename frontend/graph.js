// Function to show profile popup or bottom sheet
function showProfile(d) {
  const popup = document.getElementById('profile-popup');
  if (!popup) return;
  // Fetch full profile data
  fetch(`/profile/${encodeURIComponent(d.id)}`)
    .then(res => res.json())
    .then(data => {
      // Populate popup fields
      document.getElementById('popup-avatar').src = data.avatarUrl;
      document.getElementById('popup-name').textContent = data.name;
      const rolesDiv = document.getElementById('popup-roles');
      rolesDiv.innerHTML = '';
      (data.roles || []).forEach((role, idx) => {
        const badge = document.createElement('span');
        badge.className = 'role-badge';
        badge.title = role;
        badge.style.background = d3.schemeCategory10[idx % 10];
        rolesDiv.appendChild(badge);
      });
      document.getElementById('popup-bio').textContent = data.bio;
      document.getElementById('popup-looking-text').textContent = data.lookingFor;
      document.getElementById('popup-offering-text').textContent = data.offering;
      const fullBtn = document.getElementById('popup-full-profile');
      fullBtn.href = `profile.html?user=${encodeURIComponent(d.id)}`;
    })
    .catch(err => console.error('Error loading profile:', err));
  // Show popup
  popup.classList.remove('hidden');
  if (window.innerWidth <= 768) popup.classList.add('show');
}

window.addEventListener('load', () => {
  // Close popup handler
  // Close popup functions
  function closePopup() {
    const popup = document.getElementById('profile-popup');
    if (!popup) return;
    popup.classList.add('hidden');
    popup.classList.remove('show');
  }
  const closeBtn = document.getElementById('close-popup');
  if (closeBtn) closeBtn.addEventListener('click', closePopup);
  // Close on outside click
  const popup = document.getElementById('profile-popup');
  if (popup) {
    popup.addEventListener('click', e => {
      if (e.target === popup) closePopup();
    });
    // Swipe down to close on mobile
    const content = popup.querySelector('.popup-content');
    let startY = 0;
    if (content) {
      content.addEventListener('touchstart', e => { startY = e.touches[0].clientY; });
      content.addEventListener('touchmove', e => {
        const deltaY = e.touches[0].clientY - startY;
        if (deltaY > 100) closePopup();
      });
    }
  }
  // Sidebar toggle for mobile
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (hamburger && sidebar && overlay) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.add('open');
      overlay.classList.remove('hidden');
    });
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.add('hidden');
    });
  }
  const params = new URLSearchParams(window.location.search);
  const user = params.get('user') || 'alice';
  const depth = params.get('depth') || '1';
  fetch(`/graph?user=${encodeURIComponent(user)}&depth=${encodeURIComponent(depth)}`)
    .then(res => {
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    })
    .then(data => {
      drawGraph(data.nodes, data.links);
    })
    .catch(err => console.error('Error loading graph data:', err));
});

function drawGraph(nodes, links) {
  let container = document.getElementById('graph-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'graph-container';
    document.body.appendChild(container);
  }
  container.innerHTML = '';
  // Show message if no connections
  if (!links || links.length === 0) {
    container.innerHTML = '<p class="no-connections">No connections yet.</p>';
    return;
  }
  const width = container.clientWidth || window.innerWidth;
  const height = container.clientHeight || window.innerHeight;
  if (typeof d3 !== 'undefined') {
    // Color scale based on user roles
    const rolesList = Array.from(new Set(nodes.flatMap(d => d.roles || [])));
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(rolesList);
    const svg = d3.select(container).append('svg')
      .attr('width', width)
      .attr('height', height);
    const link = svg.append('g').selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 1);
    const node = svg.append('g').selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', 10)
      .attr('fill', d => colorScale((d.roles && d.roles[0]) || d.id))
      .on('click', (event, d) => showProfile(d));
    const label = svg.append('g').selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.name || d.id)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4);
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
  } else {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    nodes.forEach(n => {
      n.x = Math.random() * width;
      n.y = Math.random() * height;
    });
    ctx.strokeStyle = '#999';
    links.forEach(l => {
      const s = nodes.find(n => n.id === l.source);
      const t = nodes.find(n => n.id === l.target);
      if (s && t) {
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.stroke();
      }
    });
    ctx.fillStyle = '#69b3a2';
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 10, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = '#000';
      ctx.fillText(n.id, n.x + 12, n.y + 4);
      ctx.fillStyle = '#69b3a2';
    });
  }
}
