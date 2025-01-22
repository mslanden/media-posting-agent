document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("settings-form").addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        const llmModel = document.getElementById("llm-model-select").value;
        let apiKey = "";
        if (llmModel === "openai") {
            apiKey = document.getElementById("openai-api-key").value;
        } else if (llmModel === "gemini") {
            apiKey = document.getElementById("gemini-api-key").value;
        } else if (llmModel === "anthropic") {
            apiKey = document.getElementById("anthropic-api-key").value;
        }
        const darkMode = document.getElementById("dark-mode-toggle").checked;

        fetch("/save_settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                api_key: apiKey,
                llm_model: llmModel,
                dark_mode: darkMode,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                const errorDiv = document.getElementById("settings-error");
                if (data.error) {
                    errorDiv.textContent = "Error: " + data.error;
                } else {
                    errorDiv.textContent = "Success: " + data.message;
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while saving settings.");
            });
    });
});
