const stickyHeader = document.getElementById('sticky-header');
const scrollHidePoint = 160; // Set the point where you want to start hiding the header

window.addEventListener('scroll', function () {
    const scrollPosition = window.scrollY || window.pageYOffset;

    if (scrollPosition >= scrollHidePoint) {
        // Apply a class to hide the header with a fade-out effect
        stickyHeader.style.transition = 'opacity 0.5s'; // You can adjust the duration as needed
        stickyHeader.style.opacity = 0;
    } else {
        // Remove the class to make the header visible
        stickyHeader.style.transition = 'opacity 0.3s'; // You can adjust the duration as needed
        stickyHeader.style.opacity = 1;
    }
});
