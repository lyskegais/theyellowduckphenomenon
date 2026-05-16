// ============================================================
// HOMEPAGE interactions
// ============================================================

const magnifier      = document.getElementById('text-magnifier');
const magnifierImage = document.getElementById('magnifier-image');
const magnifierLabel = document.getElementById('magnifier-label');
const magnifierText  = document.getElementById('magnifier-text');
const magnifierCta   = document.getElementById('magnifier-cta');

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

// Chapter text sections (label + body text + CTA link)
function showSectionTip(section, x, y) {
  clearTimeout(hideTimer);
  magnifierLabel.textContent = section.dataset.label;
  magnifierImage.setAttribute('hidden', '');
  magnifierImage.src = '';
  magnifierText.textContent  = section.dataset.text || '';
  magnifierCta.textContent   = '→ Read ' + section.dataset.label;
  magnifierCta.href          = section.dataset.url;
  magnifierCta.removeAttribute('hidden');
  if (section.dataset.url) {
    magnifier.dataset.url = section.dataset.url;
  } else {
    delete magnifier.dataset.url;
  }
  positionMagnifier(x, y);
  magnifier.classList.add('visible');
}

// Duck images (label, optional image preview, optional URL)
function showDuckTip(duck, x, y) {
  clearTimeout(hideTimer);
  magnifierLabel.textContent = duck.dataset.label;

  if (duck.dataset.image) {
    magnifierImage.src = duck.dataset.image;
    magnifierImage.removeAttribute('hidden');
  } else {
    magnifierImage.setAttribute('hidden', '');
    magnifierImage.src = '';
  }

  magnifierText.textContent = '';

  if (duck.dataset.url) {
    magnifierCta.textContent = '→ Open';
    magnifierCta.href = duck.dataset.url;
    magnifierCta.removeAttribute('hidden');
    magnifier.dataset.url = duck.dataset.url;
  } else {
    magnifierCta.setAttribute('hidden', '');
    delete magnifier.dataset.url;
  }

  positionMagnifier(x, y);
  magnifier.classList.add('visible');
}

function hideMagnifier() {
  hideTimer = setTimeout(() => {
    magnifier.classList.remove('visible');
    magnifierImage.setAttribute('hidden', '');
    magnifierImage.src = '';
  }, 180);
}

// Chapter text sections
document.querySelectorAll('.home-section').forEach(section => {
  section.addEventListener('mouseenter', e => showSectionTip(section, e.clientX, e.clientY));
  section.addEventListener('mousemove',  e => showSectionTip(section, e.clientX, e.clientY));
  section.addEventListener('mouseleave', hideMagnifier);
  section.addEventListener('click', e => {
    // Don't navigate if the click is on a nested duck
    if (e.target.classList.contains('duck')) return;
    if (section.dataset.url) window.location.href = section.dataset.url;
  });
});

// Duck images with labels — stopPropagation so the parent .home-section
// listener doesn't override the duck tooltip when ducks are nested in chapters
document.querySelectorAll('.duck[data-label]').forEach(duck => {
  duck.addEventListener('mouseenter', e => {
    e.stopPropagation();
    showDuckTip(duck, e.clientX, e.clientY);
  });
  duck.addEventListener('mousemove', e => {
    e.stopPropagation();
    showDuckTip(duck, e.clientX, e.clientY);
  });
  duck.addEventListener('mouseleave', e => {
    e.stopPropagation();
    hideMagnifier();
  });
  duck.addEventListener('click', e => {
    e.stopPropagation();
    if (duck.dataset.url) window.location.href = duck.dataset.url;
  });
});

// Magnifier itself: stay open on hover, navigate on click if a URL is set
magnifier.addEventListener('mouseenter', () => clearTimeout(hideTimer));
magnifier.addEventListener('mouseleave', hideMagnifier);
magnifier.addEventListener('click', e => {
  // Let the inner <a> CTA handle its own click
  if (e.target.tagName === 'A') return;
  if (magnifier.dataset.url) window.location.href = magnifier.dataset.url;
});
