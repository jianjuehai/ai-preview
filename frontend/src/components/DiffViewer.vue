<template>
  <div class="diff-viewer">
    <div v-if="!file" class="diff-empty">
      Select a file to view its diff.
    </div>

    <template v-else>
      <!-- File header -->
      <div class="file-header">
        <span class="status-badge" :class="`status-${file.status}`">
          {{ statusLabel(file.status) }}
        </span>
        <span class="file-name">{{ file.filename }}</span>
        <span class="file-meta">+{{ file.additions }} / -{{ file.deletions }}</span>
      </div>

      <!-- Per-hunk rendering -->
      <div class="hunks">
        <div v-for="(hunk, hi) in file.hunks" :key="hi" class="hunk">
          <div class="hunk-header">{{ hunk.header }}</div>
          <DiffLine
            v-for="(line, li) in hunk.lines"
            :key="li"
            :line="line"
            :language="language"
            :badgeItems="annotations.get(line.new_line) || null"
          />
        </div>
      </div>

      <!-- Suggestion panel -->
      <SuggestionPanel
        v-if="suggestions.length"
        :items="suggestions"
      />
    </template>
  </div>
</template>

<script>
import { computed } from 'vue'
import DiffLine from './DiffLine.vue'
import SuggestionPanel from './SuggestionPanel.vue'
import { buildAnnotations } from '../utils/annotations.js'
import { getLanguage } from '../utils/diffColors.js'

export default {
  name: 'DiffViewer',
  components: { DiffLine, SuggestionPanel },
  props: {
    file: { type: Object, default: null },
    diffData: { type: Object, default: null },
    reviewData: { type: Object, default: null }
  },
  setup(props) {
    const language = computed(() => getLanguage(props.file?.filename || ''))

    const annotations = computed(() => {
      if (!props.reviewData || !props.file) return new Map()
      return buildAnnotations(props.reviewData, props.file.filename)
    })

    const suggestions = computed(() => {
      if (!props.reviewData?.suggestions || !props.file) return []
      return props.reviewData.suggestions.filter(s => s.file === props.file.filename)
    })

    function statusLabel(s) {
      return { added: 'ADD', modified: 'MOD', removed: 'DEL', renamed: 'RNM' }[s] || s?.toUpperCase()
    }

    return { language, annotations, suggestions, statusLabel }
  }
}
</script>

<style scoped>
.diff-viewer { height: 100%; display: flex; flex-direction: column; }

.diff-empty {
  flex: 1; display: flex; align-items: center; justify-content: center;
  color: #8b949e; font-size: 0.9rem; opacity: 0.6;
}

/* File header */
.file-header {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; background: #161b22;
  border-bottom: 1px solid #30363d; flex-shrink: 0; position: sticky; top: 0; z-index: 1;
}
.file-name { font-size: 0.88rem; font-weight: 500; font-family: monospace; }
.file-meta { font-size: 0.78rem; color: #8b949e; margin-left: auto; }

.status-badge { font-size: 0.62rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.status-added { background: #3fb95022; color: #3fb950; }
.status-modified { background: #d2992222; color: #d29922; }
.status-removed { background: #f8514922; color: #f85149; }
.status-renamed { background: #58a6ff22; color: #58a6ff; }

/* Hunks */
.hunks { flex: 1; overflow-y: auto; padding-bottom: 32px; }

.hunk-header {
  padding: 6px 16px; font-size: 0.72rem; color: #58a6ff;
  background: #1a1f2e; border-top: 1px solid #30363d44;
  font-family: monospace; position: sticky; top: 38px; z-index: 1;
}
</style>
