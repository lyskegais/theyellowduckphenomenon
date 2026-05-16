// ============================================================
// THESIS PAGES — footnote tooltips + bibliography links
// ============================================================

// Create tooltip element
const tooltip = document.createElement('div');
tooltip.className = 'fn-tooltip';
document.body.appendChild(tooltip);

// Collect all footnote contents
const footnoteContents = {};
document.querySelectorAll('.footnotes li').forEach(li => {
  const id = li.id; // e.g. "fn1"
  // Strip the back-link arrow from the footnote text
  const clone = li.cloneNode(true);
  const backref = clone.querySelector('.footnote-backref');
  if (backref) backref.remove();
  footnoteContents[id] = clone.textContent.trim();
});

// Wire up footnote refs to show tooltips
document.querySelectorAll('.footnote-ref a, sup a[href^="#fn"]').forEach(ref => {
  const targetId = ref.getAttribute('href').replace('#', '');

  ref.addEventListener('mouseenter', function(e) {
    const content = footnoteContents[targetId];
    if (!content) return;
    tooltip.textContent = content;
    positionTooltip(e.clientX, e.clientY);
    tooltip.classList.add('visible');
  });

  ref.addEventListener('mousemove', function(e) {
    positionTooltip(e.clientX, e.clientY);
  });

  ref.addEventListener('mouseleave', function() {
    tooltip.classList.remove('visible');
  });

  // Clicking footnote ref → smooth scroll to bibliography item or footnote
  ref.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.style.transition = 'background 0.3s';
      target.style.background = 'rgba(158,155,148,0.15)';
      setTimeout(() => { target.style.background = ''; }, 1500);
    }
  });
});

function positionTooltip(x, y) {
  const w = 340;
  const margin = 16;
  let left = x + margin;
  let top = y - 60;
  if (left + w > window.innerWidth - margin) left = x - w - margin;
  if (top < margin) top = margin;
  tooltip.style.left = left + 'px';
  tooltip.style.top = top + 'px';
}

// Lightbox for thesis inline images
document.querySelectorAll('.thesis-image img').forEach(img => {
  img.style.cursor = 'zoom-in';
  img.addEventListener('click', function() {
    openLightbox(this.src, this.alt);
  });
});

function openLightbox(src, alt) {
  const lb = document.createElement('div');
  lb.className = 'lightbox open';
  lb.innerHTML = `
    <div class="lightbox-close">[ close ]</div>
    <img src="${src}" alt="${alt}">
  `;
  document.body.appendChild(lb);
  lb.addEventListener('click', () => lb.remove());
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') { lb.remove(); document.removeEventListener('keydown', esc); }
  });
}
