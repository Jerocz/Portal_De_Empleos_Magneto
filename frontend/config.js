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

  let res;
  try {
    res = await fetch(API + path, { ...options, headers });
  } catch (networkErr) {
    throw new Error("No se pudo conectar con el servidor. Verifica que esté corriendo.");
  }

  if (res.status === 401) {
    logout();
    return;
  }

  // Intentar parsear como JSON; si falla, construir un error legible
  let data;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    data = await res.json();
  } else {
    // El servidor devolvió texto plano o HTML (ej: error 500 sin handler)
    const text = await res.text();
    throw new Error(
      res.ok
        ? text
        : `Error del servidor (${res.status}). Revisa la consola del backend.`
    );
  }

  if (!res.ok) throw new Error(data.detail || "Error en la solicitud");
  return data;
}
