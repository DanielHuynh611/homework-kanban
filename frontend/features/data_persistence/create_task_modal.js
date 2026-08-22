(() => {
  "use strict";
  const app = window.HomeworkKanban;
  if (!app.requireAuth()) return;

  const form = document.getElementById("task-form");
  const subjectSelect = document.getElementById("subject_id");
  const message = document.getElementById("task-message");
  document.getElementById("cancel-task").addEventListener("click", () => {
    location.assign("/board");
  });

  async function loadSubjects() {
    try {
      const payload = await app.request("/subjects");
      subjectSelect.replaceChildren(new Option("Select a subject…", ""));
      payload.subjects.forEach((subject) => {
        subjectSelect.add(new Option(subject.name, subject.id));
      });
      if (!payload.subjects.length) {
        app.showMessage(message, "Add a subject before creating a task.");
        subjectSelect.disabled = true;
        form.querySelector('button[type="submit"]').disabled = true;
      }
    } catch (error) {
      app.showMessage(message, error.message);
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    app.hideMessage(message);
    if (!form.reportValidity()) return;
    const values = Object.fromEntries(new FormData(form).entries());
    app.setBusy(form, true);
    try {
      await app.request("/tasks", { method: "POST", body: values });
      location.assign("/board");
    } catch (error) {
      app.showMessage(message, error.message);
    } finally {
      app.setBusy(form, false);
    }
  });

  loadSubjects();
})();
