<template>
  <div class="file-list">
    <div
      v-for="file in files"
      :key="file.filename"
      class="file-item"
      :class="{ active: activeFile === file.filename }"
      @click="$emit('select', file.filename)"
    >
      <!-- Status badge -->
      <span class="status-badge" :class="`status-${file.status}`">
        {{ statusLabel(file.status) }}
      </span>

      <!-- Filename -->
      <div class="file-info">
        <span class="file-name">{{ file.filename }}</span>
        <span class="file-meta">
          +{{ file.additions }} / -{{ file.deletions }}
        </span>
      </div>

      <!-- Risk indicators -->
      <div v-if="getFileRisks(file.filename).length" class="risk-dots">
        <span
          v-for="risk in getFileRisks(file.filename)"
          :key="risk.description"
          class="risk-dot"
          :class="`severity-${risk.severity}`"
          :title="risk.description"
        ></span>
      </div>
    </div>

    <div v-if="files.length === 0" class="empty-state">
      No changed files found.
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileList',
  props: {
    files: { type: Array, default: () => [] },
    reviewData: { type: Object, default: null },
    activeFile: { type: String, default: null }
  },
  emits: ['select'],
  methods: {
    statusLabel(status) {
      const map = { added: 'ADD', modified: 'MOD', removed: 'DEL', renamed: 'RNM' }
      return map[status] || status.toUpperCase()
    },
    getFileRisks(filename) {
      if (!this.reviewData?.risk_items) return []
      return this.reviewData.risk_items.filter(r => r.file === filename)
    }
  }
}
</script>

<style scoped>
.file-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; cursor: pointer; border-bottom: 1px solid #30363d44;
  transition: background 0.15s;
}
.file-item:hover { background: #21262d; }
.file-item.active { background: #1f6feb22; border-left: 3px solid var(--accent); padding-left: 13px; }

.status-badge {
  font-size: 0.65rem; font-weight: 600; padding: 2px 6px; border-radius: 4px;
  text-transform: uppercase; flex-shrink: 0; min-width: 36px; text-align: center;
}
.status-added { background: #3fb95022; color: var(--green); }
.status-modified { background: #d2992222; color: var(--yellow); }
.status-removed { background: #f8514922; color: var(--red); }
.status-renamed { background: #58a6ff22; color: var(--blue); }

.file-info { flex: 1; min-width: 0; }
.file-name {
  display: block; font-size: 0.85rem; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.file-meta { font-size: 0.72rem; color: var(--text-secondary); }

.risk-dots { display: flex; gap: 4px; flex-shrink: 0; }
.risk-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.severity-critical { background: var(--red); }
.severity-high { background: var(--orange); }
.severity-medium { background: var(--yellow); }
.severity-low { background: var(--blue); }

.empty-state { padding: 40px 16px; text-align: center; color: var(--text-secondary); font-size: 0.85rem; }
</style>
