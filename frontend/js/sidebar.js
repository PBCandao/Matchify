// frontend/js/sidebar.js
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('filter-toggle');
  const drawer = document.getElementById('filter-drawer');
  if (!toggleBtn || !drawer) return;
  toggleBtn.addEventListener('click', () => drawer.classList.toggle('open'));

  // Build filter controls
  fetch('/api/roles')
    .then(r => r.json())
    .then(json => {
      const roles = json.roles || [];
      const roleSection = document.createElement('div');
      roleSection.className = 'mb-3';
      roleSection.innerHTML = '<strong>Roles</strong>';
      roles.forEach(role => {
        const id = `filter-role-${role}`;
        const label = document.createElement('label');
        label.className = 'd-block';
        label.innerHTML = `<input type="checkbox" id="${id}" data-role="${role}"> ${role}`;
        roleSection.appendChild(label);
      });
      drawer.appendChild(roleSection);

      // Distance slider
      const distSection = document.createElement('div');
      distSection.className = 'mb-3';
      distSection.innerHTML = '<strong>Radius (km)</strong> <span id="distance-value">5</span> km';
      const distInput = document.createElement('input');
      distInput.type = 'range'; distInput.id = 'distance-slider';
      distInput.min = 1; distInput.max = 20; distInput.value = 5;
      distSection.appendChild(distInput);
      drawer.appendChild(distSection);

      // Online only toggle
      const onlineLabel = document.createElement('label');
      onlineLabel.className = 'form-check';
      onlineLabel.innerHTML = '<input class="form-check-input" type="checkbox" id="online-only-toggle"> Online only';
      drawer.appendChild(onlineLabel);

      // Visible to specific roles toggle
      const visibleLabel = document.createElement('label');
      visibleLabel.className = 'form-check mt-2';
      visibleLabel.innerHTML = '<input class="form-check-input" type="checkbox" id="visible-to-toggle"> Visible only to selected roles';
      drawer.appendChild(visibleLabel);

      // Attach change listeners
      drawer.querySelectorAll('input').forEach(el => el.addEventListener('change', publishFilters));
      distInput.addEventListener('input', () => {
        document.getElementById('distance-value').textContent = distInput.value;
        publishFilters();
      });
      // Initial publish
      publishFilters();
    });

  function publishFilters() {
    const roles = Array.from(drawer.querySelectorAll('input[data-role]:checked')).map(i => i.dataset.role);
    const radius = parseFloat(document.getElementById('distance-slider').value);
    const onlineOnly = document.getElementById('online-only-toggle').checked;
    const invisible = document.getElementById('visible-to-toggle').checked;
    window.dispatchEvent(new CustomEvent('filtersChanged', { detail: { roles, radius, onlineOnly, invisible } }));
  }
});