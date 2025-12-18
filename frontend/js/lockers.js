let currentFilter = "all";
let lockersCache = [];

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString();
}

function isMine(locker) {
  const user = (() => { try { return JSON.parse(localStorage.getItem("user")); } catch { return null; } })();
  return user && locker.user_info && locker.user_info.username === user.username;
}

function setStats(stats) {
  const total = document.getElementById("total-lockers");
  const free = document.getElementById("free-lockers");
  const occupied = document.getElementById("occupied-lockers");
  if (total) total.textContent = stats.total;
  if (free) free.textContent = stats.free;
  if (occupied) occupied.textContent = stats.occupied;
}

function renderGrid() {
  const grid = document.getElementById("lockers-grid");
  if (!grid) return;

  let list = lockersCache;

  if (currentFilter === "free") list = list.filter(l => l.status === "free");
  if (currentFilter === "occupied") list = list.filter(l => l.status === "occupied");
  if (currentFilter === "mine") list = list.filter(l => isMine(l));

  grid.innerHTML = "";

  for (const locker of list) {
    const cell = document.createElement("div");
    cell.className = "locker-cell " + (isMine(locker) ? "mine" : locker.status);
    cell.onclick = () => openLockerModal(locker);

    const num = document.createElement("div");
    num.className = "locker-number";
    num.textContent = locker.locker_number;

    const st = document.createElement("div");
    st.className = "locker-status";
    st.textContent = isMine(locker) ? "моя" : (locker.status === "free" ? "свободна" : "занята");

    cell.appendChild(num);
    cell.appendChild(st);
    grid.appendChild(cell);
  }
}

function setActiveFilterButton(filter) {
  const buttons = document.querySelectorAll(".btn-filter");
  buttons.forEach(b => b.classList.remove("active"));

  const map = {
    all: 0, free: 1, occupied: 2, mine: 3
  };
  const idx = map[filter];
  if (buttons[idx]) buttons[idx].classList.add("active");
}

function filterLockers(filter) {
  currentFilter = filter;
  setActiveFilterButton(filter);
  renderGrid();
}

// ===== MODAL =====
function openLockerModal(locker) {
  const modal = document.getElementById("locker-modal");
  const numEl = document.getElementById("modal-locker-number");
  const info = document.getElementById("modal-info");
  const actions = document.getElementById("modal-actions");

  if (!modal || !numEl || !info || !actions) return;

  numEl.textContent = locker.locker_number;

  const token = localStorage.getItem("token");

  let userBlock = "—";
  if (locker.user_info) {
    if (locker.user_info.username === "скрыто") {
      userBlock = "скрыто (нужна авторизация)";
    } else {
      userBlock = `${locker.user_info.username} (${locker.user_info.first_name} ${locker.user_info.last_name}, ${locker.user_info.group})`;
    }
  }

  info.innerHTML = `
    <p><b>Статус:</b> ${locker.status === "free" ? "свободна" : "занята"}</p>
    <p><b>Пользователь:</b> ${userBlock}</p>
    <p><b>Забронировано:</b> ${formatDate(locker.reserved_at)}</p>
    <p><b>Истекает:</b> ${formatDate(locker.expires_at)}</p>
  `;

  actions.innerHTML = "";

  if (!token) {
    actions.innerHTML = `<p class="text-muted">Войдите, чтобы бронировать и видеть детали.</p>`;
  } else {
    // авторизован: можно резервировать свободную или отменять свою
    if (locker.status === "free") {
      const btn = document.createElement("button");
      btn.className = "btn btn-primary";
      btn.textContent = "Забронировать";
      btn.onclick = () => reserveLocker(locker.id);
      actions.appendChild(btn);
    } else {
      if (isMine(locker)) {
        const btn = document.createElement("button");
        btn.className = "btn btn-danger";
        btn.textContent = "Отменить бронь";
        btn.onclick = () => cancelLocker(locker.id);
        actions.appendChild(btn);
      } else {
        actions.innerHTML = `<p class="text-muted">Эта ячейка занята другим пользователем.</p>`;
      }
    }
  }

  modal.style.display = "flex";
}

function closeModal() {
  const modal = document.getElementById("locker-modal");
  if (modal) modal.style.display = "none";
}

async function reserveLocker(lockerId) {
  const { res, data } = await apiFetch(`/lockers/${lockerId}/reserve`, { method: "POST" });
  if (!res.ok) {
    alert(data.error || "Ошибка бронирования");
    return;
  }
  // требование задания: запросы через перезагрузку страниц
  window.location.reload();
}

async function cancelLocker(lockerId) {
  const { res, data } = await apiFetch(`/lockers/${lockerId}/cancel`, { method: "POST" });
  if (!res.ok) {
    alert(data.error || "Ошибка отмены");
    return;
  }
  window.location.reload();
}

// ===== LOAD =====
document.addEventListener("DOMContentLoaded", async () => {
  const grid = document.getElementById("lockers-grid");
  if (!grid) return;

  // Неавторизованный делает запрос без токена => backend скроет детали
  const token = localStorage.getItem("token");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const res = await fetch(`${API_BASE}/lockers/`, { headers });
  const data = await res.json();

  lockersCache = data.lockers || [];
  setStats(data.statistics || { total: 0, free: 0, occupied: 0 });

  // мои брони (для карточки на главной)
  const myEl = document.getElementById("my-reservations");
  if (token && myEl) {
    const { res: r2, data: d2 } = await apiFetch("/lockers/my-reservations", { method: "GET" });
    if (r2.ok) {
      myEl.textContent = d2.count;
    } else {
      myEl.textContent = "0";
    }
  }

  renderGrid();

  // закрытие модалки по клику вне
  const modal = document.getElementById("locker-modal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
  }
});