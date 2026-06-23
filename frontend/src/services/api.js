import { t } from '../i18n.js'

const API_BASE = ''

function getApiKey() {
  try {
    return localStorage.getItem('nas_api_key') || ''
  } catch {
    return ''
  }
}

export function setApiKey(key) {
  try {
    if (key) localStorage.setItem('nas_api_key', key)
    else localStorage.removeItem('nas_api_key')
  } catch {
    /* 忽略隐私模式下 localStorage 不可用 */
  }
}

let prompting = false

async function request(url, options = {}) {
  const headers = { ...(options.headers || {}), 'Content-Type': 'application/json' }
  const apiKey = getApiKey()
  if (apiKey) headers['X-API-Key'] = apiKey
  const res = await fetch(API_BASE + url, { ...options, headers })

  // 后端启用了 API Key 认证但本地未配置或配置错误：提示输入并重试一次
  if (res.status === 401 && !prompting && !options._retried) {
    prompting = true
    const key = window.prompt(t('apiKeyPromptRetry'))
    prompting = false
    if (key) {
      setApiKey(key.trim())
      return request(url, { ...options, _retried: true })
    }
    throw new Error(t('apiKeyRequired'))
  }

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
