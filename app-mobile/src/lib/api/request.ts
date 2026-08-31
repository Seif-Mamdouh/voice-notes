import Constants from "expo-constants";

/**
 * The only transport file: base-URL resolution, error unwrapping.
 * Everything else goes through `client.ts`.
 *
 * Base URL priority:
 *  1. EXPO_PUBLIC_API_URL (explicit override, e.g. a deployed backend)
 *  2. The Expo dev server's host with the API port — works for both the
 *     iOS simulator and a phone on the same LAN without any config.
 */
const API_PORT = 8000;

export function apiBaseUrl(): string {
  const explicit = process.env.EXPO_PUBLIC_API_URL;
  if (explicit) return explicit.replace(/\/$/, "");

  const hostUri = Constants.expoConfig?.hostUri; // e.g. "192.168.1.42:8081"
  const host = hostUri?.split(":")[0] ?? "localhost";
  return `http://${host}:${API_PORT}`;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, init);
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // non-JSON error body; keep statusText
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}
