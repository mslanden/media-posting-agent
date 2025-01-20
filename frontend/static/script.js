// Function to show the selected tab
function showTab(tabId) {
    ["scheduled-posts", "api-keys", "settings"].forEach((id) => {
        document.getElementById(id).style.display = id === tabId ? "block" : "none";
    });
}

// Initialize sidebar with Scheduled Posts visible
document.addEventListener("DOMContentLoaded", () => {
    // Show the default tab on load
    showTab("scheduled-posts");

    // Handle sidebar dropdown change
    document
        .getElementById("sidebar-select")
        .addEventListener("change", (event) => {
            const selectedTab = event.target.value;
            showTab(selectedTab);
        });

    // Handle dark mode toggle
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    darkModeToggle.addEventListener("change", (event) => {
        document.body.classList.toggle("dark-mode", event.target.checked);
    });
});
