const BASE = '/api'
const TIMEOUT_MS = 120000  // 2 minutes (DeepSeek API can be slow)

async function fetchWithTimeout(url) {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS)
  try {
    const res = await fetch(url, { signal: ctrl.signal })
    if (!res.ok) {
      const body = await res.text().catch(() => '')
      throw new Error(`API ${res.status}: ${body.slice(0, 200) || res.statusText}`)
    }
    return res.json()
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out (2 min). The AI review may take longer with large diffs.')
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}

export async function fetchDiff(owner, repo, pr) {
  const params = new URLSearchParams({ owner, repo, pr })
  return fetchWithTimeout(`${BASE}/diff?${params}`)
}

export async function fetchReview(owner, repo, pr) {
  const params = new URLSearchParams({ owner, repo, pr })
  return fetchWithTimeout(`${BASE}/review?${params}`)
}
