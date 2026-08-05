/** Auth token helpers — access + refresh. */

const ACCESS_KEY = "cs_access_token";
const REFRESH_KEY = "cs_refresh_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(ACCESS_KEY, token);
}

export function setTokens(access: string, refresh?: string | null) {
  localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearToken() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}
