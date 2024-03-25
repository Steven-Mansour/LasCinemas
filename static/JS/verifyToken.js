document.addEventListener('DOMContentLoaded', function () {
    var inputs = document.querySelectorAll('input[name^="char"]');

    inputs.forEach(function (input, index, arr) {
        input.addEventListener('input', function () {
            if (this.value.length === this.maxLength) {
                // Move to the next input if it exists
                if (index < arr.length - 1) {
                    arr[index + 1].focus();
                }
            }
        });
    });
});

