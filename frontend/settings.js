// frontend/settings.js
document.addEventListener('DOMContentLoaded', () => {
  const backBtn = document.getElementById('back-btn');
  const form = document.getElementById('settings-form');
  const saveBtn = document.getElementById('save-btn');
  const avatarInput = document.getElementById('avatar-input');
  const avatarPreview = document.getElementById('avatar-preview');
  const nameInput = document.getElementById('name-input');
  const bioInput = document.getElementById('bio-input');
  const telegramInput = document.getElementById('telegram-input');
  const rolesInput = document.getElementById('roles-input');
  const mainRoleSelect = document.getElementById('main-role-input');
  const contactSyncInput = document.getElementById('contact-sync-input');
  const locShareInput = document.getElementById('location-sharing-input');
  const notifMap = {
    'notify-contact-join-input': 'contact_join',
    'notify-introductions-input': 'introductions',
    'notify-new-connections-input': 'new_connections',
    'notify-role-discovery-input': 'role_discovery',
    'notify-area-unlock-input': 'area_unlock',
    'notify-system-alert-input': 'system',
  };
  const notifInputs = Object.keys(notifMap).map(id => document.getElementById(id));
  let original = {};
  // Navigate back
  backBtn.addEventListener('click', () => window.history.back());
  // Preview avatar
  avatarInput.addEventListener('change', () => {
    const file = avatarInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => { avatarPreview.src = reader.result; markDirty(); };
      reader.readAsDataURL(file);
    }
  });
  // Track dirty state
  const inputs = [nameInput, bioInput, telegramInput, rolesInput, mainRoleSelect, contactSyncInput, locShareInput, ...notifInputs];
  inputs.forEach(el => el.addEventListener('input', markDirty));
  function markDirty() { saveBtn.disabled = false; }
  // Populate form from API
  fetch('/api/settings')
    .then(r => r.json())
    .then(data => {
      const p = data.profile || {};
      const s = data.preferences || {};
      original = { profile: p, preferences: s };
      avatarPreview.src = p.avatar_url || '';
      nameInput.value = p.name || '';
      bioInput.value = p.bio_long || '';
      telegramInput.value = p.telegram || '';
      const roles = p.roles || [];
      rolesInput.value = roles.join(', ');
      // Populate main role options
      updateMainRoles(roles, p.main_role);
      contactSyncInput.checked = !!s.contact_sync;
      locShareInput.checked = !!s.location_sharing;
      notifInputs.forEach(inp => {
        const key = notifMap[inp.id];
        inp.checked = !!s[key];
      });
    })
    .catch(err => console.error('Error loading settings:', err));
  function updateMainRoles(roles, selected) {
    mainRoleSelect.innerHTML = '';
    roles.forEach(r => {
      const opt = document.createElement('option'); opt.value = r; opt.textContent = r;
      if (r === selected) opt.selected = true;
      mainRoleSelect.append(opt);
    });
  }
  // Keep main roles in sync
  rolesInput.addEventListener('input', () => {
    const list = rolesInput.value.split(',').map(s => s.trim()).filter(s => s);
    updateMainRoles(list, list[0] || '');
  });
  // Submit form
  form.addEventListener('submit', async e => {
    e.preventDefault(); saveBtn.disabled = true;
    let avatarUrl = original.profile.avatar_url;
    if (avatarInput.files[0]) {
      const formData = new FormData();
      formData.append('avatar', avatarInput.files[0]);
      try {
        const res = await fetch('/api/upload_avatar', { method: 'POST', body: formData });
        const json = await res.json(); avatarUrl = json.url;
      } catch (err) { console.error('Avatar upload failed', err); }
    }
    const rolesList = rolesInput.value.split(',').map(s => s.trim()).filter(s => s);
    const prefs = {
      contact_sync: contactSyncInput.checked,
      location_sharing: locShareInput.checked
    };
    notifInputs.forEach(inp => { prefs[notifMap[inp.id]] = inp.checked; });
    const payload = {
      avatar_url: avatarUrl,
      name: nameInput.value,
      bio_long: bioInput.value,
      telegram: telegramInput.value,
      roles: rolesList,
      main_role: mainRoleSelect.value,
      preferences: prefs
    };
    try {
      const res = await fetch('/api/settings', {
        method: 'PUT', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(res.statusText);
      // Show success toast
      alert('Your settings have been saved.');
    } catch (err) {
      console.error('Save failed', err);
      alert('Error saving settings');
    }
  });
  // Advanced Settings: preferences, export, delete
  // Utility: show toast messages
  function showToast(msg) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.innerText = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }
  // Initialize advanced preferences
  fetch('/api/preferences')
    .then(res => res.json())
    .then(prefs => {
      document.getElementById('theme-select').value = prefs.theme || 'system';
      document.getElementById('language-select').value = prefs.language || 'en';
      document.getElementById('twofa-toggle').checked = !!prefs.twofa;
    });
  // Save preference helper
  function savePref(key, value) {
    fetch('/api/preferences', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({[key]: value})
    }).then(() => showToast('Settings saved.'));
  }
  // Handlers for theme, language, 2FA toggles
  document.getElementById('theme-select')
    .addEventListener('change', e => savePref('theme', e.target.value));
  document.getElementById('language-select')
    .addEventListener('change', e => savePref('language', e.target.value));
  document.getElementById('twofa-toggle')
    .addEventListener('change', e => savePref('twofa', e.target.checked));
  // Export Data
  document.getElementById('export-data')
    .addEventListener('click', () => { window.location = '/api/export_data'; });
  // Delete Account
  document.getElementById('delete-account')
    .addEventListener('click', () => {
      const confirmCode = prompt('Type DELETE to confirm account deletion.');
      if (confirmCode === 'DELETE') {
        fetch('/api/delete_account', { method: 'POST' })
          .then(res => res.json())
          .then(() => {
            alert('Your account has been deleted.');
            window.location = '/goodbye.html';
          });
      }
    });
});