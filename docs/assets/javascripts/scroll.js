/* Scroll ambient effect — subtle parchment particle drift */
document.addEventListener('DOMContentLoaded', function () {
    // Add a subtle wax seal watermark to the hero page
    const content = document.querySelector('.md-content__inner');
    if (!content) return;

    // Add runic drop-caps to blockquotes on LORE pages
    const blockquotes = document.querySelectorAll('blockquote p');
    blockquotes.forEach(function (bq) {
        const text = bq.textContent;
        if (text && text.length > 0) {
            bq.setAttribute('data-first-char', text[0]);
        }
    });

    // Animate tables in with a stagger when they scroll into view
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
            table.style.transform = 'translateY(16px)';
            table.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(table);
        });
    }
});
