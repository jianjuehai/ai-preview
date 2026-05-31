<template>
  <span class="risk-badge-wrapper">
    <span
      class="risk-dot"
      :class="`sev-${topSeverity}`"
      @click.stop="expanded = !expanded"
      :title="`${topSeverity}: ${items[0]?.description?.slice(0, 80)}`"
    ></span>

    <!-- Expanded tooltip -->
    <Teleport to="body">
      <div v-if="expanded" class="risk-tooltip-backdrop" @click="expanded = false"></div>
      <div v-if="expanded" class="risk-tooltip" :class="`sev-${topSeverity}`">
        <div
          v-for="(item, i) in items"
          :key="i"
          class="tooltip-item"
        >
          <div class="tooltip-header">
            <span class="tooltip-sev" :class="`sev-${item.severity}`">
              {{ item.severity.toUpperCase() }}
            </span>
            <span class="tooltip-cat">{{ item.category }}</span>
            <span class="tooltip-line">{{ item.line_range }}</span>
          </div>
          <p class="tooltip-desc">{{ item.description }}</p>
          <pre v-if="item.code_snippet" class="tooltip-code"><code>{{ item.code_snippet }}</code></pre>
        </div>
      </div>
    </Teleport>
  </span>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'RiskBadge',
  props: {
    items: { type: Array, required: true }
  },
  setup(props) {
    const expanded = ref(false)
    const SEV_ORDER = { critical: 4, high: 3, medium: 2, low: 1 }

    const topSeverity = computed(() => {
      if (!props.items.length) return 'low'
      return props.items.reduce((a, b) =>
        (SEV_ORDER[a.severity] || 0) > (SEV_ORDER[b.severity] || 0) ? a : b
      ).severity
    })

    return { expanded, topSeverity }
  }
}
</script>

<style scoped>
.risk-badge-wrapper { position: relative; display: inline-flex; align-items: center; margin-left: 4px; }
.risk-dot {
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  cursor: pointer; flex-shrink: 0; transition: transform 0.15s;
}
.risk-dot:hover { transform: scale(1.4); }

.sev-critical { background: #f85149; }
.sev-high { background: #f0883e; }
.sev-medium { background: #d29922; }
.sev-low { background: #58a6ff; }

/* Tooltip */
.risk-tooltip-backdrop { position: fixed; inset: 0; z-index: 200; }
.risk-tooltip {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 201; width: 520px; max-height: 70vh; overflow-y: auto;
  background: #161b22; border: 1px solid #30363d; border-radius: 8px;
  padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
.risk-tooltip.sev-critical { border-color: #f8514966; }
.risk-tooltip.sev-high { border-color: #f0883e66; }
.risk-tooltip.sev-medium { border-color: #d2992266; }
.risk-tooltip.sev-low { border-color: #58a6ff66; }

.tooltip-item + .tooltip-item { margin-top: 12px; padding-top: 12px; border-top: 1px solid #30363d44; }
.tooltip-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tooltip-sev {
  font-size: 0.65rem; font-weight: 700; padding: 1px 6px; border-radius: 4px;
  color: #fff;
}
.tooltip-sev.sev-critical { background: #f85149; }
.tooltip-sev.sev-high { background: #f0883e; }
.tooltip-sev.sev-medium { background: #d29922; }
.tooltip-sev.sev-low { background: #58a6ff; }
.tooltip-cat { font-size: 0.72rem; color: #8b949e; }
.tooltip-line { font-size: 0.72rem; color: #58a6ff; margin-left: auto; }
.tooltip-desc { font-size: 0.85rem; color: #c9d1d9; line-height: 1.5; margin: 0; }
.tooltip-code {
  margin-top: 8px; padding: 10px; background: #0d1117; border-radius: 6px;
  font-size: 0.78rem; overflow-x: auto;
}
.tooltip-code code { color: #c9d1d9; font-family: 'Fira Code', 'Consolas', monospace; }
</style>
