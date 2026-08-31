import {
  requestRecordingPermissionsAsync,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorder,
  useAudioRecorderState,
} from 'expo-audio';
import { useCallback } from 'react';

/**
 * Wraps expo-audio's recorder: permission request, audio-mode setup,
 * start/stop, elapsed time. Returns the recorded file's URI on stop.
 */
export function useRecorder() {
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const state = useAudioRecorderState(recorder);

  const start = useCallback(async () => {
    const { granted } = await requestRecordingPermissionsAsync();
    if (!granted) throw new Error('Microphone permission denied');
    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync();
    recorder.record();
  }, [recorder]);

  const stop = useCallback(async (): Promise<string> => {
    await recorder.stop();
    await setAudioModeAsync({ allowsRecording: false });
    if (!recorder.uri) throw new Error('Recording produced no file');
    return recorder.uri;
  }, [recorder]);

  return {
    start,
    stop,
    isRecording: state.isRecording,
    durationSeconds: Math.floor(state.durationMillis / 1000),
  };
}
