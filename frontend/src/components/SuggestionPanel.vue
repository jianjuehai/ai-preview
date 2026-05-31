<template>
  <div class="suggestion-panel" v-if="items.length">
    <div class="panel-header">
      Suggested Fixes ({{ items.length }})
    </div>
    <div v-for="(sug, i) in items" :key="i" class="sug-item">
      <div class="sug-header">
        <span class="sug-file">{{ sug.file }}:{{ sug.line_range }}</span>
      </div>
      <p class="sug-desc">{{ sug.description }}</p>
      <div v-if="sug.code_before" class="code-block before">
        <div class="code-label">Before</div>
        <pre><code>{{ sug.code_before }}</code></pre>
      </div>
      <div v-if="sug.code_after" class="code-block after">
        <div class="code-label">After</div>
        <pre><code>{{ sug.code_after }}</code></pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SuggestionPanel',
  props: {
    items: { type: Array, default: () => [] }
  }
}
</script>

<style scoped>
.suggestion-panel {
  background: #161b22; border: 1px solid #30363d; border-radius: 8px;
  margin: 16px 0; overflow: hidden;
}
.panel-header {
  padding: 10px 16px; font-size: 0.8rem; font-weight: 600; color: #58a6ff;
  border-bottom: 1px solid #30363d;
}
.sug-item { padding: 14px 16px; border-bottom: 1px solid #30363d44; }
.sug-item:last-child { border-bottom: none; }
.sug-header { margin-bottom: 6px; }
.sug-file { font-size: 0.82rem; color: #58a6ff; font-family: monospace; }
.sug-desc { font-size: 0.85rem; color: #c9d1d9; line-height: 1.5; margin: 0 0 10px; }
.code-block { margin-top: 8px; }
.code-label {
  font-size: 0.7rem; color: #8b949e; margin-bottom: 4px;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.code-block pre {
  padding: 10px; border-radius: 6px; font-size: 0.78rem; overflow-x: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
}
.code-block.before pre { background: #f8514922; color: #f85149; }
.code-block.after pre { background: #3fb95022; color: #3fb950; }
</style>
