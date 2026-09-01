import { useCallback, useEffect, useState } from 'react';

import { api, type Transcription } from '@/lib/api/client';

/**
 * The only consumers of lib/api — screens go through these hooks,
 * mirroring the stores/networking seam from the take-home.
 */

export function useCreateTranscription() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(async (fileUri: string): Promise<Transcription | null> => {
    setIsUploading(true);
    setError(null);
    try {
      return await api.transcriptions.create(fileUri);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed');
      return null;
    } finally {
      setIsUploading(false);
    }
  }, []);

  return { create, isUploading, error };
}

export function useTranscription(id: number | null) {
  const [data, setData] = useState<Transcription | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id === null) return;
    let cancelled = false;
    api.transcriptions
      .get(id)
      .then((row) => !cancelled && setData(row))
      .catch((e) => !cancelled && setError(e instanceof Error ? e.message : 'Failed to load'));
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { data, error };
}

export function useTranscriptions() {
  const [data, setData] = useState<Transcription[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const result = await api.transcriptions.list();
      setData(result.transcriptions);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load');
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, error, refresh };
}
