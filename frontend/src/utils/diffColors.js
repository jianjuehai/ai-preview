/** CSS class mappings for diff lines and severity levels. */

// Diff line type → CSS class
export const LINE_CLASS = {
  addition: 'diff-add',
  deletion: 'diff-del',
  context: 'diff-ctx',
}

// Severity → CSS class
export const SEVERITY_CLASS = {
  critical: 'sev-critical',
  high: 'sev-high',
  medium: 'sev-medium',
  low: 'sev-low',
}

// Severity → icon (single char)
export const SEVERITY_ICON = {
  critical: '●',  // ●
  high: '▲',      // ▲
  medium: '■',    // ■
  low: '▬',       // ▬
}

// Language map: file extension → Prism language
const LANG_MAP = {
  py: 'python', js: 'javascript', ts: 'typescript', jsx: 'jsx', tsx: 'tsx',
  vue: 'markup', html: 'markup', css: 'css', scss: 'css', json: 'json',
  yaml: 'yaml', yml: 'yaml', md: 'markdown', sh: 'bash', sql: 'sql',
  go: 'go', rs: 'rust', java: 'java', c: 'c', cpp: 'cpp', h: 'c',
  rb: 'ruby', php: 'php', xml: 'markup', toml: 'toml',
}

export function getLanguage(filename) {
  const ext = (filename || '').split('.').pop().toLowerCase()
  return LANG_MAP[ext] || 'plaintext'
}
