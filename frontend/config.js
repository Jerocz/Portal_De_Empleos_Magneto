const API = "";

function getToken() {
  return localStorage.getItem("token");
}

function getUser() {
  const u = localStorage.getItem("user");
  return u ? JSON.parse(u) : null;
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "index.html";
}

function requireAuth() {
  if (!getToken()) window.location.href = "index.html";
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401) {
    logout();
    return;
  }
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Error en la solicitud");
  return data;
}
