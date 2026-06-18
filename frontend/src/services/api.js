const API_BASE = ''

async function request(url, options = {}) {
  const res = await fetch(API_BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  search(q, type = 'all', page = 1, size = 20) {
    return request(`/api/search?q=${encodeURIComponent(q)}&type=${type}&page=${page}&size=${size}`)
  },
  getStats() {
    return request('/api/stats')
  },
  getDirs() {
    return request('/api/dirs')
  },
  addDir(path, excludeDirs = '', minSize = 0, maxSize = 0) {
    return request('/api/dirs', {
      method: 'POST',
      body: JSON.stringify({ path, exclude_dirs: excludeDirs, min_size: minSize, max_size: maxSize }),
    })
  },
  deleteDir(id) {
    return request(`/api/dirs/${id}`, { method: 'DELETE' })
  },
  rebuildIndex() {
    return request('/api/index/rebuild', { method: 'POST' })
  },
  getIndexStatus() {
    return request('/api/index/status')
  },
  getFileTypes() {
    return request('/api/file-types')
  },
}
