import { ref, computed } from 'vue'

/**
 * Composable for fetching PR data.
 * Loads diff first (fast), then review (slow — calls DeepSeek).
 */
export function usePrData() {
  const diffData = ref(null)
  const reviewData = ref(null)
  const diffLoading = ref(false)
  const reviewLoading = ref(false)
  const error = ref(null)

  const files = computed(() => {
    return diffData.value?.structured_diff?.files || []
  })

  const stats = computed(() => {
    return diffData.value?.structured_diff?.stats || { files_changed: 0, additions: 0, deletions: 0 }
  })

  const prInfo = computed(() => diffData.value?.pr || null)
  const loading = computed(() => diffLoading.value || reviewLoading.value)

  async function fetchAll(owner, repo, pr) {
    error.value = null

    // 1. Load diff first (fast — GitHub API with mock fallback)
    diffLoading.value = true
    reviewLoading.value = true  // show loading for both while diff loads
    try {
      const { fetchDiff, fetchReview } = await import('../api/index.js')

      const diff = await fetchDiff(owner, repo, pr)
      diffData.value = diff
      diffLoading.value = false
      // diff loaded, review still loading

      // 2. Load review (slow — calls DeepSeek)
      const review = await fetchReview(owner, repo, pr)
      reviewData.value = review
      reviewLoading.value = false

    } catch (e) {
      error.value = e.message
      diffLoading.value = false
      reviewLoading.value = false
    }
  }

  return { diffData, reviewData, files, stats, prInfo, diffLoading, reviewLoading, loading, error, fetchAll }
}
