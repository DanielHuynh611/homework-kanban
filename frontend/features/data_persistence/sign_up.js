(() => {
  "use strict";
  const app = window.HomeworkKanban;
  const form = document.getElementById("signup-form");
  const message = document.getElementById("signup-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    app.hideMessage(message);
    if (!form.reportValidity()) return;
    const values = Object.fromEntries(new FormData(form).entries());
    app.setBusy(form, true);
    try {
      await app.request("/users", { method: "POST", body: values, auth: false });
      app.showMessage(message, "Account created. Taking you to sign in…", "success");
      location.assign("/login?created=1");
    } catch (error) {
      app.showMessage(message, error.message);
    } finally {
      app.setBusy(form, false);
    }
  });
})();
