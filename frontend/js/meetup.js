// frontend/js/meetup.js
document.addEventListener('DOMContentLoaded', () => {
  let currentTarget = null;
  // Listen for FAB or bottom sheet triggers
  window.addEventListener('openMeetupModal', () => { currentTarget = null; showModal(); });
  window.addEventListener('initiateMeetupWith', e => { currentTarget = e.detail; showModal(); });

  function showModal() {
    let modal = document.getElementById('meetup-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'meetup-modal';
      modal.className = 'modal fade';
      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Create Meetup</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Title</label>
                <input id="meetup-title" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Time</label>
                <input id="meetup-time" type="datetime-local" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Invitee IDs (comma-separated)</label>
                <input id="meetup-invitees" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Message</label>
                <textarea id="meetup-message" class="form-control"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button id="meetup-cancel" type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button id="meetup-create" type="button" class="btn btn-primary">Create</button>
            </div>
          </div>
        </div>`;
      document.body.appendChild(modal);
      lucide.replace();
    }
    const bsModal = new bootstrap.Modal(modal);
    // Prefill invitee
    if (currentTarget) {
      document.getElementById('meetup-invitees').value = currentTarget.id;
    } else {
      document.getElementById('meetup-invitees').value = '';
    }
    bsModal.show();
    document.getElementById('meetup-create').addEventListener('click', async () => {
      const title = document.getElementById('meetup-title').value;
      const time = document.getElementById('meetup-time').value;
      const invitees = document.getElementById('meetup-invitees').value
        .split(',').map(s => s.trim()).filter(Boolean);
      const location = window.lastKnownLocation || {};
      const payload = { title, time, invitees, location };
      try {
        const res = await fetch('/api/meetups', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Create failed');
        alert('Meetup created and invites sent.');
      } catch (err) {
        console.error(err);
        alert('Error creating meetup.');
      }
      bsModal.hide();
    });
  }
});