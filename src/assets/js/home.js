// ============================================================
// HOMEPAGE interactions
// ============================================================

const magnifier = document.getElementById('text-magnifier');
const magnifierText = document.getElementById('magnifier-text');
const magnifierLabel = document.getElementById('magnifier-label');
const magnifierCta = document.getElementById('magnifier-cta');

let hideTimer = null;

function showMagnifier(section, x, y) {
  clearTimeout(hideTimer);
  magnifierLabel.textContent = section.dataset.label;
  magnifierText.textContent = section.dataset.text;
  magnifierCta.textContent = '→ Read ' + section.dataset.label;
  magnifierCta.href = section.dataset.url;

  const w = 380, margin = 20;
  const h = magnifier.offsetHeight || 160;
  let left = x + margin;
  let top  = y - h / 2;
  if (left + w > window.innerWidth - margin) left = x - w - margin;
  if (top < margin) top = margin;
  if (top + h > window.innerHeight - margin) top = window.innerHeight - h - margin;

  magnifier.style.left = left + 'px';
  magnifier.style.top  = top  + 'px';
  magnifier.classList.add('visible');
}

function hideMagnifier() {
  hideTimer = setTimeout(() => magnifier.classList.remove('visible'), 180);
}

// Text sections: hover to enlarge, click to navigate
document.querySelectorAll('.home-section').forEach(section => {
  section.addEventListener('mouseenter', e => showMagnifier(section, e.clientX, e.clientY));
  section.addEventListener('mousemove',  e => showMagnifier(section, e.clientX, e.clientY));
  section.addEventListener('mouseleave', hideMagnifier);
  section.addEventListener('click', () => window.location.href = section.dataset.url);
});

// Keep magnifier open when hovering it
magnifier.addEventListener('mouseenter', () => clearTimeout(hideTimer));
magnifier.addEventListener('mouseleave', hideMagnifier);

// Chapter markers are now <a> tags — no extra click handler needed.
// (data-url kept for any future JS hooks)

// Embedded images: click to navigate to project
document.querySelectorAll('.home-image-embed').forEach(embed => {
  embed.addEventListener('click', e => {
    e.stopPropagation();
    window.location.href = embed.dataset.url;
  });
});
