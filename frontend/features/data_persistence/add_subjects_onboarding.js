(() => {
  "use strict";
  const app = window.HomeworkKanban;
  if (!app.requireAuth()) return;

  const form = document.getElementById("subject-form");
  const input = document.getElementById("subject-name");
  const list = document.getElementById("subjects-list");
  const message = document.getElementById("subject-message");
  const continueButton = document.getElementById("continue-button");

  function renderSubjects(subjects) {
    list.replaceChildren();
    continueButton.style.display = subjects.length ? "inline-flex" : "none";
    if (!subjects.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No subjects yet. Add your first subject above.";
      list.append(empty);
      return;
    }
    const group = document.createElement("div");
    group.style.cssText = "display:flex;flex-direction:column;gap:.75rem";
    subjects.forEach((subject) => {
      const row = document.createElement("div");
      row.className = "data-card";
      row.style.cssText = "display:flex;align-items:center;gap:.75rem";
      const mark = document.createElement("span");
      mark.textContent = "✓";
      mark.setAttribute("aria-hidden", "true");
      const name = document.createElement("span");
      name.style.fontWeight = "600";
      name.textContent = subject.name;
      row.append(mark, name);
      group.append(row);
    });
    list.append(group);
  }

  async function loadSubjects() {
    try {
      const payload = await app.request("/subjects");
      renderSubjects(payload.subjects);
    } catch (error) {
      app.showMessage(message, error.message);
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    app.hideMessage(message);
    if (!form.reportValidity()) return;
    app.setBusy(form, true);
    try {
      await app.request("/subjects", {
        method: "POST",
        body: { name: input.value },
      });
      form.reset();
      app.showMessage(message, "Subject added.", "success");
      await loadSubjects();
      input.focus();
    } catch (error) {
      app.showMessage(message, error.message);
    } finally {
      app.setBusy(form, false);
    }
  });

  loadSubjects();
})();
