/*
  BREAKPOINTS are the source of truth for all responsive breakpoints in this project.
  To keep styles.css in sync, run the provided sync script:

    node source/content/assets/js/sync-breakpoints.js

  This will update all hardcoded px values in styles.css media queries to match the BREAKPOINTS below.
  (You can also run this script after changing any breakpoint value here.)
*/
// Responsive breakpoints (source of truth, keep in sync with styles.css media queries!)
const BREAKPOINTS = {
  desktop: 1450,
  tablet: 800,
  mobileLg: 768,
  mobileMd: 600,
  mobile: 480,
  mobileXs: 360
};
// Expose globally for debug widget in page.html
window.BREAKPOINTS = BREAKPOINTS;
// Set as CSS custom properties for reference/debugging
Object.entries(BREAKPOINTS).forEach(([key, value]) => {
  document.documentElement.style.setProperty(`--breakpoint-${key.toLowerCase()}`, value + 'px');
});

function isMobile() {
  return window.innerWidth <= BREAKPOINTS.tablet;
}

// Burger menu: only used on mobile (<=800px). On desktop/tablet, nav is always visible via CSS.
window.addEventListener('DOMContentLoaded', function() {
  var menuToggle = document.getElementById('menu-toggle');
  var burgerNav = document.getElementById('burger-nav');
  var burgerOverlay = document.getElementById('burger-overlay');
  var burgerLabel = document.getElementById('burger-label');

  function closeBurger() {
    if (menuToggle) menuToggle.checked = false;
    updateAria();
  }

  function updateAria() {
    if (!menuToggle || !burgerLabel) return;
    var expanded = menuToggle.checked;
    burgerLabel.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    if (burgerNav) burgerNav.setAttribute('aria-hidden', expanded ? 'false' : 'true');
    if (expanded && burgerNav) {
      var firstLink = burgerNav.querySelector('a');
      if (firstLink) firstLink.focus();
    }
  }

  if (menuToggle && burgerNav && burgerOverlay && burgerLabel) {
    burgerLabel.setAttribute('aria-controls', 'burger-nav');
    burgerLabel.setAttribute('aria-expanded', 'false');
    burgerLabel.setAttribute('role', 'button');
    burgerNav.setAttribute('aria-hidden', 'true');

    // Overlay click closes burger
    burgerOverlay.addEventListener('click', closeBurger);

    // Escape key closes burger
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && menuToggle.checked) {
        closeBurger();
      }
    });

    // Clicking a link inside burger closes it
    burgerNav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', closeBurger);
    });

    // Checkbox change updates aria
    menuToggle.addEventListener('change', updateAria);

    // If window resizes above mobile breakpoint, close burger
    window.addEventListener('resize', function() {
      if (!isMobile() && menuToggle.checked) {
        closeBurger();
      }
    });
  }
});

// Profile modal logic
function openProfileModal() {
  const overlay = document.getElementById('profile-modal-overlay');
  const body = document.getElementById('profile-modal-body');
  overlay.style.display = 'flex';
  body.innerHTML = '<div class="profile-modal-loading">Loading...</div>';
  fetch('/accounts/change/profile/?modal=1').then(r => r.text()).then(html => {
    body.innerHTML = html;
    const closeBtn = document.getElementById('profile-modal-close');
    closeBtn.onclick = closeProfileModal;
    const form = body.querySelector('form');
    if (form) {
      form.onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(form.action, {method:'POST', body:formData, headers:{'X-Requested-With':'XMLHttpRequest'}})
          .then(r => r.text()).then(html => {
            body.innerHTML = html;
          });
        return false;
      };
    }
  });
}
function closeProfileModal() {
  document.getElementById('profile-modal-overlay').style.display = 'none';
}
document.addEventListener('DOMContentLoaded', function() {
  var closeBtn = document.getElementById('profile-modal-close');
  if (closeBtn) closeBtn.onclick = closeProfileModal;
  var overlay = document.getElementById('profile-modal-overlay');
  if (overlay) overlay.onclick = function(e) {
    if (e.target === this) closeProfileModal();
  };
  document.querySelectorAll('a[href$="accounts/change_profile/"]').forEach(function(el) {
    el.addEventListener('click', function(e) {
      e.preventDefault();
      openProfileModal();
    });
  });
  var navPic = document.querySelector('nav img[alt="Profile"]');
  if (navPic && navPic.parentElement.tagName === 'A') {
    navPic.parentElement.addEventListener('click', function(e) {
      e.preventDefault();
      openProfileModal();
    });
  }
});
