/**
 * Line range parsing and annotation matching logic.
 *
 * RiskItem.line_range = "L12-L15" → matches DiffLine.new_line values 12..15.
 * Suggestion.line_range follows the same format.
 */

/**
 * Parse a line_range string like "L12-L15" or "L10" into { start, end }.
 * Returns null for unparseable input.
 */
export function parseLineRange(range) {
  if (!range) return null
  const m = range.match(/L(\d+)(?:-L?(\d+))?/)
  if (!m) return null
  const start = parseInt(m[1], 10)
  const end = m[2] ? parseInt(m[2], 10) : start
  return { start, end }
}

/**
 * Build a Map<lineNum, { risks: RiskItem[], suggestions: Suggestion[] }>
 * for a single file, matching risk_items and suggestions by file name and
 * then expanding line_range to individual line numbers.
 */
export function buildAnnotations(reviewResult, filename) {
  const map = new Map()

  const empty = () => ({ risks: [], suggestions: [] })

  for (const risk of (reviewResult?.risk_items || [])) {
    if (risk.file !== filename) continue
    const rng = parseLineRange(risk.line_range)
    if (!rng) continue
    for (let ln = rng.start; ln <= rng.end; ln++) {
      if (!map.has(ln)) map.set(ln, empty())
      map.get(ln).risks.push(risk)
    }
  }

  for (const sug of (reviewResult?.suggestions || [])) {
    if (sug.file !== filename) continue
    const rng = parseLineRange(sug.line_range)
    if (!rng) continue
    for (let ln = rng.start; ln <= rng.end; ln++) {
      if (!map.has(ln)) map.set(ln, empty())
      map.get(ln).suggestions.push(sug)
    }
  }

  return map
}

/**
 * Find all risks that apply to a given file (not expanded by line).
 * Used by FileList to show per-file risk counts/dots.
 */
export function getFileRisks(reviewResult, filename) {
  return (reviewResult?.risk_items || []).filter(r => r.file === filename)
}
