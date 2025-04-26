// Function to show profile popup or bottom sheet
// Global state for graph navigation
let currentDepth = 1;
// Fetch and draw graph for given user and depth
function fetchAndDraw(u, d) {
  currentDepth = d;
  fetch(`/graph?user=${encodeURIComponent(u)}&depth=${encodeURIComponent(d)}`)
    .then(res => {
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    })
    .then(data => {
      console.log('Graph data:', data);
      drawGraph(data.nodes, data.links);
    })
    .catch(err => console.error('Error loading graph data:', err));
}
// Global socket for real-time notifications
const socket = io();
socket.on('notification', n => {
  // Update badge count and ensure badge is visible
  const countSpan = document.getElementById('notif-badge') || document.getElementById('notif-count');
  let cnt = parseInt(countSpan.textContent, 10) || 0;
  countSpan.textContent = ++cnt;
  countSpan.style.display = 'inline-block';
  // Prepend notification to list
  const list = document.getElementById('notif-list');
  const li = document.createElement('li');
  li.textContent = n.message || n.type;
  li.dataset.payload = JSON.stringify(n);
  li.addEventListener('click', () => handleNotificationClick(n));
  list.prepend(li);
});
function handleNotificationClick(n) {
  // TODO: implement approve/decline logic
  console.log('Notification clicked:', n);
}
// Function to show locked-node introduction preview
function showLockedPreview(d) {
  // Fetch shortest path to determine intermediary
  fetch(`/path?from=me&to=${encodeURIComponent(d.id)}`)
    .then(res => res.json())
    .then(data => {
      const path = data.path || [];
      const viaId = path[1];
      // Fetch via user profile to get name
      fetch(`/profile/${encodeURIComponent(viaId)}`)
        .then(r => r.json())
        .then(viaProfile => {
          const lp = document.getElementById('locked-preview');
          if (!lp) return;
          // Populate preview avatar and friend-of label
          lp.querySelector('.preview-avatar').src = d.avatar_url || d.avatarUrl;
          lp.querySelector('.preview-name').textContent = `Friend of ${viaProfile.name}`;
          // Show all roles as badges
          const rolesContainer = lp.querySelector('.preview-roles');
          rolesContainer.innerHTML = '';
          (d.roles || []).forEach((role, idx) => {
            const badge = document.createElement('span');
            badge.className = 'role-badge';
            badge.title = role;
            rolesContainer.appendChild(badge);
          });
          // Short bio, looking for, and offering
          lp.querySelector('.preview-short-bio').textContent = d.bio_long || '';
          lp.querySelector('.preview-looking').textContent = `Looking for: ${d.looking_for || ''}`;
          lp.querySelector('.preview-offering').textContent = `Offering: ${d.offering || ''}`;
          // Attach request connection handler
          const reqBtn = lp.querySelector('#request-connection');
          reqBtn.onclick = () => {
            fetch('/request_connection', {
              method: 'POST', headers: {'Content-Type':'application/json'},
              body: JSON.stringify({from:'me', to:d.id, via:viaId})
            }).then(r=>r.json()).then(_=>{
              alert('Connection request sent');
              lp.classList.remove('show');
              lp.classList.add('hidden');
            });
          };
          // Attach show path handler
          const spBtn = lp.querySelector('#show-path');
          spBtn.onclick = () => {
            // Animate path highlight
            animatePath(path);
            // Show intermediary avatars as clickable links
            const container = lp.querySelector('#path-avatars');
            container.innerHTML = '';
            const allNodes = (window._graphData && window._graphData.nodes) || [];
            path.slice(1, -1).forEach(uid => {
              const nodeInfo = allNodes.find(n => n.id === uid) || {};
              const img = document.createElement('img');
              img.src = nodeInfo.avatar_url || nodeInfo.avatarUrl || '';
              img.width = 40; img.height = 40;
              img.classList.add('rounded-circle');
              img.style.cursor = 'pointer';
              // On click, focus this intermediary in the graph
              img.addEventListener('click', () => {
                // Close preview
                lp.classList.remove('show');
                lp.classList.add('hidden');
                // Center graph on this user with full depth
                fetchAndDraw(uid, 6);
              });
              container.appendChild(img);
            });
            const label = lp.querySelector('#path-label');
            label.textContent = `${path.length - 1}-handshake`;
          };
          // Show the locked preview bottom sheet
          lp.classList.remove('hidden');
          lp.classList.add('show');
        });
    });
}
// Animate a glowing highlight along a path of node IDs
function animatePath(path) {
  // Highlight links in sequence
  const svg = d3.select('#graph-container svg');
  path.reduce((promise, curr, idx) => {
    return promise.then(() => new Promise(res => {
      if (idx < path.length-1) {
        const s = path[idx], t = path[idx+1];
        svg.selectAll('line')
          .filter(d => (d.source.id||d.source)===s && (d.target.id||d.target)===t)
          .transition().duration(300)
          .attr('stroke', 'gold').attr('stroke-width', 4)
          .transition().duration(300)
          .attr('stroke', '#999').attr('stroke-width', 1)
          .on('end', res);
      } else res();
    }));
  }, Promise.resolve());
}
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
      document.getElementById('popup-bio').textContent = data.bio_short;
      document.getElementById('popup-looking-text').textContent = data.looking_for;
      document.getElementById('popup-offering-text').textContent = data.offering;
      const telLink = document.getElementById('popup-telegram');
      telLink.href = `https://t.me/${data.telegram}`;
      telLink.textContent = data.telegram;
      const fullBtn = document.getElementById('popup-full-profile');
      fullBtn.href = `profile.html?user=${encodeURIComponent(d.id)}`;
    })
    .catch(err => console.error('Error loading profile:', err));
  // Show popup
  popup.classList.remove('hidden');
  if (window.innerWidth <= 768) popup.classList.add('show');
}

window.addEventListener('load', () => {
  // Hide notification badge if count is zero
  // Hide notification badge if count is zero
  const badgeInit = document.getElementById('notif-badge') || document.getElementById('notif-count');
  if (badgeInit && parseInt(badgeInit.textContent, 10) === 0) {
    badgeInit.style.display = 'none';
  }
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
  // Graph search filter
  const searchInput = document.getElementById('graph-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => filterGraph(searchInput.value));
  }
  // Zoom controls
  const zoomIn = document.getElementById('zoom-in');
  const zoomOut = document.getElementById('zoom-out');
  if (zoomIn) zoomIn.addEventListener('click', () => adjustZoom(1.2));
  if (zoomOut) zoomOut.addEventListener('click', () => adjustZoom(0.8));
  // Notification dropdown toggle with fetch on open
  const notifBtn = document.getElementById('notif-btn');
  const notifList = document.getElementById('notif-list');
  if (notifBtn && notifList) {
    // Rename any existing count badge id to badge
    const oldCount = document.getElementById('notif-count');
    if (oldCount) oldCount.id = 'notif-badge';
    // Remove any static view-all entries
    Array.from(notifList.querySelectorAll('li')).forEach(li => {
      if (li.textContent.includes('View All Notifications')) li.remove();
    });
    notifBtn.addEventListener('click', async () => {
      const isHidden = notifList.classList.toggle('hidden');
      if (!isHidden) {
        try {
          const res = await fetch('/notifications');
          if (!res.ok) throw new Error(res.statusText);
          const json = await res.json();
          console.log('Fetched notifications:', json);
          notifList.innerHTML = '';
          (json.notifications || []).forEach(n => {
            const li = document.createElement('li');
            li.textContent = n.details?.message || n.type || '';
            notifList.appendChild(li);
          });
          // Append 'View All' link
          const seeAllLi = document.createElement('li');
          const a = document.createElement('a');
          a.href = '/notifications';
          a.textContent = 'View All Notifications';
          seeAllLi.appendChild(a);
          notifList.appendChild(seeAllLi);
        } catch (err) {
          console.error('Error fetching notifications:', err);
        }
      }
    });
  }
  // Locked-preview close button
  const closeLockedBtn = document.querySelector('#locked-preview .close-locked');
  if (closeLockedBtn) {
    closeLockedBtn.addEventListener('click', () => {
      const lp = document.getElementById('locked-preview');
      lp.classList.remove('show');
      lp.classList.add('hidden');
    });
  }
  // Initialize with URL params or defaults, then fetch graph
  const params = new URLSearchParams(window.location.search);
  const user = params.get('user') || 'me';
  // Default to 6-degree separation on homepage
  const depth = parseInt(params.get('depth'), 10) || 6;
  fetchAndDraw(user, depth);
});

function drawGraph(nodes, links) {
  // Expose graph data globally for path preview
  window._graphData = { nodes, links };
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
    // Create SVG with zoomable g
    const svg = d3.select(container).append('svg')
      .attr('width', width)
      .attr('height', height);
    const gMain = svg.append('g');
    // Define avatar patterns
    const defs = svg.append('defs');
    nodes.forEach(d => {
      defs.append('pattern')
        .attr('id', `avatar-${d.id}`)
        .attr('patternUnits', 'objectBoundingBox')
        .attr('width', 1)
        .attr('height', 1)
        .append('image')
          .attr('xlink:href', d.avatar_url || d.avatarUrl)
          .attr('preserveAspectRatio', 'xMidYMid slice')
          .attr('width', 40)
          .attr('height', 40);
    });
    // Draw links
    const link = gMain.append('g').selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 1);
    // Draw nodes (avatar circles)
    const nodeGroup = gMain.append('g').selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', d => d.depth > 1 ? 'locked' : '');
    // Click handler: locked vs unlocked
    nodeGroup.on('click', (event, d) => {
      if (d.depth > 1) showLockedPreview(d);
      else showProfile(d);
    });
    nodeGroup.append('circle')
      .attr('r', 20)
      .attr('fill', d => `url(#avatar-${d.id})`)
      .on('dblclick', (event, d) => fetchAndDraw(d.id, currentDepth));
    // Name and role labels (contacts only)
    nodeGroup.append('text')
      .attr('class', 'name-label')
      .text(d => d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', 30)
      .attr('fill', '#000')
      .attr('font-size', '12px');
    nodeGroup.append('text')
      .attr('class', 'role-label')
      .text(d => (d.roles && d.roles[0]) || '')
      .attr('text-anchor', 'middle')
      .attr('dy', 45)
      .attr('fill', '#666')
      .attr('font-size', '10px');
    // Apply zoom and pan
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        gMain.attr('transform', event.transform);
      });
    svg.call(zoomBehavior);
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));
    simulation.on('tick', () => {
      // Update link positions
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      // Update node group positions
      nodeGroup
        .attr('transform', d => `translate(${d.x},${d.y})`);
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
