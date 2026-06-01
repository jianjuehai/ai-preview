const BASE = '/api'
const TIMEOUT_MS = 15000  // 15 second timeout

async function fetchWithTimeout(url) {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS)
  try {
    const res = await fetch(url, { signal: ctrl.signal })
    if (!res.ok) throw new Error(`API error: ${res.status}`)
    return res.json()
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
