// Wait for the document to fully load
document.addEventListener('DOMContentLoaded', function() {

    // Example: Handling button clicks
    const exampleButton = document.getElementById('exampleButton');
    if (exampleButton) {
        exampleButton.addEventListener('click', function() {
            alert('Button clicked!');
        });
    }

    // Example: Toggling a dropdown menu
    const menuButton = document.getElementById('menuButton');
    const menu = document.getElementById('dropdownMenu');
    if (menuButton && menu) {
        menuButton.addEventListener('click', function() {
            menu.classList.toggle('show');
        });
    }

    // Example: Smooth scrolling to an anchor
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Example: Add more interactivity as needed
    // Add more custom JavaScript functions or event listeners here

});