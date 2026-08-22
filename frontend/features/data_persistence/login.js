(() => {
  "use strict";
  const app = window.HomeworkKanban;
  const form = document.getElementById("login-form");
  const message = document.getElementById("login-message");

  if (new URLSearchParams(location.search).has("created")) {
    app.showMessage(message, "Account created. Sign in to continue.", "success");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    app.hideMessage(message);
    if (!form.reportValidity()) return;
    const values = Object.fromEntries(new FormData(form).entries());
    app.setBusy(form, true);
    try {
      const payload = await app.request("/auth/login", {
        method: "POST",
        body: values,
        auth: false,
      });
      app.saveSession(payload);
      const requested = new URLSearchParams(location.search).get("next");
      const destination = requested && requested.startsWith("/") && !requested.startsWith("//")
        ? requested
        : "/onboarding/subjects";
      location.assign(destination);
    } catch (error) {
      app.showMessage(message, error.message);
    } finally {
      app.setBusy(form, false);
    }
  });
})();
