// frontend/js/bottomSheet.js
document.addEventListener('DOMContentLoaded', () => {
  const sheet = document.getElementById('bottom-sheet');
  if (!sheet) return;
  window.addEventListener('openBottomSheet', e => {
    const u = e.detail;
    const distance = u.lat && u.lng && window.lastKnownLocation
      ? `${Math.round(mapDistance(window.lastKnownLocation.lat, window.lastKnownLocation.lng, u.lat, u.lng) * 1000)} m away`
      : '';
    sheet.innerHTML = `
      <div class="d-flex justify-content-between align-items-center p-2 border-bottom">
        <h5 class="mb-0">${u.name}</h5>
        <button id="close-bottom" class="btn btn-link p-0">&times;</button>
      </div>
      <div class="p-3">
        <img src="${u.avatar_url}" alt="${u.name}" class="map-avatar mb-2" />
        <p><strong>${u.main_role || (u.roles && u.roles[0] || '')}</strong></p>
        <p><small>${u.status === 'online' ? '🟢 Online' : '🔴 Offline'} ${distance}</small></p>
        <button id="bs-request" class="btn btn-primary w-100 mb-2">Request Meetup</button>
        <button id="bs-profile" class="btn btn-outline-secondary w-100">View Profile</button>
      </div>
    `;
    sheet.classList.add('open');
    lucide.replace();
    document.getElementById('close-bottom').addEventListener('click', () => sheet.classList.remove('open'));
    document.getElementById('bs-profile').addEventListener('click', () => {
      window.location = `/profile.html?id=${encodeURIComponent(u.id)}`;
    });
    document.getElementById('bs-request').addEventListener('click', () => {
      window.dispatchEvent(new CustomEvent('initiateMeetupWith', { detail: u }));
    });
  });
  // Utility to compute distance (Haversine)
  function mapDistance(lat1, lon1, lat2, lon2) {
    const toRad = d => d * Math.PI / 180;
    const R = 6371; // km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
});