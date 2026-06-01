<template>
  <div class="suggestion-panel">
    <div class="panel-header" @click="toggle">
      <span class="panel-arrow">{{ collapsed ? '▸' : '▾' }}</span>
      Suggested Fixes ({{ items.length }})
    </div>

    <div v-if="!collapsed" class="panel-body">
      <div v-for="(sug, i) in items" :key="i" class="sug-row" @click="expandedIdx = expandedIdx === i ? -1 : i">
        <div class="sug-row-header">
          <span class="sug-row-arrow">{{ expandedIdx === i ? '▾' : '▸' }}</span>
          <span class="sug-row-file">{{ sug.file }}:{{ sug.line_range }}</span>
          <span class="sug-row-desc">{{ sug.description }}</span>
        </div>
        <template v-if="expandedIdx === i">
          <div v-if="sug.code_before" class="code-block before">
            <div class="code-label">Before</div>
            <pre><code>{{ sug.code_before }}</code></pre>
          </div>
          <div v-if="sug.code_after" class="code-block after">
            <div class="code-label">After</div>
            <pre><code>{{ sug.code_after }}</code></pre>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SuggestionPanel',
  props: {
    items: { type: Array, default: () => [] }
  },
  emits: ['collapse'],
  setup(props, { emit }) {
    const collapsed = ref(false)
    const expandedIdx = ref(-1)

    function toggle() {
      collapsed.value = !collapsed.value
      emit('collapse', collapsed.value)
    }

    watch(() => props.items, () => { expandedIdx.value = -1; collapsed.value = false })

    return { collapsed, expandedIdx, toggle }
  }
}
</script>

<style scoped>
.suggestion-panel {
  display: flex; flex-direction: column; height: 100%;
  background: #161b22;
}

.panel-header {
  padding: 8px 14px; font-size: 0.78rem; font-weight: 600; color: #58a6ff;
  cursor: pointer; user-select: none; flex-shrink: 0;
  display: flex; align-items: center; gap: 6px;
}
.panel-header:hover { background: #21262d; }
.panel-arrow { font-size: 0.7rem; width: 14px; text-align: center; }

.panel-body { flex: 1; overflow-y: auto; }

.sug-row {
  padding: 7px 14px; cursor: pointer;
  border-bottom: 1px solid #30363d33; transition: background 0.1s;
}
.sug-row:hover { background: #21262d; }

.sug-row-header {
  display: flex; align-items: baseline; gap: 8px; font-size: 0.78rem; overflow: hidden;
}
.sug-row-arrow { font-size: 0.65rem; color: #8b949e; flex-shrink: 0; width: 12px; }
.sug-row-file { color: #58a6ff; font-family: monospace; white-space: nowrap; flex-shrink: 0; }
.sug-row-desc { color: #8b949e; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.code-block { margin-top: 4px; padding-left: 20px; }
.code-label { font-size: 0.65rem; color: #8b949e; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.04em; }
.code-block pre {
  padding: 8px; border-radius: 4px; font-size: 0.74rem; overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', monospace; margin: 0;
}
.code-block.before pre { background: #f8514922; color: #f85149; }
.code-block.after pre { background: #3fb95022; color: #3fb950; }
</style>
