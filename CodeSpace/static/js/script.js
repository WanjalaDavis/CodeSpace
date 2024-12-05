
document.addEventListener('DOMContentLoaded', function () {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('showLogin')) {
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            loginModal.show();
        }
    });

 // Set a timeout to hide the success message after 5 seconds
        setTimeout(function() {
            const successMessage = document.getElementById('successMessage');
            if (successMessage) {
                successMessage.classList.add('hidden');  // Add hidden class to fade out
            }
        }, 5000);  // 5000 milliseconds = 5 seconds

document.addEventListener("DOMContentLoaded", function () {
        const handImage = document.getElementById('wavingHand');

        // Start waving animation when the page loads
        handImage.classList.add('waving');

        // Optional: Add a hover effect to make it interactive
        handImage.addEventListener('mouseenter', () => {
            handImage.classList.add('waving');
        });

        handImage.addEventListener('mouseleave', () => {
            handImage.classList.remove('waving');
        });
    });