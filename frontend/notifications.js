// frontend/notifications.js
document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('notif-list');
  const filters = document.querySelectorAll('.notif-filters button');
  let allNotifs = [];

  // Fetch notifications
  fetch('/api/notifications')
    .then(res => { if (!res.ok) throw new Error(res.statusText); return res.json(); })
    .then(data => {
      allNotifs = data.notifications || [];
      allNotifs.forEach(n => { n.read = !!n.read; });
      updateBadges();
      const activeFilter = document.querySelector('.notif-filters button.active').dataset.filter;
      renderList(activeFilter);
    })
    .catch(err => console.error('Error fetching notifications:', err));

  // Filter tab clicks
  filters.forEach(btn => {
    btn.addEventListener('click', () => {
      filters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderList(btn.dataset.filter);
    });
  });

  // Mark all read
  document.getElementById('mark-all-read').addEventListener('click', () => {
    allNotifs.forEach(n => n.read = true);
    updateBadges();
    const activeFilter = document.querySelector('.notif-filters button.active').dataset.filter;
    renderList(activeFilter);
    fetch('/api/notifications/mark_all_read', { method: 'POST' })
      .catch(err => console.error(err));
  });

  // Real-time updates via Socket.IO
  if (typeof io === 'function') {
    const socket = io();
    socket.on('notification', payload => {
      const event = payload.payload || payload;
      event.read = false;
      allNotifs.unshift(event);
      updateBadges();
      renderList('all');
    });
  }

  // Render notification list for given filter
  function renderList(filter) {
    listEl.innerHTML = '';
    allNotifs
      .filter(n => filter === 'all' || n.type === filter)
      .forEach(n => {
        const item = document.createElement('div');
        item.className = 'notif-item' + (n.read ? '' : ' unread');
        const icon = document.createElement('span');
        icon.className = 'icon';
        icon.textContent = iconFor(n.type);
        const content = document.createElement('span');
        content.className = 'content';
        content.textContent = n.details?.message || n.message || n.type;
        item.append(icon, content);
        if (n.type === 'intros') {
          const approve = document.createElement('button');
          approve.className = 'action';
          approve.textContent = 'Approve';
          approve.onclick = e => { e.stopPropagation(); respondIntro(n.event_id, true); };
          const decline = document.createElement('button');
          decline.className = 'action';
          decline.textContent = 'Decline';
          decline.onclick = e => { e.stopPropagation(); respondIntro(n.event_id, false); };
          item.append(approve, decline);
        }
        item.onclick = () => {
          if (!n.read) markRead(n.event_id);
          const link = n.details?.link || n.link;
          if (link) window.location = link;
        };
        listEl.append(item);
      });
  }

  // Update unread badges on tabs
  function updateBadges() {
    const counts = { all: 0, connections: 0, intros: 0, roles: 0, system: 0 };
    allNotifs.forEach(n => { if (!n.read) {
      counts.all++;
      if (counts[n.type] !== undefined) counts[n.type]++;
    }});
    Object.keys(counts).forEach(type => {
      const badge = document.getElementById(`badge-${type}`);
      if (badge) badge.textContent = counts[type] > 0 ? counts[type] : '';
    });
  }

  function iconFor(type) {
    return { joined:'👤➕', connection:'🔗', intros:'📩', roles:'🏷️', area:'🌐', system:'⚙️' }[type] || '🔔';
  }

  function markRead(id) {
    const n = allNotifs.find(x => x.event_id === id);
    if (n) n.read = true;
    updateBadges();
    const activeFilter = document.querySelector('.notif-filters button.active').dataset.filter;
    renderList(activeFilter);
    fetch(`/api/notifications/${id}/read`, { method: 'POST' })
      .catch(err => console.error(err));
  }

  function respondIntro(id, approve) {
    fetch(`/api/notifications/${id}/${approve?'approve':'decline'}`, { method: 'POST' })
      .then(() => markRead(id))
      .catch(err => console.error(err));
  }
});