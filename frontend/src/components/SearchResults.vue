<template>
  <div>
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
      <p class="text-sm text-gray-400 mt-2">{{ $t('searching') }}</p>
    </div>

    <div v-else-if="query && results.length === 0" class="text-center py-12">
      <p class="text-4xl mb-3">🔍</p>
      <p class="text-gray-500">{{ $t('noResult', { query }) }}</p>
    </div>

    <div v-else-if="results.length > 0">
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm text-gray-500">
          {{ $t('foundResults', { total }) }}
        </p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden divide-y divide-gray-50">
        <div
          v-for="(file, index) in results"
          :key="file.id"
          class="px-4 py-3 flex items-center gap-3 hover:bg-gray-50/50 transition-colors fade-in-up"
          :style="{ animationDelay: (index * 30) + 'ms' }"
        >
          <!-- Thumbnail for images -->
          <div class="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-lg overflow-hidden bg-gray-100">
            <img
              v-if="file.is_image"
              :src="'/api/thumbnail?path=' + encodeURIComponent(file.file_path)"
              :alt="file.file_name"
              class="w-full h-full object-cover"
              loading="lazy"
              @error="($event) => $event.target.style.display = 'none'"
            />
            <span v-else class="text-xl">{{ file.icon }}</span>
          </div>

          <!-- File Info -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-[#1d1d1f] truncate">{{ file.file_name }}</p>
            <p class="text-xs text-gray-400 truncate mt-0.5">{{ file.file_path }}</p>
            <p
              v-if="file.snippet"
              class="text-xs text-gray-500 mt-1 line-clamp-2"
              v-html="safeSnippet(file.snippet)"
            ></p>
          </div>

          <!-- Meta -->
          <div class="flex-shrink-0 text-right">
            <p class="text-xs text-gray-500">{{ formatSize(file.file_size) }}</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ formatTime(file.modified_time) }}</p>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
        <button
          @click="$emit('page-change', page - 1)"
          :disabled="page <= 1"
          class="px-3 py-1.5 rounded-full text-sm bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          {{ $t('prevPage') }}
        </button>
        <span class="text-sm text-gray-500">{{ page }} / {{ totalPages }}</span>
        <button
          @click="$emit('page-change', page + 1)"
          :disabled="page >= totalPages"
          class="px-3 py-1.5 rounded-full text-sm bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          {{ $t('nextPage') }}
        </button>
      </div>
    </div>

    <!-- Empty state when no query -->
    <div v-else class="text-center py-16">
      <p class="text-5xl mb-4">🔍</p>
      <p class="text-gray-500 text-lg">{{ $t('noQueryTitle') }}</p>
      <p class="text-gray-400 text-sm mt-1">{{ $t('noQueryHint') }}</p>
    </div>
  </div>
</template>

<script>
import { computed, getCurrentInstance } from 'vue'
import DOMPurify from 'dompurify'
import { i18n } from '../i18n.js'

export default {
  name: 'SearchResults',
  props: {
    results: { type: Array, default: () => [] },
    total: { type: Number, default: 0 },
    page: { type: Number, default: 1 },
    loading: { type: Boolean, default: false },
    query: { type: String, default: '' },
  },
  emits: ['page-change'],
  setup(props) {
    const { proxy } = getCurrentInstance()
    const pageSize = 20
    const totalPages = computed(() => Math.ceil(props.total / pageSize))

    const formatSize = (bytes) => {
      if (!bytes) return '0 B'
      const units = proxy.$t('sizeUnit')
      let i = 0
      let size = bytes
      while (size >= 1024 && i < units.length - 1) {
        size /= 1024
        i++
      }
      return size.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      try {
        const d = new Date(timestamp * 1000)
        const now = new Date()
        const diff = (now - d) / 1000
        if (diff < 60) return proxy.$t('justNow')
        if (diff < 3600) return proxy.$t('minutesAgo', { n: Math.floor(diff / 60) })
        if (diff < 86400) return proxy.$t('hoursAgo', { n: Math.floor(diff / 3600) })
        if (diff < 604800) return proxy.$t('daysAgo', { n: Math.floor(diff / 86400) })
        // 超过一周用本地化日期，按当前语言选择 locale
        return d.toLocaleDateString(i18n.lang === 'zh' ? 'zh-CN' : 'en-US')
      } catch {
        return ''
      }
    }

    const safeSnippet = (snippet) => (snippet ? DOMPurify.sanitize(snippet) : '')

    return { totalPages, formatSize, formatTime, safeSnippet }
  },
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
