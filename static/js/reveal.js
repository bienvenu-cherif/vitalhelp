// static/js/reveal.js
// Anime les éléments .reveal-on-scroll quand ils entrent dans le viewport.
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
});

// Active le top-loader pour les formulaires longs (analyse IA)
document.querySelectorAll('form[action*="lancer"], form[data-loader]').forEach(form => {
  form.addEventListener('submit', () => {
    const loader = document.getElementById('topLoader');
    if (loader) { loader.classList.add('is-loading'); }
  });
});