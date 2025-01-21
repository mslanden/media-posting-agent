// js/dark-mode.js

document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("dark-mode-toggle")
    .addEventListener("change", (event) => {
      document.body.classList.toggle("dark-mode", event.target.checked);
    });
});
