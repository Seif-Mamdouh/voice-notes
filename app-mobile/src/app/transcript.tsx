import { useLocalSearchParams } from 'expo-router';
import { FlatList, StyleSheet, Text, View } from 'react-native';

import type { Transcription } from '@/lib/api/client';
import { useTranscription, useTranscriptions } from '@/stores/transcriptions';

export default function TranscriptScreen() {
  const params = useLocalSearchParams<{ id?: string }>();
  const currentId = params.id ? Number(params.id) : null;
  const { data: current, error: currentError } = useTranscription(currentId);
  const { data: history, error: historyError } = useTranscriptions();

  const rest = history.filter((row) => row.id !== currentId);

  return (
    <FlatList
      contentContainerStyle={styles.container}
      data={rest}
      keyExtractor={(row) => String(row.id)}
      ListHeaderComponent={
        <View style={styles.header}>
          {currentId !== null && (
            <View style={styles.card}>
              {current ? (
                <>
                  <Text style={styles.transcript}>{current.transcript || '(no speech detected)'}</Text>
                  <Text style={styles.meta}>{metaLine(current)}</Text>
                </>
              ) : currentError ? (
                <Text style={styles.error}>{currentError}</Text>
              ) : (
                <Text style={styles.meta}>Loading…</Text>
              )}
            </View>
          )}
          {rest.length > 0 && <Text style={styles.sectionTitle}>Earlier</Text>}
          {historyError && <Text style={styles.error}>{historyError}</Text>}
        </View>
      }
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.transcript}>{item.transcript || '(no speech detected)'}</Text>
          <Text style={styles.meta}>{metaLine(item)}</Text>
        </View>
      )}
    />
  );
}

function metaLine(row: Transcription): string {
  const when = new Date(row.created_at).toLocaleString();
  return row.duration_seconds ? `${when} · ${row.duration_seconds.toFixed(1)}s` : when;
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  header: { gap: 12 },
  card: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(128, 128, 128, 0.1)',
    gap: 8,
    marginBottom: 12,
  },
  transcript: { fontSize: 17, lineHeight: 24 },
  meta: { fontSize: 13, opacity: 0.5 },
  sectionTitle: { fontSize: 13, fontWeight: '600', opacity: 0.5, textTransform: 'uppercase' },
  error: { color: '#E5484D' },
});
