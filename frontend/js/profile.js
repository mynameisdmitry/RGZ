function renderUserInfo(user) {
  const el = document.getElementById("user-info");
  if (!el) return;

  el.innerHTML = `
    <p><b>Username:</b> ${user.username}</p>
    <p><b>Email:</b> ${user.email}</p>
    <p><b>Имя:</b> ${user.first_name}</p>
    <p><b>Фамилия:</b> ${user.last_name}</p>
    <p><b>Группа:</b> ${user.group}</p>
    <p><b>Роль:</b> ${user.is_admin ? "Администратор" : "Пользователь"}</p>
  `;
}

function renderReservations(list) {
  const el = document.getElementById("reservations-list");
  if (!el) return;

  if (!list || list.length === 0) {
    el.innerHTML = `<p class="text-muted">Нет активных бронирований.</p>`;
    return;
  }

  el.innerHTML = "";
  for (const l of list) {
    const item = document.createElement("div");
    item.className = "reservation-item";

    const left = document.createElement("div");
    left.innerHTML = `<div class="locker-info">Ячейка #${l.locker_number}</div>
                      <div class="text-muted">Истекает: ${l.expires_at ? new Date(l.expires_at).toLocaleString() : "—"}</div>`;

    const btn = document.createElement("button");
    btn.className = "btn btn-danger btn-sm";
    btn.textContent = "Снять бронь";
    btn.onclick = async () => {
      const { res, data } = await apiFetch(`/lockers/${l.id}/cancel`, { method: "POST" });
      if (!res.ok) {
        alert(data.error || "Ошибка");
        return;
      }
      window.location.reload();
    };

    item.appendChild(left);
    item.appendChild(btn);
    el.appendChild(item);
  }
}

function showUpdateForm() {
  const modal = document.getElementById("update-form");
  if (modal) modal.style.display = "flex";

  const user = (() => { try { return JSON.parse(localStorage.getItem("user")); } catch { return null; } })();
  if (user) {
    document.getElementById("update-email").value = user.email || "";
    document.getElementById("update-first_name").value = user.first_name || "";
    document.getElementById("update-last_name").value = user.last_name || "";
    document.getElementById("update-group").value = user.group || "";
  }
}

function closeUpdateForm() {
  const modal = document.getElementById("update-form");
  if (modal) modal.style.display = "none";
}

async function deleteAccount() {
  if (!confirm("Удалить аккаунт? Все ваши брони будут сняты.")) return;

  const { res, data } = await apiFetch("/users/me", { method: "DELETE" });
  if (!res.ok) {
    alert(data.error || "Ошибка удаления");
    return;
  }

  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "index.html";
}

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // Получаем актуальные данные профиля
  const { res, data } = await apiFetch("/users/me", { method: "GET" });
  if (!res.ok) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
    return;
  }

  localStorage.setItem("user", JSON.stringify(data.user));
  renderUserInfo(data.user);

  // Загружаем брони
  const { res: r2, data: d2 } = await apiFetch("/lockers/my-reservations", { method: "GET" });
  if (r2.ok) renderReservations(d2.reservations);

  // submit формы редактирования
  const form = document.getElementById("update-profile-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        email: document.getElementById("update-email").value.trim(),
        first_name: document.getElementById("update-first_name").value.trim(),
        last_name: document.getElementById("update-last_name").value.trim(),
        group: document.getElementById("update-group").value.trim()
      };

      const { res: r3, data: d3 } = await apiFetch("/users/profile", {
        method: "PUT",
        body: JSON.stringify(payload)
      });

      if (!r3.ok) {
        alert(d3.error || "Ошибка обновления");
        return;
      }

      localStorage.setItem("user", JSON.stringify(d3.user));
      window.location.reload();
    });
  }

  // закрытие модалки по клику вне
  const modal = document.getElementById("update-form");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeUpdateForm();
    });
  }
});