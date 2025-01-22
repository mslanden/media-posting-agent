// js/tabs.js

function fetchPosts() {
    fetch("/get_posts")
        .then((response) => response.json())
        .then((posts) => {
            const postList = document.getElementById("post-list");
            postList.innerHTML = "";
            posts.forEach((post) => {
                const listItem = document.createElement("li");
                listItem.textContent = `Tweet: ${post.tweet} Date: ${post.post_date} Time: ${post.post_time}`;
                postList.appendChild(listItem);
            });
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while loading scheduled posts.");
        });
}

function showTab(tabId) {
    const sidebar = document.getElementById("sidebar");
    const allTabs = ["scheduled-posts", "api-keys", "settings"];

    if (sidebar.style.display === "block" && sidebar.dataset.currentTab === tabId) {
        sidebar.style.display = "none";
        sidebar.dataset.currentTab = "";
        allTabs.forEach(id => {
            document.getElementById(id).style.display = "none";
        });
        return;
    }

    sidebar.style.display = "block";
    sidebar.dataset.currentTab = tabId;

    allTabs.forEach(id => {
        const tabContent = document.getElementById(id);
        if (tabContent) {
            tabContent.style.display = id === tabId ? "block" : "none";
        }
    });


    if (tabId === "scheduled-posts") {
        fetchPosts();
    } else if (tabId === "settings") {
        fetch("/settings_ui")
            .then(response => response.text())
            .then(html => {
                document.getElementById("settings").innerHTML = html;
                loadSettingsJS();
            })
            .catch(error => {
                console.error("Error loading settings:", error);
                alert("Failed to load settings.");
            });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("settings-button").addEventListener("click", () => {
        showTab("settings");
    });

    document.getElementById("scheduled-posts-button").addEventListener("click", () => {
        showTab("scheduled-posts");
    });
});
