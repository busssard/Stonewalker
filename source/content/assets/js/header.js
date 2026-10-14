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
    // Hide floating action buttons when burger menu is open to prevent overlap
    // on short mobile screens. The FABs are position:fixed at bottom-right and
    // can collide with the burger nav items on viewports shorter than ~700px.
    var fab = document.querySelector('.floating-action-bar');
    if (fab) {
      fab.style.display = expanded ? 'none' : '';
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

// Dark mode toggle
(function() {
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  function getPreferredTheme() {
    var saved = localStorage.getItem('theme');
    if (saved) return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  // Apply theme immediately on script load (before DOMContentLoaded)
  applyTheme(getPreferredTheme());

  function toggleDarkMode() {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('theme', next);
  }

  window.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('dark-mode-toggle');
    if (btn) {
      btn.addEventListener('click', toggleDarkMode);
    }
  });

  // Listen for OS theme changes
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
      if (!localStorage.getItem('theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  window.toggleDarkMode = toggleDarkMode;
})();

// Profile modal logic lives in profile-modal.js
