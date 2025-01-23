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
        const twitterApiKey = document.getElementById("twitter_api_key").value;
        const twitterApiSecret = document.getElementById("twitter_api_secret").value;
        const twitterAccessToken = document.getElementById("twitter_access_token").value;
        const twitterAccessTokenSecret = document.getElementById("twitter_access_token_secret").value;

        const linkedinClientId = document.getElementById("linkedin_client_id").value;
        const linkedinClientSecret = document.getElementById("linkedin_client_secret").value;
        const linkedinClientSecret = document.getElementById("linkedin_client_secret").value;
        const linkedinAccessToken = document.getElementById("linkedin_access_token").value;
        const twitterBearerToken = document.getElementById("twitter_bearer_token").value;

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
                twitter_api_key: twitterApiKey,
                twitter_api_secret: twitterApiSecret,
                twitter_access_token: twitterAccessToken,
                twitter_access_token_secret: twitterAccessTokenSecret,
                linkedin_client_id: linkedinClientId,
                linkedin_client_secret: linkedinClientSecret,
                linkedin_client_secret: linkedinClientSecret, // Add this line
                linkedin_access_token: linkedinAccessToken,
                twitter_bearer_token: twitterBearerToken,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                const errorDiv = document.getElementById("settings-error");
                const successDiv = document.getElementById("settings-success"); // Add this line

                if (data.error) {
                    errorDiv.textContent = data.error; // More specific error message
                } else {
                    successDiv.textContent = "Settings saved successfully!"; // Display success message
                    setTimeout(() => {
                        window.location.reload(); // Refresh only on success
                    }, 1000); // Refresh after 1 second
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                errorDiv.textContent = "An unexpected error occurred."; // Generic error message
            });
    });
});
