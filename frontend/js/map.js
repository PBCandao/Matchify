// frontend/js/map.js
document.addEventListener('DOMContentLoaded', () => {
  // Initialize map with style toggle base layers
  const map = L.map('map');
  const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  });
  const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenTopoMap contributors'
  });
  let currentBase = streetLayer.addTo(map);
  // Marker cluster group
  const markers = L.markerClusterGroup();
  map.addLayer(markers);
  // Heatmap layer
  const heatmapCfg = {
    radius: 0.01,
    maxOpacity: 0.8,
    scaleRadius: true,
    useLocalExtrema: false,
    latField: 'lat',
    lngField: 'lng',
    valueField: 'count'
  };
  const heatmapLayer = new HeatmapOverlay(heatmapCfg);
  // Routing control placeholder
  let routeControl = null;
  // Filters state
  let filters = { roles: [], radius: 5, onlineOnly: false, invisible: false, searchTerm: '' };
  // Map search input filtering
  const mapSearch = document.getElementById('map-search');
  mapSearch.addEventListener('input', () => {
    filters.searchTerm = mapSearch.value.trim().toLowerCase();
    loadNodes();
  });
  let lastKnownLocation = null;
  // Listen for filter changes
  window.addEventListener('filtersChanged', e => {
    filters = e.detail;
    loadNodes();
  });
  // Real-time location updates
  const socket = io();
  socket.on('location_update', data => updateMarker(data));
  // Watch user geolocation
  if (navigator.geolocation) {
    navigator.geolocation.watchPosition(pos => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      lastKnownLocation = { lat, lng };
      window.lastKnownLocation = lastKnownLocation;
      // Update server
      fetch('/api/location', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ lat, lng })
      });
      // Update own marker
      updateMarker({ user_id: 'me', lat, lng });
      map.setView([lat, lng], 13);
      loadNodes();
    }, err => console.error('Geolocation error:', err), { enableHighAccuracy: true, maximumAge: 5000 });
  }
  // Header buttons
  document.getElementById('settings-btn').addEventListener('click', () => window.location = '/settings.html');
  // Filter drawer toggle
  const filterDrawer = document.getElementById('filter-drawer');
  document.getElementById('filter-toggle').addEventListener('click', () => filterDrawer.classList.toggle('open'));
  // Map style toggle
  document.getElementById('map-style-toggle').addEventListener('click', () => {
    map.removeLayer(currentBase);
    currentBase = (currentBase === streetLayer ? topoLayer : streetLayer);
    map.addLayer(currentBase);
  });
  // Load nodes from API
  function loadNodes() {
    if (!lastKnownLocation) return;
    const params = new URLSearchParams();
    params.set('radius', filters.radius);
    if (filters.roles.length) params.set('roles', filters.roles.join(','));
    if (filters.onlineOnly) params.set('onlineOnly', 'true');
    fetch('/api/map_nodes?' + params.toString())
      .then(r => r.json())
      .then(json => {
        markers.clearLayers();
        const heatData = [];
        (json.users || []).forEach(u => {
          // Client-side search filtering
          if (filters.searchTerm) {
            const matchName = u.name.toLowerCase().includes(filters.searchTerm);
            const matchRole = (u.roles || []).some(r => r.toLowerCase().includes(filters.searchTerm));
            if (!matchName && !matchRole) return;
          }
          const html = `<div class="map-avatar"><img src="${u.avatar_url}"/></div>`;
          const icon = L.divIcon({ html, className: '', iconSize: [48,48], iconAnchor: [24,24] });
          const m = L.marker([u.lat, u.lng], { icon });
          m.userData = u;
          m.on('click', () => window.dispatchEvent(new CustomEvent('showBottomSheet', { detail: u })));
          markers.addLayer(m);
          heatData.push({ lat: u.lat, lng: u.lng, count: 1 });
        });
        if (heatmapLayer._heatmap) {
          heatmapLayer.setData({ max: 1, data: heatData });
          if (!map.hasLayer(heatmapLayer)) map.addLayer(heatmapLayer);
        }
      });
  }
  // Update or add marker for a user
  function updateMarker(data) {
    markers.eachLayer(layer => {
      if (layer.userData && layer.userData.id === data.user_id) {
        layer.setLatLng([data.lat, data.lng]);
      }
    });
  }
  // Bridge to bottom sheet
  window.addEventListener('showBottomSheet', e => {
    window.dispatchEvent(new CustomEvent('openBottomSheet', { detail: e.detail }));
  });
  // Meetup FAB
  document.getElementById('fab-meetup').addEventListener('click', () => {
    window.dispatchEvent(new Event('openMeetupModal'));
  });
});