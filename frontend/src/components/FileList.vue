<template>
  <div class="file-list">
    <div
      v-for="file in files"
      :key="file.filename"
      class="file-item"
      :class="{ active: activeFile === file.filename }"
      @click="$emit('select', file.filename)"
    >
      <span class="status-badge" :class="`status-${file.status}`">
        {{ statusLabel(file.status) }}
      </span>

      <div class="file-info">
        <span class="file-name">{{ file.filename }}</span>
        <span class="file-meta">
          +{{ file.additions }} / -{{ file.deletions }}
          <span v-if="getFileRisks(file.filename).length" class="risk-count">
            {{ getFileRisks(file.filename).length }} issue{{ getFileRisks(file.filename).length > 1 ? 's' : '' }}
          </span>
        </span>
      </div>

      <div v-if="getFileRisks(file.filename).length" class="risk-dots">
        <span
          v-for="(risk, i) in getFileRisks(file.filename)"
          :key="i"
          class="risk-dot"
          :class="`sev-${risk.severity}`"
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
import { getFileRisks } from '../utils/annotations.js'
import { SEVERITY_CLASS } from '../utils/diffColors.js'

export default {
  name: 'FileList',
  props: {
    files: { type: Array, default: () => [] },
    reviewData: { type: Object, default: null },
    activeFile: { type: String, default: null }
  },
  emits: ['select'],
  methods: {
    statusLabel(s) {
      return { added: 'ADD', modified: 'MOD', removed: 'DEL', renamed: 'RNM' }[s] || s?.toUpperCase()
    },
    getFileRisks(filename) {
      return getFileRisks(this.reviewData, filename)
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
.file-item.active { background: #1f6feb22; border-left: 3px solid #58a6ff; padding-left: 13px; }

.status-badge {
  font-size: 0.62rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;
  flex-shrink: 0; min-width: 34px; text-align: center;
}
.status-added { background: #3fb95022; color: #3fb950; }
.status-modified { background: #d2992222; color: #d29922; }
.status-removed { background: #f8514922; color: #f85149; }
.status-renamed { background: #58a6ff22; color: #58a6ff; }

.file-info { flex: 1; min-width: 0; }
.file-name {
  display: block; font-size: 0.82rem; color: #c9d1d9;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.file-meta { font-size: 0.7rem; color: #8b949e; }
.risk-count { color: #d29922; margin-left: 6px; }

.risk-dots { display: flex; gap: 3px; flex-shrink: 0; }
.risk-dot {
  width: 7px; height: 7px; border-radius: 50%;
}
.sev-critical { background: #f85149; }
.sev-high { background: #f0883e; }
.sev-medium { background: #d29922; }
.sev-low { background: #58a6ff; }

.empty-state { padding: 40px 16px; text-align: center; color: #8b949e; font-size: 0.85rem; }
</style>
