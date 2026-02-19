// stone-modal.js
export function openStoneModal(pk, color, stonesData) {
  // Ensure modal HTML exists
  let modal = document.getElementById('stone-gallery-modal');
  let modalBody;
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'stone-gallery-modal';
    modal.style.display = 'none';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(0,0,0,0.4)';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '3000';
    modal.innerHTML = `
      <div id="stone-gallery-content" style="background:#fff; border-radius:18px; max-width:600px; width:90vw; margin:auto; padding:2rem; position:relative; box-shadow:0 4px 32px rgba(0,0,0,0.18);">
        <span id="stone-gallery-close" style="position:absolute; top:1rem; right:1rem; font-size:2rem; cursor:pointer;">&times;</span>
        <div id="stone-gallery-body"></div>
      </div>
    `;
    document.body.appendChild(modal);
  } else {
    // Clean up any conflicting CSS classes
    modal.className = '';
    modal.style.display = 'none';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(0,0,0,0.4)';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '3000';
  }
  
  modalBody = document.getElementById('stone-gallery-body');
  const closeBtn = document.getElementById('stone-gallery-close');
  closeBtn.onclick = () => { modal.style.display = 'none'; };
  window.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };

  const stone = stonesData.find(s => s.PK_stone === pk);
  if (!stone) return;

  // Robustly deduplicate images, only show stone.png if no real images
  let images = [];
  const defaultImg = '/static/stone.png';
  const allImgs = [];
  if (stone.image) allImgs.push(stone.image);
  (stone.moves || []).forEach(m => { if (m.image) allImgs.push(m.image); });
  // Deduplicate by URL
  images = allImgs.filter((img, idx) => allImgs.indexOf(img) === idx && img && img !== '');
  // Remove stone.png if there are other images
  images = images.filter(img => !img.includes('stone.png'));
  if (images.length === 0) images = [defaultImg];

  let currentImg = 0;

  // Format creation date nicely for display
  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  // Sort moves by ISO timestamp descending (newest first)
  const sortedMoves = (stone.moves || []).slice().sort((a, b) => {
    if (!a.timestamp) return 1;
    if (!b.timestamp) return -1;
    return new Date(b.timestamp) - new Date(a.timestamp);
  });
  let html = `<div style='text-align:center;margin-bottom:1.2rem;'>
    <span style="font-family:var(--font-title);font-size:2.1rem;font-weight:700;letter-spacing:1px;color:${color};text-shadow:0 2px 8px rgba(0,0,0,0.07);">${stone.PK_stone}</span>
    ${stone.stone_number ? `<div style="font-size:0.85rem;color:#aaa;font-family:monospace;margin-top:0.2rem;">#${stone.stone_number}</div>` : ''}
  </div>`;
  if (images.length) {
    html += `<div style='display:flex;align-items:center;justify-content:center;gap:0.7rem;margin-bottom:0.3rem;padding:0;'>
      <button id='img-prev' style='background:none;border:none;font-size:2.2rem;color:${color};cursor:pointer;outline:none;'>&#8592;</button>
      <img id='main-img' src='${images[0]}' style='max-width:420px;max-height:320px;border-radius:18px;box-shadow:0 6px 32px rgba(0,0,0,0.13);border:3px solid ${color};background:#fff;transition:box-shadow 0.2s;margin:0;'/>
      <button id='img-next' style='background:none;border:none;font-size:2.2rem;color:${color};cursor:pointer;outline:none;'>&#8594;</button>
    </div>`;
    if (images.length > 1) {
      html += `<div style='display:flex;gap:0.5rem;flex-wrap:nowrap;overflow-x:auto;margin-bottom:1.2rem;padding-bottom:0.3rem;justify-content:center;'>`;
      images.forEach((img, idx) => {
        html += `<img src='${img}' class='thumb-img' data-idx='${idx}' style='width:60px;height:48px;object-fit:cover;border-radius:8px;border:2px solid ${color};background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.07);transition:transform 0.2s,border-color 0.2s;cursor:pointer;${idx===0?'border-color:'+color+';transform:scale(1.08);':''}'/>`;
      });
      html += `</div>`;
    }
  }
  html += `<div style="background:linear-gradient(90deg,${color}11 0%,#fff 100%);border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:1.2rem;font-size:1.13rem;font-family:var(--font-serif);box-shadow:0 2px 8px rgba(0,0,0,0.04);color:#333;">${stone.description}</div>`;
  html += `<div style='display:flex;justify-content:center;align-items:center;margin-bottom:1.2rem;font-size:1.05em;color:#888;font-family:monospace;gap:0;'>
    <div style='flex:1;min-width:120px;max-width:160px;text-align:center;padding:0 0.5em;'>
      <span style='display:block;font-size:0.97em;color:#aaa;'>Created</span>
      <span style='font-weight:600;color:#444;white-space:nowrap;'>${formatDate(stone.created_at)}</span>
    </div>
    <div style='width:1px;height:2.2em;background:#eee;margin:0 0.5em;'></div>
    <div style='flex:1;min-width:80px;max-width:120px;text-align:center;padding:0 0.5em;'>
      <span style='display:block;font-size:0.97em;color:#aaa;'>By</span>
      <span style='font-weight:600;color:${color};font-family:inherit;'>${stone.username}</span>
    </div>
    <div style='width:1px;height:2.2em;background:#eee;margin:0 0.5em;'></div>
    <div style='flex:1;min-width:80px;max-width:120px;text-align:center;padding:0 0.5em;'>
      <span style='display:block;font-size:0.97em;color:#aaa;'>Moves</span>
      <span style='font-weight:600;color:#444;'>${stone.moves.length}</span>
    </div>
    <div style='width:1px;height:2.2em;background:#eee;margin:0 0.5em;'></div>
    <div style='flex:1;min-width:80px;max-width:120px;text-align:center;padding:0 0.5em;'>
      <span style='display:block;font-size:0.97em;color:#aaa;'>Distance</span>
      <span style='font-weight:600;color:#444;'>${stone.distance_km} km</span>
    </div>
  </div>`;
  if (sortedMoves.length) {
    html += `<div style='margin-top:1.2rem;'><b style='font-family:inherit;color:${color};font-size:1.1em;'>Comments</b><div style='max-height:180px;overflow-y:auto;margin-top:0.7em;'><ul style='padding-left:0;'>`;
    sortedMoves.forEach(m => {
      if (m.comment && m.comment.trim()) {
        html += `<li style='margin-bottom:0.7em;list-style:none;display:flex;align-items:flex-start;gap:0.7em;'>
          <img src='${m.user_picture}' style='width:38px;height:38px;border-radius:50%;object-fit:cover;box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-top:2px;border:2px solid #eee;'/>
          <div style='flex:1;min-width:0;'>
            <div style='display:flex;align-items:baseline;gap:0.7em;'>
              <span style='font-weight:700;font-size:1.08em;color:${color};font-family:monospace;'>${m.username}</span>
              <span style='font-family:"Playfair Display",serif;font-size:1.08em;word-break:break-word;'>${m.comment.split('\n')[0]}</span>
            </div>
            <div style='display:flex;align-items:flex-start;gap:0.7em;'>
              <span style='font-size:0.93em;color:#888;min-width:70px;'>${m.timestamp_display}</span>
              <span style='font-family:"Playfair Display",serif;font-size:1.08em;word-break:break-word;'>${m.comment.split('\n').slice(1).join('<br>')}</span>
            </div>
          </div>
        </li>`;
      }
    });
    html += `</ul></div></div>`;
  }
  modalBody.innerHTML = `<div style='background:repeating-linear-gradient(135deg,${color}09 0 12px,transparent 12px 24px);border-radius:18px;padding:1.2rem 0.7rem;'>${html}</div>`;
  modal.style.display = 'flex';
  if (images.length) {
    const mainImg = document.getElementById('main-img');
    const thumbs = modalBody.querySelectorAll('.thumb-img');
    function setImg(idx) {
      currentImg = idx;
      mainImg.src = images[idx];
      thumbs.forEach((t,i) => {
        t.style.borderColor = i===idx?color:'#ccc';
        t.style.transform = i===idx?'scale(1.08)':'scale(1)';
      });
    }
    if (thumbs.length) {
      thumbs.forEach((t,i) => {
        t.onclick = () => setImg(i);
      });
    }
    document.getElementById('img-prev').onclick = function() {
      setImg((currentImg-1+images.length)%images.length);
    };
    document.getElementById('img-next').onclick = function() {
      setImg((currentImg+1)%images.length);
    };
  }
} 