document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (event) {
        const clickedElement = event.target.closest('.tooltip.clickable');
        
        if (clickedElement) {
            event.preventDefault();
            event.stopPropagation();
            
            const href = clickedElement.getAttribute('data-href');
            console.log('Clicked element:', clickedElement);
            console.log('Href:', href);
            
            if (href) {
                window.open(href, '_blank');
            }
        }
    });
});