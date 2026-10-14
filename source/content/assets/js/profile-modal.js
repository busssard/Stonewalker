// Header "Edit Profile" modal.
// The form fragment (accounts/profile/change_profile_form.html) is inserted via
// innerHTML, where inline <script> tags never run, so all of its behaviour is
// bound here after each insertion. A successful save returns JSON and we
// reload the page so the flash messages and header picture update.
(function() {
  var MAX_FILE_SIZE = 5 * 1024 * 1024;

  function getBody() {
    return document.getElementById('profile-modal-body');
  }

  function closeProfileModal() {
    var overlay = document.getElementById('profile-modal-overlay');
    if (overlay) overlay.style.display = 'none';
  }

  function bindPictureControls(root) {
    var fileInput = root.querySelector('#id_profile_picture');
    var previewImg = root.querySelector('#profile-picture-preview');
    var cancelBtn = root.querySelector('#cancel-preview-btn');
    var clearBtn = root.querySelector('#clear-picture-btn');
    var clearInput = root.querySelector('#profile_picture_clear');
    var validationMsg = root.querySelector('#image-validation-msg');
    if (!fileInput || !previewImg) return;
    var originalSrc = previewImg.src;

    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        if (clearInput) clearInput.value = 'on';
        previewImg.src = previewImg.getAttribute('data-default-src') || originalSrc;
        fileInput.value = '';
        if (cancelBtn) cancelBtn.style.display = 'none';
        clearBtn.style.display = 'none';
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', function() {
        previewImg.src = originalSrc;
        previewImg.style.filter = 'contrast(1.08) brightness(1.04)';
        fileInput.value = '';
        cancelBtn.style.display = 'none';
        if (validationMsg) { validationMsg.textContent = ''; validationMsg.style.display = 'none'; }
      });
    }

    fileInput.addEventListener('change', function(e) {
      var file = e.target.files[0];
      if (!file) return;
      if (!file.type.startsWith('image/') || file.size > MAX_FILE_SIZE) { fileInput.value = ''; return; }
      var reader = new FileReader();
      reader.onload = function(ev) {
        previewImg.src = ev.target.result;
        previewImg.style.filter = 'contrast(1.08) brightness(1.04) drop-shadow(0 0 8px #4CAF50)';
        if (cancelBtn) cancelBtn.style.display = 'inline-flex';
      };
      reader.readAsDataURL(file);
    });
  }

  function bindUsernameCheck(root) {
    var usernameInput = root.querySelector('#id_username');
    var checkmark = root.querySelector('#username-checkmark');
    var checkResult = root.querySelector('#username-check-result');
    if (!usernameInput || !checkmark || !checkResult) return;
    var currentUsername = checkResult.getAttribute('data-current-username') || '';
    var timeout = null;

    function check() {
      var username = usernameInput.value.trim();
      if (!username || username === currentUsername) { checkmark.textContent = ''; checkResult.textContent = ''; return; }
      fetch('/accounts/api/check_username/?username=' + encodeURIComponent(username))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.taken) {
            checkmark.className = 'js-checkmark js-checkmark-invalid';
            checkResult.textContent = checkResult.getAttribute('data-taken-text');
            checkResult.className = 'js-result-text js-result-invalid';
          } else {
            checkmark.className = 'js-checkmark js-checkmark-valid';
            checkResult.textContent = checkResult.getAttribute('data-available-text');
            checkResult.className = 'js-result-text js-result-valid';
          }
        });
    }

    usernameInput.addEventListener('input', function() {
      usernameInput.value = usernameInput.value.toLowerCase();
      checkmark.textContent = ''; checkResult.textContent = '';
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(check, 350);
    });
  }

  function renderFragment(html) {
    var body = getBody();
    body.innerHTML = html;
    var cancel = body.querySelector('#profile-modal-cancel');
    if (cancel) cancel.addEventListener('click', closeProfileModal);
    bindPictureControls(body);
    bindUsernameCheck(body);
    var form = body.querySelector('#profile-form');
    if (form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          credentials: 'same-origin'
        }).then(function(r) {
          var type = r.headers.get('Content-Type') || '';
          if (type.indexOf('application/json') !== -1) {
            return r.json().then(function(data) {
              if (data.success) window.location.reload();
            });
          }
          return r.text().then(renderFragment);
        });
      });
    }
  }

  function openProfileModal() {
    var overlay = document.getElementById('profile-modal-overlay');
    var body = getBody();
    if (!overlay || !body) return;
    overlay.style.display = 'flex';
    body.innerHTML = '<div class="profile-modal-loading">Loading...</div>';
    // Language-prefixed URL rendered by page.html
    var url = overlay.getAttribute('data-url') || '/accounts/change/profile/?modal=1';
    fetch(url, {credentials: 'same-origin'})
      .then(function(r) { return r.text(); })
      .then(renderFragment);
  }

  document.addEventListener('DOMContentLoaded', function() {
    var closeBtn = document.getElementById('profile-modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeProfileModal);
    var overlay = document.getElementById('profile-modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', function(e) {
        if (e.target === overlay) closeProfileModal();
      });
    }
    var profileBtn = document.getElementById('profile-menu-btn');
    if (profileBtn) profileBtn.addEventListener('click', openProfileModal);
    // Any plain "Edit Profile" link opens the modal instead of navigating
    document.querySelectorAll('a[href$="/accounts/change/profile/"]').forEach(function(el) {
      el.addEventListener('click', function(e) {
        e.preventDefault();
        openProfileModal();
      });
    });
  });

  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Escape') return;
    var overlay = document.getElementById('profile-modal-overlay');
    if (overlay && overlay.style.display === 'flex') closeProfileModal();
  });

  window.openProfileModal = openProfileModal;
  window.closeProfileModal = closeProfileModal;
})();
