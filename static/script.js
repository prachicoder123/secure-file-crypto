// Tab switching
const tabButtons = document.querySelectorAll(".tab-btn");
const panels = document.querySelectorAll(".panel");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`${btn.dataset.tab}-panel`).classList.add("active");
  });
});

function setupDropZone(dropId, inputId, filenameId) {
  const dropZone = document.getElementById(dropId);
  const input = document.getElementById(inputId);
  const filenameEl = document.getElementById(filenameId);

  dropZone.addEventListener("click", () => input.click());

  input.addEventListener("change", () => {
    if (input.files.length > 0) {
      filenameEl.textContent = input.files[0].name;
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      input.files = e.dataTransfer.files;
      filenameEl.textContent = input.files[0].name;
    }
  });
}

setupDropZone("encrypt-drop", "encrypt-file", "encrypt-filename");
setupDropZone("decrypt-drop", "decrypt-file", "decrypt-filename");

async function handleSubmit(formId, endpoint, statusId, submitBtnSelector) {
  const form = document.getElementById(formId);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const statusEl = document.getElementById(statusId);
    const btn = form.querySelector(submitBtnSelector);

    const formData = new FormData(form);
    if (!formData.get("file") || formData.get("file").name === "") {
      statusEl.textContent = "Please choose a file first.";
      statusEl.className = "status error";
      return;
    }

    btn.disabled = true;
    statusEl.textContent = "Processing...";
    statusEl.className = "status working";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Operation failed.");
      }

      // Extract filename from Content-Disposition header if present
      const disposition = response.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/);
      const downloadName = match ? match[1] : "output_file";

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = downloadName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      statusEl.textContent = `Done — downloaded as "${downloadName}"`;
      statusEl.className = "status success";
    } catch (err) {
      statusEl.textContent = err.message;
      statusEl.className = "status error";
    } finally {
      btn.disabled = false;
    }
  });
}

handleSubmit("encrypt-form", "/encrypt", "encrypt-status", ".action-btn");
handleSubmit("decrypt-form", "/decrypt", "decrypt-status", ".action-btn");
