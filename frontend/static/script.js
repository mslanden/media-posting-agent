// Function to show the selected tab
function showTab(tabId) {
    ["scheduled-posts", "api-keys", "settings"].forEach((id) => {
        document.getElementById(id).style.display = id === tabId ? "block" : "none";
    });
}

// Function to handle API calls
async function apiCall(url, method, data) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("API call failed:", error);
        alert("An error occurred. Please check the console for details.");
        return null;
    }
}

// Initialize sidebar with Scheduled Posts visible
document.addEventListener("DOMContentLoaded", async () => {
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

    // Fetch and display scheduled posts
    const scheduledPostsSelect = document.getElementById("scheduled-posts-select");
    const scheduledPosts = await apiCall("/api/scheduled", "GET");
    if (scheduledPosts) {
        scheduledPosts.forEach((post) => {
            const option = document.createElement("option");
            option.value = post.time;
            option.text = `${post.platform}: ${post.content}`;
            scheduledPostsSelect.appendChild(option);
        });
    }
});

// Handle chat form submission
document.getElementById("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.getElementById("message").value;
    const url = document.getElementById("url").value;
    const image = document.getElementById("image").files[0];
    const mediaType = document.getElementById("mediaType").value;
    const data = { task: message, url: url, image: image, mediaType: mediaType };
    const response = await apiCall("/api/task", "POST", data);
    if (response) {
        console.log("Response:", response);
        // Update UI with response
    }
});
