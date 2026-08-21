const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export type DiseaseSchema = {
  disease: string;
  features: string[];
  feature_count: number;
};

export type PredictionResult = {
  disease: string;
  risk_score: number;
  risk_level: "low" | "moderate" | "elevated" | string;
  probability: number;
  model: string;
  model_features: number;
  disclaimer?: string;
  predicted_class?: string;
  predicted_class_probability?: number;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in_minutes?: number;
  user: {
    id: string | number;
    username: string;
    role: string;
  };
};

export class ApiError extends Error {
  status?: number;
  detail?: string;

  constructor(message: string, status?: number, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

export function clearAccessToken() {
  accessToken = null;
}

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        accessToken = null;
        return null;
      }

      const data = (await response.json()) as {
        access_token?: string;
      };

      if (!data.access_token) {
        accessToken = null;
        return null;
      }

      accessToken = data.access_token;
      return accessToken;
    } catch {
      accessToken = null;
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

async function rawRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<{ response: Response; body: unknown }> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);

  try {
    const headers = new Headers(options.headers || {});
    headers.set("Content-Type", "application/json");

    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      credentials: "include",
      headers,
      signal: controller.signal,
    });

    const raw = await response.text();

    let body: unknown = null;

    try {
      body = raw ? JSON.parse(raw) : null;
    } catch {
      body = raw;
    }

    return { response, body };
  } finally {
    window.clearTimeout(timeout);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  allowRefresh = true,
): Promise<T> {
  try {
    const { response, body } = await rawRequest<T>(path, options);

    if (response.status === 401 && allowRefresh && path !== "/auth/refresh") {
      const newToken = await refreshAccessToken();

      if (newToken) {
        return request<T>(path, options, false);
      }
    }

    if (!response.ok) {
      const detail =
        typeof body === "object" &&
        body !== null &&
        "detail" in body
          ? String(
              (body as { detail?: unknown }).detail ?? "",
            )
          : "";

      throw new ApiError(
        detail ||
          `Request failed with status ${response.status}`,
        response.status,
        detail,
      );
    }

    return body as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (
      error instanceof DOMException &&
      error.name === "AbortError"
    ) {
      throw new ApiError(
        "The MedPulse service took too long to respond.",
      );
    }

    throw new ApiError(
      "MedPulse couldn't connect to the screening service. Please check that the backend is running.",
    );
  }
}

export const api = {
  health: () =>
    request<{ status: string }>("/health"),

  getDiseaseSchema: (disease: string) =>
    request<DiseaseSchema>(
      `/predict/${disease}/schema`,
    ),

  predictDisease: (
    disease: string,
    payload: Record<string, unknown>,
  ) =>
    request<PredictionResult>(
      `/predict/${disease}`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),

  login: (username: string, password: string) =>
    request<LoginResponse>(
      "/auth/login",
      {
        method: "POST",
        body: JSON.stringify({
          username,
          password,
        }),
      },
    ),

  register: (username: string, password: string) =>
    request<{
      id: string | number;
      username: string;
      role: string;
    }>(
      "/auth/register",
      {
        method: "POST",
        body: JSON.stringify({
          username,
          password,
        }),
      },
    ),

  refresh: () =>
    refreshAccessToken(),

  logout: () =>
    request<{ status?: string }>(
      "/auth/logout",
      {
        method: "POST",
      },
    ),

  logoutAll: () =>
    request<{ status?: string }>(
      "/auth/logout-all",
      {
        method: "POST",
      },
    ),

  getProfile: () =>
    request<{
      completed: boolean;
      profile: Record<string, unknown> | null;
    }>("/profile/me"),

  saveProfile: (
    profile: Record<string, unknown>,
  ) =>
    request<{
      status: string;
      completed: boolean;
      profile: Record<string, unknown>;
    }>(
      "/profile/me",
      {
        method: "PUT",
        body: JSON.stringify(profile),
      },
    ),
};

export { API_URL };

