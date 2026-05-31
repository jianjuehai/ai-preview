import { ref, computed } from 'vue'

/**
 * Composable for fetching PR data (diff + review) with loading/error state.
 */
export function usePrData() {
  const diffData = ref(null)
  const reviewData = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const files = computed(() => {
    return diffData.value?.structured_diff?.files || []
  })

  const stats = computed(() => {
    return diffData.value?.structured_diff?.stats || { files_changed: 0, additions: 0, deletions: 0 }
  })

  const prInfo = computed(() => diffData.value?.pr || null)

  async function fetchAll(owner, repo, pr) {
    loading.value = true
    error.value = null
    try {
      const { fetchDiff, fetchReview } = await import('../api/index.js')
      const [diff, review] = await Promise.all([
        fetchDiff(owner, repo, pr),
        fetchReview(owner, repo, pr)
      ])
      diffData.value = diff
      reviewData.value = review
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { diffData, reviewData, files, stats, prInfo, loading, error, fetchAll }
}
