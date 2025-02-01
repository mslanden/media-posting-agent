document
  .getElementById("scrape-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const url = document.getElementById("url").value;
    fetch("/scrape", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "url=" + encodeURIComponent(url),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          alert("Success: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while scraping the URL.");
      });
  });

document
  .getElementById("chat-form")
  .addEventListener("submit", function (event) {
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
    formData.append("api_key", apiKey);
    formData.append("llm_model", llmModel);
    fetch("/generate", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          alert("Success: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while generating the output.");
      });
  });

document
  .getElementById("llm-model-select")
  .addEventListener("change", function () {
    const selectedModel = this.value;
    document.getElementById("openai-api-key-input").style.display = "none";
    document.getElementById("gemini-api-key-input").style.display = "none";
    document.getElementById("anthropic-api-key-input").style.display = "none";

    if (selectedModel === "openai") {
      document.getElementById("openai-api-key-input").style.display = "block";
    } else if (selectedModel === "gemini") {
      document.getElementById("gemini-api-key-input").style.display = "block";
    } else if (selectedModel === "anthropic") {
      document.getElementById("anthropic-api-key-input").style.display =
        "block";
    }
  });

document
  .getElementById("save-settings-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    const selectedModel = document.getElementById("llm-model-select").value;
    let apiKey = "";
    const darkMode = document.getElementById("dark-mode-toggle").checked;

    if (selectedModel === "openai") {
      apiKey = document.getElementById("openai-api-key").value;
    } else if (selectedModel === "gemini") {
      apiKey = document.getElementById("gemini-api-key").value;
    } else if (selectedModel === "anthropic") {
      apiKey = document.getElementById("anthropic-api-key").value;
    }

    fetch("/save_settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        api_key: apiKey,
        llm_model: selectedModel,
        dark_mode: darkMode,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          alert("Success: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while saving settings.");
      });
  });
