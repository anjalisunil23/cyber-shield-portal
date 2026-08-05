import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { clearToken, getRefreshToken, getToken, setTokens } from "@/lib/auth";

const baseURL =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ||
  (import.meta.env.DEV ? "" : "http://127.0.0.1:8001");

export const apiClient = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${baseURL}/api/auth/refresh`, { refresh_token: refresh });
    setTokens(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    clearToken();
    return null;
  }
}

apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshing ??= refreshAccessToken().finally(() => {
        refreshing = null;
      });
      const token = await refreshing;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return apiClient(original);
      }
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export function apiMessage(error: unknown, fallback = "Request failed"): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { message?: string } | undefined;
    return data?.message || error.message || fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
