// Мобильное меню, scroll-reveal, аккордеон FAQ
(function () {
    'use strict';

    // ---- Мобильное меню ----
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            nav.classList.toggle('open');
            toggle.classList.toggle('active');
        });
    }

    // ---- Scroll-reveal через IntersectionObserver ----
    var revealEls = document.querySelectorAll('[data-reveal]');
    if ('IntersectionObserver' in window && revealEls.length) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        revealEls.forEach(function (el) { observer.observe(el); });
    } else {
        revealEls.forEach(function (el) { el.classList.add('is-visible'); });
    }

    // ---- Аккордеон (FAQ) ----
    document.querySelectorAll('.accordion-trigger').forEach(function (trigger) {
        trigger.addEventListener('click', function () {
            var item = trigger.closest('.accordion-item');
            var panel = item.querySelector('.accordion-panel');
            var isOpen = item.classList.toggle('open');
            panel.style.maxHeight = isOpen ? panel.scrollHeight + 'px' : null;
        });
    });
})();
