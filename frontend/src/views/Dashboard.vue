<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <h1>AI PR Review</h1>
        <!-- Repo input bar -->
        <form class="repo-form" @submit.prevent="doFetch">
          <input v-model="owner" class="repo-input" placeholder="owner" spellcheck="false" />
          <span class="repo-slash">/</span>
          <input v-model="repo" class="repo-input" placeholder="repo" spellcheck="false" />
          <span class="repo-hash">#</span>
          <input v-model.number="pr" class="repo-input pr-input" type="number" placeholder="1" min="1" />
          <button type="submit" class="go-btn" :disabled="loading">Go</button>
        </form>
        <span v-if="prInfo" class="pr-badge">
          {{ prInfo.base_ref }}#{{ prInfo.number }} — {{ prInfo.title }}
        </span>
        <span v-if="loading" class="loading-tag">Loading...</span>
      </div>
      <div class="header-right">
        <span class="stat">Files: {{ stats.files_changed }}</span>
        <span class="stat add">+{{ stats.additions }}</span>
        <span class="stat del">-{{ stats.deletions }}</span>
        <span v-if="reviewData" class="risk-level" :class="riskLevel">
          {{ riskLevel.toUpperCase() }}
        </span>
      </div>
    </header>

    <!-- Body: two panels -->
    <div class="body">
      <!-- Left Panel: File List -->
      <aside class="left-panel">
        <div class="panel-title">Changed Files</div>

        <!-- Error state -->
        <div v-if="error" class="error-box">
          <p class="error-msg">{{ error }}</p>
          <p class="error-hint">
            Make sure the backend is running:<br/>
            <code>python -m uvicorn src.api.server:app --port 8000</code>
          </p>
          <button class="retry-btn" @click="doFetch">
            Retry
          </button>
        </div>

        <!-- Loading state -->
        <div v-else-if="loading" class="loading-state">
          Fetching PR data...
        </div>

        <!-- File list -->
        <FileList
          v-else
          :files="files"
          :review-data="reviewData"
          :active-file="activeFile"
          @select="onSelectFile"
        />
      </aside>

      <!-- Right Panel: File Detail -->
      <main class="right-panel">
        <router-view v-slot="{ Component }">
          <component
            :is="Component"
            :diff-data="diffData"
            :review-data="reviewData"
            :active-file="activeFile"
          />
        </router-view>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FileList from '../components/FileList.vue'
import { usePrData } from '../composables/useApi.js'

export default {
  name: 'Dashboard',
  components: { FileList },
  setup() {
    const { diffData, reviewData, files, stats, prInfo, loading, error, fetchAll } = usePrData()
    const activeFile = ref(null)
    const router = useRouter()

    const owner = ref('jianjuehai')
    const repo = ref('ai-preview')
    const pr = ref(1)

    function doFetch() {
      if (!owner.value || !repo.value || !pr.value) return
      activeFile.value = null
      router.push({ name: 'dashboard' })
      fetchAll(owner.value, repo.value, pr.value)
    }

    const riskLevel = computed(() => {
      if (!reviewData.value) return 'none'
      const order = { critical: 4, high: 3, medium: 2, low: 1 }
      const risks = reviewData.value.risk_items || []
      if (!risks.length) return 'none'
      return risks.reduce((a, b) =>
        (order[a.severity] || 0) > (order[b.severity] || 0) ? a : b
      ).severity
    })

    function onSelectFile(filename) {
      activeFile.value = filename
      router.push({ name: 'file-detail', params: { filename } })
    }

    onMounted(() => {
      doFetch()
    })

    return { diffData, reviewData, files, stats, prInfo, loading, error, activeFile, riskLevel, onSelectFile, owner, repo, pr, doFetch }
  }
}
</script>

<style>
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --border: #30363d;
  --text-primary: #c9d1d9;
  --text-secondary: #8b949e;
  --accent: #58a6ff;
  --green: #3fb950;
  --red: #f85149;
  --orange: #f0883e;
  --yellow: #d29922;
  --blue: #58a6ff;
}

body { background: var(--bg-primary); color: var(--text-primary); }

.dashboard {
  display: flex; flex-direction: column; height: 100vh;
}

/* Header */
.header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px; background: var(--bg-secondary); border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-left h1 { font-size: 1.1rem; color: var(--accent); font-weight: 600; white-space: nowrap; }

/* Repo input form */
.repo-form { display: flex; align-items: center; gap: 2px; }
.repo-input {
  width: 100px; padding: 4px 8px; background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: 5px; color: var(--text-primary); font-size: 0.8rem; outline: none;
  font-family: inherit;
}
.repo-input:focus { border-color: var(--accent); }
.repo-input.pr-input { width: 52px; -moz-appearance: textfield; }
.repo-input.pr-input::-webkit-outer-spin-button,
.repo-input.pr-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.repo-slash, .repo-hash { color: var(--text-secondary); font-size: 0.8rem; flex-shrink: 0; }
.go-btn {
  padding: 4px 12px; background: #238636; color: #fff; border: none;
  border-radius: 5px; font-size: 0.78rem; font-weight: 600; cursor: pointer; margin-left: 4px;
}
.go-btn:hover { background: #2ea043; }
.go-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.pr-badge { font-size: 0.85rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px; }
.loading-tag { font-size: 0.75rem; color: var(--yellow); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.header-right { display: flex; align-items: center; gap: 14px; font-size: 0.85rem; }
.stat { color: var(--text-secondary); }
.stat.add { color: var(--green); }
.stat.del { color: var(--red); }
.risk-level {
  padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
}
.risk-level.critical { background: #f8514922; color: var(--red); }
.risk-level.high { background: #f0883e22; color: var(--orange); }
.risk-level.medium { background: #d2992222; color: var(--yellow); }
.risk-level.low { background: #58a6ff22; color: var(--blue); }
.risk-level.none { background: #3fb95022; color: var(--green); }

/* Body */
.body { display: flex; flex: 1; overflow: hidden; }

/* Left Panel */
.left-panel {
  width: 300px; min-width: 260px; background: var(--bg-secondary);
  border-right: 1px solid var(--border); overflow-y: auto; flex-shrink: 0;
}
.panel-title {
  padding: 12px 16px; font-size: 0.8rem; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-secondary);
  border-bottom: 1px solid var(--border); position: sticky; top: 0;
  background: var(--bg-secondary);
}

/* Right Panel */
.right-panel {
  flex: 1; overflow-y: auto; background: var(--bg-primary);
}

/* Error */
.error-box {
  padding: 24px 16px; text-align: center;
}
.error-msg { color: var(--red); font-size: 0.9rem; margin-bottom: 12px; }
.error-hint { color: var(--text-secondary); font-size: 0.78rem; margin-bottom: 16px; line-height: 1.6; }
.error-hint code {
  background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px;
  font-size: 0.75rem; color: var(--accent);
}
.retry-btn {
  padding: 6px 20px; background: #1f6feb; color: #fff; border: none;
  border-radius: 6px; font-size: 0.85rem; cursor: pointer;
}
.retry-btn:hover { background: #388bfd; }

/* Loading state (in panel, not full-screen overlay) */
.loading-state {
  padding: 32px 16px; text-align: center; color: var(--text-secondary);
  font-size: 0.85rem;
}
</style>
