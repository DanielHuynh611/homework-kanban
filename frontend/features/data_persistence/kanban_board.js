(() => {
  "use strict";
  const app = window.HomeworkKanban;
  if (!app.requireAuth()) return;

  const message = document.getElementById("board-message");
  const columnIds = {
    to_do: "col-to_do",
    in_progress: "col-in_progress",
    done: "col-done",
  };
  const priorityColors = {
    low: "#10B981",
    medium: "#6366F1",
    high: "#C0362C",
  };
  let subjects = {};

  function field(label, value) {
    const container = document.createElement("div");
    container.className = "field";
    const labelNode = document.createElement("span");
    labelNode.className = "label";
    labelNode.textContent = label;
    const valueNode = document.createElement("span");
    valueNode.textContent = value;
    container.append(labelNode, valueNode);
    return container;
  }

  function urgency(dueDateValue) {
    const dueDate = new Date(`${dueDateValue}T23:59:59`);
    const difference = Math.ceil((dueDate - new Date()) / 86400000);
    if (difference < 0) return ["Overdue", "#C0362C"];
    if (difference <= 2) return ["Due soon", "#F59E0B"];
    return null;
  }

  function taskCard(task) {
    const card = document.createElement("article");
    card.className = "data-card task-card";
    card.draggable = true;
    card.dataset.taskId = task.id;
    card.dataset.status = task.status;
    card.style.cssText = "border:1px solid #E2E8F0;border-radius:14px;padding:12px;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.05)";

    const header = document.createElement("div");
    header.style.cssText = "display:flex;justify-content:space-between;align-items:center;gap:8px";
    const title = document.createElement("h2");
    title.textContent = task.title;
    title.style.cssText = "font-size:1rem;margin:0;color:#1E293B";
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = task.priority[0].toUpperCase() + task.priority.slice(1);
    badge.style.cssText = `background:${priorityColors[task.priority]};color:#fff`;
    header.append(title, badge);

    const urgent = urgency(task.due_date);
    if (urgent) {
      const urgentBadge = document.createElement("span");
      urgentBadge.className = "badge";
      urgentBadge.textContent = urgent[0];
      urgentBadge.style.cssText = `margin-top:8px;background:${urgent[1]};color:#fff`;
      card.append(header, urgentBadge);
    } else {
      card.append(header);
    }
    const details = document.createElement("div");
    details.style.cssText = "display:grid;gap:8px;margin-top:12px";
    details.append(
      field("Subject", subjects[task.subject_id] || "Unknown subject"),
      field("Due", task.due_date),
    );
    card.append(details);
    card.addEventListener("dragstart", (event) => {
      event.dataTransfer.setData("text/plain", task.id);
      event.dataTransfer.effectAllowed = "move";
    });
    return card;
  }

  function renderTasks(tasks) {
    Object.values(columnIds).forEach((id) => {
      const column = document.getElementById(id);
      column.replaceChildren();
    });
    tasks.forEach((task) => {
      document.getElementById(columnIds[task.status])?.append(taskCard(task));
    });
    Object.values(columnIds).forEach((id) => {
      const column = document.getElementById(id);
      if (!column.children.length) {
        const empty = document.createElement("p");
        empty.className = "column-empty";
        empty.style.cssText = "color:#667085;font-size:.875rem";
        empty.textContent = "No tasks here.";
        column.append(empty);
      }
    });
  }

  async function loadBoard() {
    app.hideMessage(message);
    try {
      const [subjectPayload, taskPayload] = await Promise.all([
        app.request("/subjects"),
        app.request("/tasks"),
      ]);
      subjects = Object.fromEntries(subjectPayload.subjects.map((subject) => [subject.id, subject.name]));
      renderTasks(taskPayload.tasks);
    } catch (error) {
      app.showMessage(message, error.message);
    }
  }

  Object.entries(columnIds).forEach(([status, id]) => {
    const column = document.getElementById(id);
    column.addEventListener("dragover", (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    });
    column.addEventListener("drop", async (event) => {
      event.preventDefault();
      const taskId = event.dataTransfer.getData("text/plain");
      const card = document.querySelector(`.task-card[data-task-id="${CSS.escape(taskId)}"]`);
      if (!card || card.dataset.status === status) return;
      const originalStatus = card.dataset.status;
      column.querySelector(".column-empty")?.remove();
      column.append(card);
      card.dataset.status = status;
      try {
        await app.request(`/tasks/${encodeURIComponent(taskId)}/status`, {
          method: "PATCH",
          body: { status },
        });
        await loadBoard();
      } catch (error) {
        card.dataset.status = originalStatus;
        document.getElementById(columnIds[originalStatus]).append(card);
        app.showMessage(message, error.message);
      }
    });
  });

  loadBoard();
})();
