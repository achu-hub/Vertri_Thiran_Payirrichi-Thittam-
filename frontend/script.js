const $ = (id) => document.getElementById(id);

function setStatus(message) {
  $("status").textContent = message;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function generateComic() {
  const prompt = $("prompt").value.trim();
  const genre = $("genre").value;
  const characters = $("characters").value.trim();
  const panels = Number($("panels").value);

  if (!prompt) {
    setStatus("Please enter a story idea.");
    $("prompt").focus();
    return;
  }

  if (!Number.isInteger(panels) || panels < 1 || panels > 12) {
    setStatus("Panels must be between 1 and 12.");
    return;
  }

  const button = $("generateBtn");
  button.disabled = true;
  setStatus("Gemini is writing your comic story...");
  $("result").classList.add("hidden");

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({prompt, genre, characters, panels})
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Story generation failed.");
    }

    renderComic(data);
    setStatus("Story generated. You can now generate images for each panel.");
  } catch (error) {
    setStatus(error.message);
  } finally {
    button.disabled = false;
  }
}

function renderComic(data) {
  $("title").textContent = data.title || "Untitled Comic";
  $("summary").textContent = data.summary || "";

  const container = $("panelsContainer");
  container.innerHTML = "";

  (data.panels || []).forEach((panel) => {
    const article = document.createElement("article");
    article.className = "panel";

    const dialogue = (panel.dialogue || [])
      .map(
        (line) =>
          `<p class="dialogue"><span class="speaker">${escapeHtml(line.speaker)}:</span> ${escapeHtml(line.text)}</p>`
      )
      .join("");

    article.innerHTML = `
      <div class="image-placeholder">
        <div class="panel-image"></div>
      </div>
      <div class="panel-content">
        <p class="panel-number">Panel ${escapeHtml(panel.panel_number)}</p>
        <p>${escapeHtml(panel.scene)}</p>
        <p class="caption">${escapeHtml(panel.caption)}</p>
        ${dialogue}
        <button class="image-button">Generate Panel Image</button>
      </div>
    `;

    const imageArea = article.querySelector(".panel-image");
    const imageButton = article.querySelector(".image-button");

    imageButton.addEventListener("click", async () => {
      imageButton.disabled = true;
      imageButton.textContent = "Generating image...";

      try {
        const imagePrompt = panel.image_prompt || panel.scene;
        const response = await fetch("/api/generate-image", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            panel_number: panel.panel_number,
            description: imagePrompt
          })
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || "Image generation failed.");
        }

        imageArea.innerHTML = `<img class="panel-image" src="${result.url}?t=${Date.now()}" alt="Generated comic panel">`;
        imageButton.textContent = "Image Generated";
      } catch (error) {
        imageButton.disabled = false;
        imageButton.textContent = "Generate Panel Image";
        setStatus(error.message);
      }
    });

    container.appendChild(article);
  });

  $("result").classList.remove("hidden");
}
