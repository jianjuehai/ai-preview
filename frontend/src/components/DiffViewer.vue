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

      <!-- Two-pane split area -->
      <div class="split-area" ref="splitArea">

        <!-- Upper: code diff -->
        <div class="split-top" :style="suggestions.length ? (suggCollapsed ? { flex: 1 } : { height: splitPercent + '%' }) : { flex: 1 }">
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
        </div>

        <!-- Resize divider -->
        <div
          v-if="suggestions.length"
          class="resize-divider"
          @mousedown.prevent="startResize"
        >
          <div class="divider-bar"></div>
          <span class="divider-label">⋮</span>
          <div class="divider-bar"></div>
          <span class="divider-label">▼ Suggested Fixes ({{ suggestions.length }})</span>
        </div>

        <!-- Lower: suggestions (header always visible) -->
        <div
          v-if="suggestions.length"
          class="split-bottom"
          :style="{ height: suggCollapsed ? 'auto' : (100 - splitPercent) + '%' }"
        >
          <SuggestionPanel
            :items="suggestions"
            @collapse="onSuggCollapse"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
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
    const splitArea = ref(null)
    const splitPercent = ref(65)
    const suggCollapsed = ref(false)

    const annotations = computed(() => {
      if (!props.reviewData || !props.file) return new Map()
      return buildAnnotations(props.reviewData, props.file.filename)
    })

    const suggestions = computed(() => {
      if (!props.reviewData?.suggestions || !props.file) return []
      return props.reviewData.suggestions.filter(s => s.file === props.file.filename)
    })

    // Reset when file changes
    watch(() => props.file?.filename, () => {
      splitPercent.value = 65
      suggCollapsed.value = false
    })

    function onSuggCollapse(collapsed) {
      suggCollapsed.value = collapsed
      // When expanding, reset to 65/35 split
      if (!collapsed) splitPercent.value = 65
    }

    function startResize(e) {
      const area = splitArea.value
      if (!area) return
      const rect = area.getBoundingClientRect()
      const totalH = rect.height
      const startY = e.clientY
      const startPct = splitPercent.value

      function onMove(ev) {
        const dy = ev.clientY - startY
        const newPct = startPct + (dy / totalH) * 100
        splitPercent.value = Math.max(35, Math.min(90, newPct))
      }

      function onUp() {
        document.removeEventListener('mousemove', onMove)
        document.removeEventListener('mouseup', onUp)
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }

      document.body.style.cursor = 'ns-resize'
      document.body.style.userSelect = 'none'
      document.addEventListener('mousemove', onMove)
      document.addEventListener('mouseup', onUp)
    }

    function statusLabel(s) {
      return { added: 'ADD', modified: 'MOD', removed: 'DEL', renamed: 'RNM' }[s] || s?.toUpperCase()
    }

    return { language, annotations, suggestions, splitArea, splitPercent, suggCollapsed, onSuggCollapse, startResize, statusLabel }
  }
}
</script>

<style scoped>
.diff-viewer { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

.diff-empty {
  flex: 1; display: flex; align-items: center; justify-content: center;
  color: #8b949e; font-size: 0.9rem; opacity: 0.6;
}

/* File header */
.file-header {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; background: #161b22;
  border-bottom: 1px solid #30363d; flex-shrink: 0;
}
.file-name { font-size: 0.88rem; font-weight: 500; font-family: monospace; }
.file-meta { font-size: 0.78rem; color: #8b949e; margin-left: auto; }

.status-badge { font-size: 0.62rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.status-added { background: #3fb95022; color: #3fb950; }
.status-modified { background: #d2992222; color: #d29922; }
.status-removed { background: #f8514922; color: #f85149; }
.status-renamed { background: #58a6ff22; color: #58a6ff; }

/* ========== SPLIT AREA ========== */
.split-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.split-top { overflow-y: auto; flex-shrink: 0; }

.hunks { padding-bottom: 16px; }

.hunk-header {
  padding: 6px 16px; font-size: 0.72rem; color: #58a6ff;
  background: #1a1f2e; border-top: 1px solid #30363d44;
  font-family: monospace; position: sticky; top: 0; z-index: 1;
}

/* ========== RESIZE DIVIDER ========== */
.resize-divider {
  cursor: ns-resize; flex-shrink: 0;
  background: #1c2128; border-top: 1px solid #30363d; border-bottom: 1px solid #30363d;
  user-select: none; transition: background 0.15s;
  display: flex; align-items: center; padding: 4px 12px; gap: 6px;
}
.resize-divider:hover { background: #252b33; }

.divider-bar {
  flex: 1; height: 1px; background: #30363d;
}
.divider-label {
  font-size: 0.65rem; color: #8b949e; white-space: nowrap;
  letter-spacing: 0.04em; text-transform: uppercase;
}

/* ========== SPLIT BOTTOM (suggestions) ========== */
.split-bottom {
  flex-shrink: 0; overflow: hidden;
  display: flex; flex-direction: column;
}
</style>
