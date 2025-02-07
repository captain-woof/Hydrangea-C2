document.addEventListener('DOMContentLoaded', function() {
    // Get the header element
    const header = document.querySelector('header nav h1');

    // Check if the header element exists
    if (header) {
        // Add a class to trigger the animation
        header.classList.add('animated-header');
    }
});