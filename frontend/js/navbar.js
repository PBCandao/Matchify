document.addEventListener('DOMContentLoaded', () => {
  const navLogo = document.getElementById('nav-logo');
  const navAvatar = document.getElementById('nav-avatar');
  const navNotif = document.getElementById('nav-notif');
  const avatarDropdown = document.getElementById('avatar-dropdown');
  const avatarSidebar = document.getElementById('avatar-sidebar');
  const notifPanel = document.getElementById('notif-panel');
  const seeMoreBtn = document.getElementById('see-more');

  if (navLogo) {
    navLogo.addEventListener('click', () => {
      window.location = '/';
    });
  }

  if (navAvatar) {
    navAvatar.addEventListener('click', () => {
      if (avatarDropdown) avatarDropdown.classList.toggle('hidden');
      if (avatarSidebar) avatarSidebar.classList.toggle('hidden');
    });
  }

  if (navNotif && notifPanel) {
    navNotif.addEventListener('click', () => {
      notifPanel.classList.toggle('hidden');
    });
  }

  const handleAction = (action) => {
    switch (action) {
      case 'profile':
        window.location = 'profile.html?id=me';
        break;
      case 'settings':
        window.location = 'settings.html';
        break;
      case 'logout':
        window.location = '/logout';
        break;
      case 'contacts':
        window.location = 'contacts.html';
        break;
      case 'faq':
        window.location = 'faq.html';
        break;
      case 'tokens':
        window.location = '#';
        break;
      case 'preorder':
        window.location = 'https://www.matchify.app';
        break;
      case 'notifications':
        window.location = 'notifications.html';
        break;
      default:
        break;
    }
  };

  if (avatarDropdown) {
    avatarDropdown.querySelectorAll('li[data-action]').forEach(item => {
      item.addEventListener('click', () => {
        const action = item.getAttribute('data-action');
        handleAction(action);
        avatarDropdown.classList.add('hidden');
      });
    });
  }

  if (avatarSidebar) {
    avatarSidebar.querySelectorAll('li[data-action]').forEach(item => {
      item.addEventListener('click', () => {
        const action = item.getAttribute('data-action');
        handleAction(action);
      });
    });
  }

  if (seeMoreBtn) {
    seeMoreBtn.addEventListener('click', () => {
      window.location = 'notifications.html';
    });
  }
});