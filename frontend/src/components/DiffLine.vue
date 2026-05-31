<template>
  <span
    class="diff-line"
    :class="lineClass"
  >
    <!-- Old line number -->
    <span class="ln ln-old">{{ line.old_line ?? '' }}</span>
    <!-- New line number -->
    <span class="ln ln-new">{{ line.new_line ?? '' }}</span>
    <!-- Prefix (+/-/ ) -->
    <span class="prefix">{{ prefix }}</span>
    <!-- Highlighted code -->
    <span
      class="code"
      v-html="highlighted"
    ></span>
    <!-- Risk badge -->
    <RiskBadge
      v-if="badgeItems && badgeItems.risks?.length"
      :items="badgeItems.risks"
    />
  </span>
</template>

<script>
import { computed } from 'vue'
import Prism from 'prismjs'
import RiskBadge from './RiskBadge.vue'

export default {
  name: 'DiffLine',
  components: { RiskBadge },
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
        try {
          return Prism.highlight(code, grammar, props.language)
        } catch { /* fallback */ }
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
.ln-old { color: #484f58; }
.ln-new { color: #484f58; border-left: 1px solid #30363d44; }

.prefix {
  display: inline-block; width: 16px; text-align: center;
  flex-shrink: 0; user-select: none;
}
.diff-addition .prefix { color: #3fb950; }
.diff-deletion .prefix { color: #f85149; }
.diff-context .prefix { color: #484f58; }

.code { flex: 1; min-width: 0; overflow: hidden; }
</style>
