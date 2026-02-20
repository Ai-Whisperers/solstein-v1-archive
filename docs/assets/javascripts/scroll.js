/* Solstein — Scroll Parallax & Alchemical Ambient Effects */
document.addEventListener('DOMContentLoaded', function () {

    // ───────── PARALLAX VOID ─────────
    // The background stays still while the scroll moves, giving physicality.
    let lastScroll = 0;
    const body = document.body;

    window.addEventListener('scroll', function () {
        const currentScroll = window.scrollY;
        const parallaxOffset = currentScroll * 0.15;
        // Shift the background grain texture at a different rate to the content
        body.style.backgroundPosition = `center ${-parallaxOffset}px`;
        lastScroll = currentScroll;
    }, { passive: true });

    // ───────── RUNIC DROP-CAPS ─────────
    // Add data attributes to blockquote first chars for CSS targeting
    const blockquotes = document.querySelectorAll('blockquote p');
    blockquotes.forEach(function (bq) {
        const text = bq.textContent;
        if (text && text.length > 0) {
            bq.setAttribute('data-first-char', text[0]);
        }
    });

    // ───────── TABLE REVEAL ─────────
    // Animate tables into view with a stagger — like the page is being illuminated
    const tables = document.querySelectorAll('.md-typeset table');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        tables.forEach(function (table) {
            table.style.opacity = '0';
            table.style.transform = 'translateY(20px)';
            table.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(table);
        });
    }

    // ───────── SIGIL HOVER ON NAV ─────────
    // Add a subtle shimmer class on active nav items
    const activeLinks = document.querySelectorAll('.md-nav__link--active');
    activeLinks.forEach(function (link) {
        link.addEventListener('mouseenter', function () {
            link.style.textShadow = '0 0 15px rgba(232, 200, 74, 0.4)';
        });
        link.addEventListener('mouseleave', function () {
            link.style.textShadow = '';
        });
    });
});
