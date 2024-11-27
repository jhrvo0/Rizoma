document.addEventListener("DOMContentLoaded", function () {
    // Function to show the modal
    function showModal() {
        const modalContainer = document.getElementById("popup-container");
        modalContainer.classList.remove("hidden"); // Show the modal
    }

    // Function to hide the modal
    function hideModal() {
        const modalContainer = document.getElementById("popup-container");
        modalContainer.classList.add("hidden"); // Hide the modal
    }

    // Close the modal when clicking outside of it
    document.addEventListener("click", function (event) {
        const modalContainer = document.getElementById("popup-container");
        if (event.target === modalContainer) {
            hideModal(); // Close modal if clicked outside
        }
    });

    // Prevent modal content from closing when clicked
    const modalContent = document.getElementById("popup-modal");
    modalContent.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    // Close modal when clicking the confirm button
    const confirmButton = document.getElementById("confirm-button");
    confirmButton.addEventListener("click", function (event) {
        hideModal();
    });

    const btn = document.getElementById("btn-aleatorio");
    btn.addEventListener("click", function (event) {
        showModal();
    });
});

document.addEventListener("DOMContentLoaded", function () {
    console.log("modal idiota");
});

function modalIdiota() {
    console.log("modal idiota");
}

modalIdiota();

