import type { components } from "./generated";
import { apiRequest } from "./request";

/**
 * Typed API client. Response types come from `generated.ts`, which is
 * auto-generated from the backend's OpenAPI spec (`npm run generate:api`) —
 * CI fails if it drifts. Only `stores/` may import this.
 */
export type Transcription = components["schemas"]["TranscriptionResponse"];
export type TranscriptionList = components["schemas"]["TranscriptionListResponse"];

export const api = {
  transcriptions: {
    /** Upload a recorded audio file for transcription. */
    async create(fileUri: string, mimetype = "audio/m4a"): Promise<Transcription> {
      const form = new FormData();
      // React Native's FormData accepts {uri, name, type} for file parts.
      form.append("file", {
        uri: fileUri,
        name: "recording.m4a",
        type: mimetype,
      } as unknown as Blob);
      return apiRequest<Transcription>("/transcriptions", { method: "POST", body: form });
    },

    async list(): Promise<TranscriptionList> {
      return apiRequest<TranscriptionList>("/transcriptions");
    },

    async get(id: number): Promise<Transcription> {
      return apiRequest<Transcription>(`/transcriptions/${id}`);
    },
  },
};
