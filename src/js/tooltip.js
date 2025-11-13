document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tooltip.clickable').forEach(function (element) {
        element.addEventListener('click', function () {
            const href = this.getAttribute('data-href');
            if (href) {
                window.open(href, '_blank');
            }
        });
    });
});