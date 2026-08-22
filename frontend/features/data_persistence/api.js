(() => {
  "use strict";

  const API_BASE = "/api/capability_data_persistence_8e00a8e9";
  const TOKEN_KEY = "zorentia_access_token";
  const USER_KEY = "zorentia_user";

  function token() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function saveSession(payload) {
    localStorage.setItem(TOKEN_KEY, payload.token);
    localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function requireAuth() {
    if (token()) return true;
    const returnTo = encodeURIComponent(location.pathname + location.search);
    location.replace(`/login?next=${returnTo}`);
    return false;
  }

  async function request(path, { method = "GET", body, auth = true } = {}) {
    const headers = { Accept: "application/json" };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth && token()) headers.Authorization = `Bearer ${token()}`;

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch (_error) {
      throw new Error("Cannot reach the server. Check your connection and try again.");
    }

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && auth) {
        clearSession();
        location.replace("/login");
      }
      const error = new Error(payload.message || `Request failed (${response.status})`);
      error.status = response.status;
      error.code = payload.code;
      throw error;
    }
    return payload;
  }

  function showMessage(element, message, type = "error") {
    if (!element) return;
    element.classList.toggle("alert-error", type === "error");
    element.classList.toggle("alert-success", type === "success");
    element.textContent = message;
    element.hidden = false;
  }

  function hideMessage(element) {
    if (element) element.hidden = true;
  }

  function setBusy(form, busy) {
    form.dataset.loading = String(busy);
    form.querySelectorAll("button, input, select, textarea").forEach((control) => {
      control.disabled = busy;
    });
  }

  function notify(message) {
    let notice = document.getElementById("global-notice");
    if (!notice) {
      notice = document.createElement("div");
      notice.id = "global-notice";
      notice.className = "alert alert-success";
      notice.setAttribute("role", "status");
      notice.style.cssText = "position:fixed;right:20px;top:88px;z-index:100;box-shadow:0 12px 30px rgba(15,23,42,.16)";
      document.body.append(notice);
    }
    notice.textContent = message;
    notice.hidden = false;
    clearTimeout(notice.hideTimer);
    notice.hideTimer = setTimeout(() => { notice.hidden = true; }, 2500);
  }

  function installSharedControls() {
    document.querySelectorAll('.btn-icon[aria-label="Notifications"]').forEach((button) => {
      button.title = "No new notifications";
      button.addEventListener("click", () => { notify("You have no new notifications."); });
    });
    document.querySelectorAll(".user-avatar").forEach((button) => {
      button.title = "Log out";
      button.addEventListener("click", () => { location.href = "/logout"; });
    });
    document.querySelectorAll(".mobile-menu-toggle").forEach((button) => {
      button.addEventListener("click", () => {
        const sidebar = document.querySelector(".app-shell > .app-sidebar");
        if (!sidebar) return;
        const expanded = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!expanded));
        sidebar.hidden = expanded;
      });
    });
  }

  window.HomeworkKanban = {
    API_BASE,
    clearSession,
    hideMessage,
    request,
    requireAuth,
    saveSession,
    setBusy,
    showMessage,
    token,
  };

  installSharedControls();
})();
