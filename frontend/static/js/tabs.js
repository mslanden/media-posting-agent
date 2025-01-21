// js/tabs.js

function showTab(tabId) {
  ["scheduled-posts", "api-keys", "settings"].forEach((id) => {
    document.getElementById(id).style.display = id === tabId ? "block" : "none";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  showTab("scheduled-posts");

  document
    .getElementById("sidebar-select")
    .addEventListener("change", (event) => {
      showTab(event.target.value);
    });
});
