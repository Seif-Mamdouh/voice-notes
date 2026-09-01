import { useRouter } from 'expo-router';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';

import { useRecorder } from '@/lib/useRecorder';
import { useCreateTranscription } from '@/stores/transcriptions';

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function RecordScreen() {
  const router = useRouter();
  const recorder = useRecorder();
  const { create, isUploading, error } = useCreateTranscription();

  const onPress = async () => {
    if (recorder.isRecording) {
      const uri = await recorder.stop();
      const transcription = await create(uri);
      if (transcription) {
        router.push({ pathname: '/transcript', params: { id: String(transcription.id) } });
      }
    } else {
      await recorder.start();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.timer}>
        {recorder.isRecording ? formatDuration(recorder.durationSeconds) : ' '}
      </Text>

      <Pressable
        onPress={onPress}
        disabled={isUploading}
        style={({ pressed }) => [
          styles.micButton,
          recorder.isRecording && styles.micButtonRecording,
          pressed && styles.micButtonPressed,
        ]}
      >
        {isUploading ? (
          <ActivityIndicator color="#fff" size="large" />
        ) : (
          <Text style={styles.micIcon}>{recorder.isRecording ? '■' : '🎙️'}</Text>
        )}
      </Pressable>

      <Text style={styles.hint}>
        {isUploading
          ? 'Transcribing…'
          : recorder.isRecording
            ? 'Tap to stop'
            : 'Tap to record'}
      </Text>

      {error && <Text style={styles.error}>{error}</Text>}

      <Pressable onPress={() => router.push('/transcript')}>
        <Text style={styles.link}>View past transcriptions</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 24, padding: 24 },
  timer: { fontSize: 40, fontVariant: ['tabular-nums'], height: 48 },
  micButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#208AEF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  micButtonRecording: { backgroundColor: '#E5484D' },
  micButtonPressed: { opacity: 0.8 },
  micIcon: { fontSize: 44, color: '#fff' },
  hint: { fontSize: 16, opacity: 0.6 },
  error: { color: '#E5484D', textAlign: 'center' },
  link: { color: '#208AEF', fontSize: 15, marginTop: 16 },
});
