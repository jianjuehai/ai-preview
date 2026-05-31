<template>
  <div class="file-detail">
    <div v-if="selectedFile" class="file-header">
      <span class="status-badge" :class="`status-${selectedFile.status}`">
        {{ statusLabel(selectedFile.status) }}
      </span>
      <span class="file-name">{{ selectedFile.filename }}</span>
      <span class="file-meta">+{{ selectedFile.additions }} / -{{ selectedFile.deletions }}</span>
    </div>

    <!-- Placeholder: diff viewer coming in PR 9 -->
    <div class="diff-area">
      <p class="placeholder">Select a file from the left panel to view its diff.</p>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'FileDetail',
  props: {
    diffData: { type: Object, default: null },
    reviewData: { type: Object, default: null },
    activeFile: { type: String, default: null }
  },
  setup(props) {
    const selectedFile = computed(() => {
      if (!props.diffData?.structured_diff?.files || !props.activeFile) return null
      return props.diffData.structured_diff.files.find(
        f => f.filename === props.activeFile
      ) || null
    })

    function statusLabel(s) {
      return { added: 'ADD', modified: 'MOD', removed: 'DEL', renamed: 'RNM' }[s] || s?.toUpperCase()
    }

    return { selectedFile, statusLabel }
  }
}
</script>

<style scoped>
.file-detail { padding: 0; height: 100%; display: flex; flex-direction: column; }
.file-header {
  display: flex; align-items: center; gap: 12px; padding: 14px 20px;
  background: var(--bg-secondary); border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.file-name { font-size: 0.95rem; font-weight: 500; }
.file-meta { font-size: 0.8rem; color: var(--text-secondary); margin-left: auto; }

.status-badge {
  font-size: 0.65rem; font-weight: 600; padding: 2px 6px; border-radius: 4px;
}
.status-added { background: #3fb95022; color: var(--green); }
.status-modified { background: #d2992222; color: var(--yellow); }
.status-removed { background: #f8514922; color: var(--red); }
.status-renamed { background: #58a6ff22; color: var(--blue); }

.diff-area {
  flex: 1; display: flex; align-items: center; justify-content: center;
  color: var(--text-secondary); font-size: 0.9rem;
}
.placeholder { opacity: 0.6; }
</style>
