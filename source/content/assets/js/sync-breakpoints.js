// sync-breakpoints.js
// Usage: node source/content/assets/js/sync-breakpoints.js
// This script syncs the BREAKPOINTS in header.js with the px values in styles.css media queries.
// Run this after changing any breakpoint in header.js.

const fs = require('fs');
const path = require('path');

const headerJsPath = path.join(__dirname, 'header.js');
const stylesCssPath = path.join(__dirname, '../css/styles.css');

// 1. Read BREAKPOINTS from header.js
const headerJs = fs.readFileSync(headerJsPath, 'utf8');
const breakpointsMatch = headerJs.match(/const BREAKPOINTS = ([\s\S]*?);/);
if (!breakpointsMatch) {
  console.error('Could not find BREAKPOINTS object in header.js');
  process.exit(1);
}
let breakpoints;
try {
  // eslint-disable-next-line no-eval
  breakpoints = eval('(' + breakpointsMatch[1] + ')');
} catch (e) {
  console.error('Failed to parse BREAKPOINTS:', e);
  process.exit(1);
}

// 2. Read styles.css
let css = fs.readFileSync(stylesCssPath, 'utf8');

// 3. Replace all hardcoded px values in media queries
for (const [key, value] of Object.entries(breakpoints)) {
  // Replace (max-width: Npx) and (min-width: Npx)
  const reMax = new RegExp(`(max-width:\s*)${value}px`, 'g');
  const reMin = new RegExp(`(min-width:\s*)${value + 1}px`, 'g');
  css = css.replace(reMax, `$1${value}px`);
  css = css.replace(reMin, `$1${value + 1}px`);
}

// 4. Write back to styles.css
fs.writeFileSync(stylesCssPath, css, 'utf8');
console.log('Breakpoints synced from header.js to styles.css!'); 