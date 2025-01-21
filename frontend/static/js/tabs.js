// js/tabs.js

function showTab(tabId) {
  ["scheduled-posts", "api-keys", "settings"].forEach((id) => {
    document.getElementById(id).style.display = id === tabId ? "block" : "none";
  });
  if (tabId === "scheduled-posts") {
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
}

document.addEventListener("DOMContentLoaded", () => {
  const initialTab = document.getElementById("sidebar-select").value;
    if (initialTab === "settings") {
        showTab(initialTab);
    }

  document
    .getElementById("sidebar-select")
    .addEventListener("change", (event) => {
      showTab(event.target.value);
    });
});
