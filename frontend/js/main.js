document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const user = (() => { try { return JSON.parse(localStorage.getItem("user")); } catch { return null; } })();

  const loginBtn = document.getElementById("login-btn");
  const registerBtn = document.getElementById("register-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const profileLink = document.getElementById("profile-link");
  const greeting = document.getElementById("user-greeting");
  const mineFilter = document.getElementById("mine-filter");
  const myCard = document.getElementById("my-reservations-card");

  if (token && user) {
    if (loginBtn) loginBtn.style.display = "none";
    if (registerBtn) registerBtn.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "inline-block";
    if (profileLink) profileLink.style.display = "inline-block";
    if (mineFilter) mineFilter.style.display = "inline-block";
    if (myCard) myCard.style.display = "block";
    if (greeting) greeting.textContent = `Здравствуйте, ${user.username}`;
  } else {
    if (logoutBtn) logoutBtn.style.display = "none";
    if (profileLink) profileLink.style.display = "none";
    if (mineFilter) mineFilter.style.display = "none";
    if (myCard) myCard.style.display = "none";
    if (greeting) greeting.textContent = "";
  }
});