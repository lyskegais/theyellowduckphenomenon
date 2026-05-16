// ============================================================
// HOMEPAGE — hover-enlarge interaction
// ============================================================

const magnifier = document.getElementById('text-magnifier');
const magnifierText = document.getElementById('magnifier-text');
const magnifierLabel = document.getElementById('magnifier-label');
const magnifierCta = document.getElementById('magnifier-cta');

let activeSection = null;
let hideTimer = null;

function showMagnifier(section, x, y) {
  clearTimeout(hideTimer);
  const text = section.dataset.text;
  const label = section.dataset.label;
  const url = section.dataset.url;

  magnifierLabel.textContent = label;
  magnifierText.textContent = text;
  magnifierCta.textContent = '→ Read ' + label;
  magnifierCta.href = url;

  // Position: prefer top-right area, avoid edges
  const w = 420;
  const h = 200;
  const margin = 20;
  let left = x + margin;
  let top = y - h / 2;

  if (left + w > window.innerWidth - margin) left = x - w - margin;
  if (top < margin) top = margin;
  if (top + h > window.innerHeight - margin) top = window.innerHeight - h - margin;

  magnifier.style.left = left + 'px';
  magnifier.style.top = top + 'px';
  magnifier.classList.add('visible');
}

function hideMagnifier() {
  hideTimer = setTimeout(() => {
    magnifier.classList.remove('visible');
    activeSection = null;
  }, 150);
}

// Attach hover listeners to each section
document.querySelectorAll('.home-section').forEach(section => {
  section.addEventListener('mouseenter', function(e) {
    activeSection = this;
    showMagnifier(this, e.clientX, e.clientY);
  });

  section.addEventListener('mousemove', function(e) {
    if (activeSection === this) {
      showMagnifier(this, e.clientX, e.clientY);
    }
  });

  section.addEventListener('mouseleave', hideMagnifier);

  section.addEventListener('click', function() {
    window.location.href = this.dataset.url;
  });
});

// Keep magnifier open when hovering over it
magnifier.addEventListener('mouseenter', () => clearTimeout(hideTimer));
magnifier.addEventListener('mouseleave', hideMagnifier);

// Embedded image click → project page
document.querySelectorAll('.home-image-embed').forEach(embed => {
  embed.addEventListener('click', function(e) {
    e.stopPropagation();
    window.location.href = this.dataset.url;
  });
});
