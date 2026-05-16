// ============================================================
// HOMEPAGE interactions
// ============================================================

const magnifier     = document.getElementById('text-magnifier');
const magnifierText = document.getElementById('magnifier-text');
const magnifierLabel = document.getElementById('magnifier-label');
const magnifierCta  = document.getElementById('magnifier-cta');

let hideTimer = null;

function positionMagnifier(x, y) {
  const w = 380, margin = 20;
  const h = magnifier.offsetHeight || 120;
  let left = x + margin;
  let top  = y - h / 2;
  if (left + w > window.innerWidth  - margin) left = x - w - margin;
  if (top < margin)                            top  = margin;
  if (top + h > window.innerHeight - margin)   top  = window.innerHeight - h - margin;
  magnifier.style.left = left + 'px';
  magnifier.style.top  = top  + 'px';
}

// Show for chapter text sections (label + body text + CTA link)
function showSectionTip(section, x, y) {
  clearTimeout(hideTimer);
  magnifierLabel.textContent  = section.dataset.label;
  magnifierText.textContent   = section.dataset.text;
  magnifierCta.textContent    = '→ Read ' + section.dataset.label;
  magnifierCta.href           = section.dataset.url;
  magnifierCta.removeAttribute('hidden');
  positionMagnifier(x, y);
  magnifier.classList.add('visible');
}

// Show for duck images (label only, no body text, no link)
function showDuckTip(duck, x, y) {
  clearTimeout(hideTimer);
  magnifierLabel.textContent = duck.dataset.label;
  magnifierText.textContent  = '';
  magnifierCta.setAttribute('hidden', '');
  positionMagnifier(x, y);
  magnifier.classList.add('visible');
}

function hideMagnifier() {
  hideTimer = setTimeout(() => magnifier.classList.remove('visible'), 180);
}

// Chapter text sections
document.querySelectorAll('.home-section').forEach(section => {
  section.addEventListener('mouseenter', e => showSectionTip(section, e.clientX, e.clientY));
  section.addEventListener('mousemove',  e => showSectionTip(section, e.clientX, e.clientY));
  section.addEventListener('mouseleave', hideMagnifier);
  section.addEventListener('click', () => window.location.href = section.dataset.url);
});

// Duck images with labels
document.querySelectorAll('.duck[data-label]').forEach(duck => {
  duck.addEventListener('mouseenter', e => showDuckTip(duck, e.clientX, e.clientY));
  duck.addEventListener('mousemove',  e => showDuckTip(duck, e.clientX, e.clientY));
  duck.addEventListener('mouseleave', hideMagnifier);
});

// Keep magnifier open when hovering it directly
magnifier.addEventListener('mouseenter', () => clearTimeout(hideTimer));
magnifier.addEventListener('mouseleave', hideMagnifier);
