document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        var messages = document.querySelectorAll('.message');
        messages.forEach(function (message) {
            message.style.display = 'none';
        });
    }, 3000); // Hide messages after 3 seconds
});