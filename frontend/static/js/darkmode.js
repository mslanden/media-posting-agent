// js/dark-mode.js

document.addEventListener("DOMContentLoaded", () => {
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  
  // Load saved dark mode preference
  const savedDarkMode = localStorage.getItem('darkMode');
  if (savedDarkMode === 'true') {
    document.body.classList.add('dark-mode');
    darkModeToggle.checked = true;
  }

  darkModeToggle.addEventListener("change", (event) => {
    document.body.classList.toggle("dark-mode", event.target.checked);
    // Save dark mode preference
    localStorage.setItem('darkMode', event.target.checked);
  });
});
