<template>
  <span class="diff-line-wrapper">
    <span
      class="diff-line"
      :class="lineClass"
    >
      <span class="ln ln-old">{{ line.old_line ?? '' }}</span>
      <span class="ln ln-new">{{ line.new_line ?? '' }}</span>
      <span class="prefix">{{ prefix }}</span>
      <span class="code" v-html="highlighted"></span>
    </span>

    <!-- Inline risk pill: shown below the code line -->
    <div
      v-for="(risk, i) in (badgeItems?.risks || [])"
      :key="i"
      class="risk-pill"
      :class="`pill-${risk.severity}`"
    >
      <span class="pill-badge" :class="`pill-${risk.severity}`">
        {{ risk.severity.toUpperCase() }}
      </span>
      <span class="pill-cat">{{ risk.category }}</span>
      <span class="pill-desc">{{ risk.description }}</span>
      <code v-if="risk.code_snippet" class="pill-code">{{ risk.code_snippet.slice(0, 120) }}</code>
    </div>
  </span>
</template>

<script>
import { computed } from 'vue'
import Prism from 'prismjs'

export default {
  name: 'DiffLine',
  props: {
    line: { type: Object, required: true },
    language: { type: String, default: 'plaintext' },
    badgeItems: { type: Object, default: null }
  },
  setup(props) {
    const lineClass = computed(() => `diff-${props.line.type}`)
    const prefix = computed(() => {
      return { addition: '+', deletion: '-', context: ' ' }[props.line.type] || ' '
    })

    const highlighted = computed(() => {
      const code = props.line.content || ''
      const grammar = Prism.languages[props.language]
      if (grammar && code) {
        try { return Prism.highlight(code, grammar, props.language) }
        catch { /* fallback */ }
      }
      return escapeHtml(code)
    })

    return { lineClass, prefix, highlighted }
  }
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
</script>

<style scoped>
.diff-line-wrapper { display: block; }

.diff-line {
  display: flex; align-items: baseline; min-height: 20px; line-height: 20px;
  font-family: 'Fira Code', 'Consolas', 'Cascadia Code', monospace;
  font-size: 0.8rem; white-space: pre;
}
.diff-line.diff-addition { background: rgba(63,185,80,0.12); }
.diff-line.diff-deletion { background: rgba(248,81,73,0.12); }
.diff-line.diff-context { background: transparent; }

.ln {
  display: inline-block; width: 42px; text-align: right;
  padding: 0 8px 0 4px; color: #484f58; flex-shrink: 0;
  user-select: none; font-size: 0.72rem;
}
.ln-new { border-left: 1px solid #30363d44; }

.prefix {
  display: inline-block; width: 16px; text-align: center;
  flex-shrink: 0; user-select: none;
}
.diff-addition .prefix { color: #3fb950; }
.diff-deletion .prefix { color: #f85149; }
.diff-context .prefix { color: #484f58; }

.code { flex: 1; min-width: 0; overflow: hidden; }

/* ===== Inline Risk Pill ===== */
.risk-pill {
  margin: 2px 0 2px 100px;
  padding: 4px 10px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 0.76rem;
  border-radius: 0;
  border-left: 3px solid;
}
.pill-critical { border-color: #f85149; background: rgba(248,81,73,0.08); }
.pill-high { border-color: #f0883e; background: rgba(240,136,62,0.08); }
.pill-medium { border-color: #d29922; background: rgba(210,153,34,0.08); }
.pill-low { border-color: #58a6ff; background: rgba(88,166,255,0.08); }

.pill-badge {
  font-size: 0.6rem; font-weight: 700; padding: 1px 6px; border-radius: 3px;
  color: #fff; flex-shrink: 0;
}
.pill-badge.pill-critical { background: #f85149; }
.pill-badge.pill-high { background: #f0883e; }
.pill-badge.pill-medium { background: #d29922; }
.pill-badge.pill-low { background: #58a6ff; }

.pill-cat {
  font-size: 0.7rem; color: #8b949e; flex-shrink: 0;
  background: #21262d; padding: 1px 6px; border-radius: 3px;
}
.pill-desc { color: #c9d1d9; line-height: 1.4; flex: 1; min-width: 200px; }

.pill-code {
  display: block; width: 100%; margin-top: 2px;
  padding: 4px 8px; background: #0d1117; border-radius: 4px;
  font-size: 0.72rem; color: #c9d1d9; font-family: 'Consolas', monospace;
  overflow-x: auto; white-space: pre;
}
</style>
