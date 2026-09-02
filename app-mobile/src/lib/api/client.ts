import { File } from "expo-file-system";

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
    async create(fileUri: string): Promise<Transcription> {
      const form = new FormData();
      // Expo's WinterCG fetch requires real Blob/File parts (the legacy RN
      // {uri, name, type} object throws "Unsupported FormDataPart implementation").
      form.append("file", new File(fileUri), "recording.m4a");
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
