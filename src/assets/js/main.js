// Mark active nav link
document.querySelectorAll('.site-nav a').forEach(link => {
  if (link.href === window.location.href) link.classList.add('active');
});
