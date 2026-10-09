export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "gift_mvp_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const { method = "GET", body = null, headers = {}, isFormData = false } = options;

  const finalHeaders = { ...headers };
  const token = getToken();

  if (token) {
    // finalHeaders.Authorization = Bearer ${token};
    finalHeaders.Authorization = `Bearer ${token}`;
  }

  if (body && !isFormData) {
    finalHeaders["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined
  });

  const rawText = await response.text();
  let data = null;

  try {
    data = rawText ? JSON.parse(rawText) : null;
  } catch {
    data = rawText;
  }

  if (!response.ok) {
    const message =
      (data && data.detail) ||
      (typeof data === "string" && data) ||
      "Произошла ошибка";
    throw new Error(message);
  }

  return data;
}

export const api = {
  register(payload) {
    return request("/auth/register", {
      method: "POST",
      body: payload
    });
  },

  login(payload) {
    return request("/auth/login", {
      method: "POST",
      body: payload
    });
  },

  me() {
    return request("/auth/me");
  },

  listRecipients() {
    return request("/recipients");
  },

  getRecipient(id) {
    return request(`/recipients/${id}`);
  },

  createRecipient(payload) {
    return request("/recipients", {
      method: "POST",
      body: payload
    });
  },

  updateRecipient(id, payload) {
    return request(`/recipients/${id}`, {
      method: "PATCH",
      body: payload
    });
  },

  deleteRecipient(id) {
    return request(`/recipients/${id}`, {
      method: "DELETE"
    });
  },

  listProducts(params = {}) {
    const query = new URLSearchParams();

    if (params.min_price !== undefined && params.min_price !== "") {
      query.append("min_price", params.min_price);
    }

    if (params.max_price !== undefined && params.max_price !== "") {
      query.append("max_price", params.max_price);
    }

    if (params.category) {
      query.append("category", params.category);
    }

    const qs = query.toString();
    return request(`/products${qs ? `?${qs}` : ""}`);
    // return request(`/products${qs ? ?${qs} : ""}`);
  },

  uploadProductsCsv(file) {
    const formData = new FormData();
    formData.append("file", file);

    return request("/products/import-csv", {
      method: "POST",
      body: formData,
      isFormData: true
    });
  },

  generateRecommendations(payload) {
    return request("/recommendations/generate", {
      method: "POST",
      body: payload
    });
  },

  importVkPublicProfile(payload) {
    return request("/vk/import-public-profile", {
      method: "POST",
      body: payload
    });
  },

  importVkToken(payload) {
    return request("/vk/import-token", {
      method: "POST",
      body: payload
    });
  },

  getVkAuthUrl(recipientId) {
    return request(`/vk/auth-url?recipient_id=${recipientId}`);
  },

  exchangeVkCode(payload) {
    return request("/vk/exchange-code", {
      method: "POST",
      body: payload
    });
  }
};

