document.addEventListener('DOMContentLoaded', function () {
    const screeningItems = document.querySelectorAll('.cursor-pointer');

    screeningItems.forEach(item => {
        item.addEventListener('mouseover', function () {
            const description = item.dataset.description;
            const duration = item.dataset.duration;
            const pgrating = item.dataset.pgrating;
            const genre = item.dataset.genre;

            // Example: You can customize this based on how you want to display the information
            console.log(`Description: ${description}, Duration: ${duration}, PGRating: ${pgrating}, Genre: ${genre}`);
        });
    });
});
