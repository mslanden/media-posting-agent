document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("settings-form")
    .addEventListener("submit", function (event) {
      event.preventDefault();

      // Retrieve only the necessary settings
      const llmModel = document.getElementById("llm-model-select").value;
      const darkMode = document.getElementById("dark-mode-toggle").checked;

      fetch("/save_settings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          llm_model: llmModel,
          dark_mode: darkMode,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          const errorDiv = document.getElementById("settings-error");
          const successDiv = document.getElementById("settings-success");

          if (data.error) {
            errorDiv.textContent = data.error;
          } else {
            successDiv.textContent = "Settings saved successfully!";
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          document.getElementById("settings-error").textContent =
            "An unexpected error occurred.";
        });
    });
});
