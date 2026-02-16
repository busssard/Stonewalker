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
// Set as CSS custom properties for reference/debugging
Object.entries(BREAKPOINTS).forEach(([key, value]) => {
  document.documentElement.style.setProperty(`--breakpoint-${key.toLowerCase()}`, value + 'px');
});

function isMobile() {
  return window.innerWidth <= BREAKPOINTS.desktop;
}

// Burger menu open/close logic with overlay and accessibility (checkbox-driven, no double toggle)
window.addEventListener('DOMContentLoaded', function() {
  var menuToggle = document.getElementById('menu-toggle');
  var burgerNav = document.getElementById('burger-nav');
  var burgerOverlay = document.getElementById('burger-overlay');
  var burgerLabel = document.getElementById('burger-label');
  function updateAria() {
    var expanded = menuToggle.checked;
    burgerLabel.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    if (burgerNav) burgerNav.setAttribute('aria-hidden', expanded ? 'false' : 'true');
    if (expanded && burgerNav) {
      var firstLink = burgerNav.querySelector('a');
      if (firstLink) firstLink.focus();
    }
    // Hide floating action buttons when burger menu is open to prevent overlap
    // on short mobile screens. The FABs are position:fixed at bottom-right and
    // can collide with the burger nav items on viewports shorter than ~700px.
    var fab = document.querySelector('.floating-action-bar');
    if (fab) {
      fab.style.display = expanded ? 'none' : '';
    }
  }
  if (menuToggle && burgerNav && burgerOverlay) {
    burgerLabel.setAttribute('aria-controls', 'burger-nav');
    burgerLabel.setAttribute('aria-expanded', 'false');
    burgerLabel.setAttribute('role', 'button');
    burgerNav.setAttribute('aria-hidden', 'true');
    burgerOverlay.addEventListener('click', function() {
      menuToggle.checked = false;
      updateAria();
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && menuToggle.checked) {
        menuToggle.checked = false;
        updateAria();
      }
    });
    burgerNav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        menuToggle.checked = false;
        updateAria();
      });
    });
    menuToggle.addEventListener('change', updateAria);
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
    // Re-attach close/cancel logic if needed
    const closeBtn = document.getElementById('profile-modal-close');
    closeBtn.onclick = closeProfileModal;
    // Prevent form submission from navigating away
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
  // Also attach to profile picture in nav if present
  const navPic = document.querySelector('nav img[alt="Profile"]');
  if (navPic && navPic.parentElement.tagName === 'A') {
    navPic.parentElement.addEventListener('click', function(e) {
      e.preventDefault();
      openProfileModal();
    });
  }
});
window.addEventListener('DOMContentLoaded', function() {
  var menuToggle = document.getElementById('menu-toggle');
  var mainNav = document.getElementById('main-nav');
  var burgerLabel = document.getElementById('burger-label');
  var profileMenuBtn = document.getElementById('profile-menu-btn');
  var profileMainNav = document.getElementById('profile-main-nav');
  var burgerOverlay = document.getElementById('burger-overlay');
    var profileMenuContainer = document.getElementById('profile-menu-container');
    var burgerMenuContainer = document.getElementById('burger-menu-container');
    var debugFrame1 = document.getElementById('debug-frame1');
    var debugFrame2 = document.getElementById('debug-frame2');


  function closeMenus() {
    if (menuToggle) menuToggle.checked = false;
    if (mainNav) mainNav.classList.remove('header-main-nav--slide-in');
    if (profileMainNav) profileMainNav.classList.remove('header-profile-main-nav--slide-in');
    if (burgerOverlay) burgerOverlay.style.display = 'none';
  }

  function openBurgerMenu() {
    closeMenus();
    if (mainNav) mainNav.classList.add('header-main-nav--slide-in');
    if (burgerOverlay) burgerOverlay.style.display = 'block';
    if (menuToggle) menuToggle.checked = true;
  }
  function openProfileMenu() {
    closeMenus();
    if (profileMainNav) profileMainNav.classList.add('header-profile-main-nav--slide-in');
    if (burgerOverlay) burgerOverlay.style.display = 'block';
  }

  // Desktop: use container hover/focus to open menus
  if (burgerMenuContainer && mainNav) {
    burgerMenuContainer.addEventListener('click', function() {
      if (!isMobile()) openBurgerMenu();
    });
  }
  if (profileMenuContainer && profileMainNav) {
    profileMenuContainer.addEventListener('click', function() {
      if (!isMobile()) openProfileMenu();
    });
  }

  // Mobile: click to open menus (unchanged)
  if (profileMenuBtn && profileMainNav) {
    profileMenuBtn.addEventListener('click', function(e) {
      if (isMobile()) {
        e.preventDefault();
        if (profileMainNav.classList.contains('header-profile-main-nav--slide-in')) {
          closeMenus();
        } else {
          closeMenus();
          openProfileMenu();
        }
      }
    });
  }
  if (menuToggle && mainNav) {
    menuToggle.addEventListener('change', function() {
      if (isMobile()) {
        if (menuToggle.checked) {
          closeMenus();
          openBurgerMenu();
        } else {
          closeMenus();
        }
      }
    });
    window.addEventListener('resize', function() {
      if (isMobile()) closeMenus();
    });
  }

  // Overlay always closes both menus
  if (burgerOverlay) {
    burgerOverlay.addEventListener('click', function() {
      closeMenus();
    });
  }

  // Escape key closes both menus
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMenus();
    }
  });

  // Clicking outside menus closes them (mobile)
  document.addEventListener('click', function(e) {
    if (isMobile()) {
      if (profileMainNav && !profileMainNav.contains(e.target) && e.target !== profileMenuBtn && !profileMenuBtn.contains(e.target)) {
        profileMainNav.classList.remove('header-profile-main-nav--slide-in');
        if (burgerOverlay) burgerOverlay.style.display = 'none';
      }
      if (mainNav && !mainNav.contains(e.target) && e.target !== menuToggle && e.target !== burgerLabel) {
        if (menuToggle) menuToggle.checked = false;
        mainNav.classList.remove('header-main-nav--slide-in');
        if (burgerOverlay) burgerOverlay.style.display = 'none';
      }
      if (
        (!mainNav || !mainNav.classList.contains('header-main-nav--slide-in')) &&
        (!profileMainNav || !profileMainNav.classList.contains('header-profile-main-nav--slide-in'))
      ) {
        if (burgerOverlay) burgerOverlay.style.display = 'none';
      }
    }
  });

  // Menu links close menus
  if (mainNav) {
    mainNav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        closeMenus();
      });
    });
  }
  if (profileMainNav) {
    profileMainNav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        closeMenus();
      });
    });
  }
}); 