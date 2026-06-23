import { reactive } from 'vue'

const LANGUAGE_KEY = 'nas_language'

// 文件分类：中文键（与后端 /api/search?type= 契约保持一致）→ i18n key
export const CATEGORY_KEYS = {
  '图片': 'cat_image',
  '视频': 'cat_video',
  '文档': 'cat_document',
  '日志': 'cat_log',
  '脚本': 'cat_script',
  '压缩包': 'cat_archive',
  '音频': 'cat_audio',
  '其他': 'cat_other',
}

const translations = {
  zh: {
    // 通用
    pageTitle: 'NAS Searcher - 全局文件搜索',
    appTitle: 'NAS Searcher',
    indexedCount: '{count} 个文件已索引',
    settings: '⚙️',
    settingsTitle: '设置',
    close: '✕',
    languageToggleToEn: 'English',
    languageToggleToZh: '中文',
    languageToggleTitleEn: 'Switch to English',
    languageToggleTitleZh: '切换到中文',

    // 搜索栏
    searchPlaceholder: '搜索文件名、路径、内容...',
    searchHint: '支持文件名、路径搜索 · 文本文件支持全文内容搜索',
    clear: '✕',

    // 类型过滤
    cat_all: '全部',
    cat_image: '图片',
    cat_video: '视频',
    cat_document: '文档',
    cat_log: '日志',
    cat_script: '脚本',
    cat_archive: '压缩包',
    cat_audio: '音频',
    cat_other: '其他',

    // 索引状态
    indexing: '🔄 正在建立索引...',
    filesUnit: '个文件',
    dirsUnit: '个目录',
    fulltextUnit: '个全文索引',
    rebuildIndex: '🔄 重建索引',
    indexingInProgress: '索引中...',
    lastRebuild: '最后索引',

    // 搜索结果
    searching: '搜索中...',
    noResult: '未找到匹配 "{query}" 的文件',
    foundResults: '找到 {total} 个结果',
    noQueryTitle: '输入关键词开始搜索',
    noQueryHint: '支持文件名、路径、文件内容搜索',
    prevPage: '← 上一页',
    nextPage: '下一页 →',

    // 设置面板
    addSearchDir: '添加搜索目录',
    addPlaceholder: '/nas/host/photos',
    addBtn: '添加',
    adding: '...',
    dirListLabel: '搜索目录列表',
    noDirs: '暂无搜索目录，请添加',
    deleteDir: '🗑️',
    dirAdded: '目录已添加',
    dirDeleted: '目录已删除',
    dirExists: '该目录已存在',
    dirNotFound: '目录不存在',
    addFailed: '添加目录失败，请检查日志',

    // API Key
    apiKeyLabel: '🔒 API Key',
    apiKeySet: '已设置（访问受保护）',
    apiKeyUnset: '未设置（未启用认证）',
    apiKeyEdit: '修改',
    apiKeySetBtn: '设置',
    apiKeyClear: '清除',
    apiKeyHint: '仅当服务端配置了 API_KEY 环境变量时才生效',
    apiKeyPrompt: '请输入 API Key：',
    apiKeyPromptRetry: '此服务启用了 API Key 认证，请输入 API Key：',
    apiKeyRequired: '需要有效的 API Key',
    invalidType: '无效的文件类型',

    // 相对时间
    justNow: '刚刚',
    minutesAgo: '{n} 分钟前',
    hoursAgo: '{n} 小时前',
    daysAgo: '{n} 天前',

    // 文件大小单位
    sizeUnit: ['B', 'KB', 'MB', 'GB', 'TB'],
  },

  en: {
    pageTitle: 'NAS Searcher - Global File Search',
    appTitle: 'NAS Searcher',
    indexedCount: '{count} files indexed',
    settings: '⚙️',
    settingsTitle: 'Settings',
    close: '✕',
    languageToggleToEn: 'English',
    languageToggleToZh: '中文',
    languageToggleTitleEn: 'Switch to English',
    languageToggleTitleZh: 'Switch to Chinese',

    searchPlaceholder: 'Search file names, paths, content...',
    searchHint: 'Search by name & path · Full-text search for text files',
    clear: '✕',

    cat_all: 'All',
    cat_image: 'Images',
    cat_video: 'Video',
    cat_document: 'Docs',
    cat_log: 'Logs',
    cat_script: 'Scripts',
    cat_archive: 'Archives',
    cat_audio: 'Audio',
    cat_other: 'Other',

    indexing: '🔄 Building index...',
    filesUnit: 'files',
    dirsUnit: 'dirs',
    fulltextUnit: 'full-text indexed',
    rebuildIndex: '🔄 Rebuild index',
    indexingInProgress: 'Indexing...',
    lastRebuild: 'Last index',

    searching: 'Searching...',
    noResult: 'No files found for "{query}"',
    foundResults: '{total} results found',
    noQueryTitle: 'Enter a keyword to start searching',
    noQueryHint: 'Search by file name, path, or content',
    prevPage: '← Prev',
    nextPage: 'Next →',

    addSearchDir: 'Add search directory',
    addPlaceholder: '/nas/host/photos',
    addBtn: 'Add',
    adding: '...',
    dirListLabel: 'Search directories',
    noDirs: 'No directories yet, please add one',
    deleteDir: '🗑️',
    dirAdded: 'Directory added',
    dirDeleted: 'Directory deleted',
    dirExists: 'This directory already exists',
    dirNotFound: 'Directory not found',
    addFailed: 'Failed to add directory, check logs',

    apiKeyLabel: '🔒 API Key',
    apiKeySet: 'Set (access protected)',
    apiKeyUnset: 'Not set (auth disabled)',
    apiKeyEdit: 'Edit',
    apiKeySetBtn: 'Set',
    apiKeyClear: 'Clear',
    apiKeyHint: 'Only effective when the server has API_KEY configured',
    apiKeyPrompt: 'Please enter the API Key:',
    apiKeyPromptRetry: 'This service requires an API Key. Please enter it:',
    apiKeyRequired: 'A valid API Key is required',
    invalidType: 'Invalid file type',

    justNow: 'just now',
    minutesAgo: '{n} min ago',
    hoursAgo: '{n} h ago',
    daysAgo: '{n} d ago',

    sizeUnit: ['B', 'KB', 'MB', 'GB', 'TB'],
  },
}

function getInitialLanguage() {
  try {
    const saved = localStorage.getItem(LANGUAGE_KEY)
    if (saved === 'zh' || saved === 'en') return saved
  } catch {
    /* localStorage 不可用时忽略 */
  }
  // 浏览器语言以 zh 开头 → 中文，其他 → 英文，无法读取 → 中文
  const lang = (typeof navigator !== 'undefined' && navigator.language) || ''
  return lang.toLowerCase().startsWith('zh') ? 'zh' : 'en'
}

// 响应式语言状态，切换时所有依赖 t() 的组件自动更新
export const i18n = reactive({
  lang: getInitialLanguage(),
})

export function setLanguage(lang) {
  if (lang !== 'zh' && lang !== 'en') return
  i18n.lang = lang
  try {
    localStorage.setItem(LANGUAGE_KEY, lang)
  } catch {
    /* 忽略 */
  }
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en'
    document.title = t('pageTitle')
  }
}

export function toggleLanguage() {
  setLanguage(i18n.lang === 'zh' ? 'en' : 'zh')
}

export function t(key, params = {}) {
  const dict = translations[i18n.lang] || translations.zh
  let text = dict[key]
  if (text === undefined) text = translations.zh[key]
  if (text === undefined) return key
  if (Array.isArray(text)) return text
  Object.keys(params).forEach((name) => {
    text = text.replace(`{${name}}`, params[name])
  })
  return text
}

// 初始化页面 lang 与 title
setLanguage(i18n.lang)
