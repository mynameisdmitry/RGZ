const API_BASE =
  (location.hostname === "localhost" || location.hostname === "127.0.0.1")
    ? "http://localhost:5000/api"
    : "/api";


function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function getUser() {
  try { return JSON.parse(localStorage.getItem("user")); }
  catch { return null; }
}

function setUser(user) {
  localStorage.setItem("user", JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function showMessage(el, text, type) {
  if (!el) return;
  el.style.display = "block";
  el.className = `message ${type}`;
  el.textContent = text;
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const mergedHeaders = {
    "Content-Type": "application/json",
    ...headers,
    ...authHeaders()
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers: mergedHeaders });
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    // токен невалидный/протух
    clearAuth();
  }
  return { res, data };
}

function logout() {
  clearAuth();
  window.location.href = "index.html";
}

// === Login/Register обработчики (работают только на соответствующих страницах) ===
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = document.getElementById("message");

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      const { res, data } = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        showMessage(msg, data.error || "Ошибка входа", "error");
        return;
      }

      setToken(data.token);
      setUser(data.user);
      window.location.href = "index.html";
    });
  }

  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = document.getElementById("message");

      const payload = {
        username: document.getElementById("username").value.trim(),
        password: document.getElementById("password").value,
        email: document.getElementById("email").value.trim(),
        first_name: document.getElementById("first_name").value.trim(),
        last_name: document.getElementById("last_name").value.trim(),
        group: document.getElementById("group").value.trim()
      };

      const { res, data } = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        showMessage(msg, data.error || "Ошибка регистрации", "error");
        return;
      }

      setToken(data.token);
      setUser(data.user);
      window.location.href = "index.html";
    });
  }
});
