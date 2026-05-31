const BASE = '/api'

export async function fetchDiff(owner, repo, pr) {
  const params = new URLSearchParams({ owner, repo, pr })
  const res = await fetch(`${BASE}/diff?${params}`)
  if (!res.ok) throw new Error(`Diff API error: ${res.status}`)
  return res.json()
}

export async function fetchReview(owner, repo, pr) {
  const params = new URLSearchParams({ owner, repo, pr })
  const res = await fetch(`${BASE}/review?${params}`)
  if (!res.ok) throw new Error(`Review API error: ${res.status}`)
  return res.json()
}
