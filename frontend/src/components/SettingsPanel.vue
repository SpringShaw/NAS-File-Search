<template>
  <div
    class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-start justify-center pt-20 px-4"
    @mousedown.self="onMaskMouseDown"
    @mouseup.self="onMaskMouseUp"
  >
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden fade-in-up">
      <!-- Header -->
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-[#1d1d1f]">⚙️ 设置</h2>
        <button @click="$emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 transition">
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="px-5 py-4 max-h-[60vh] overflow-y-auto">
        <!-- Add Directory -->
        <div class="mb-4">
          <label class="text-sm font-medium text-[#1d1d1f] block mb-2">添加搜索目录</label>
          <div class="flex gap-2">
            <input
              v-model="newDir"
              type="text"
              placeholder="/nas/host/photos"
              class="flex-1 px-3 py-2 rounded-xl border border-gray-200 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition"
              @keydown.enter="addDir"
            />
            <button
              @click="addDir"
              :disabled="!newDir.trim() || adding"
              class="px-4 py-2 rounded-xl bg-[#1d1d1f] text-white text-sm font-medium hover:bg-[#333] transition disabled:opacity-50"
            >
              {{ adding ? '...' : '添加' }}
            </button>
          </div>
          <p v-if="addError" class="text-xs text-red-500 mt-1">{{ addError }}</p>
        </div>

        <!-- Directory List -->
        <div>
          <label class="text-sm font-medium text-[#1d1d1f] block mb-2">搜索目录列表</label>
          <div v-if="dirs.length === 0" class="text-center py-6 text-gray-400 text-sm">
            暂无搜索目录，请添加
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="dir in dirs"
              :key="dir.id"
              class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-xl"
            >
              <span class="text-lg">📂</span>
              <span class="flex-1 text-sm text-[#1d1d1f] truncate">{{ dir.path }}</span>
              <button
                @click="deleteDir(dir.id)"
                class="w-6 h-6 flex items-center justify-center rounded-full text-gray-400 hover:bg-red-50 hover:text-red-500 transition text-xs"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>

        <!-- API Key 设置 -->
        <div class="mt-4 pt-4 border-t border-gray-100">
          <label class="text-sm font-medium text-[#1d1d1f] block mb-2">🔒 API Key</label>
          <div class="flex items-center gap-2">
            <span class="flex-1 text-xs" :class="apiKeySet ? 'text-gray-500' : 'text-gray-400'">
              {{ apiKeySet ? '已设置（访问受保护）' : '未设置（未启用认证）' }}
            </span>
            <button @click="editApiKey" class="px-3 py-1 text-xs bg-gray-100 rounded-lg hover:bg-gray-200 transition">
              {{ apiKeySet ? '修改' : '设置' }}
            </button>
            <button v-if="apiKeySet" @click="clearApiKey" class="px-3 py-1 text-xs bg-gray-100 rounded-lg hover:bg-red-50 hover:text-red-500 transition">
              清除
            </button>
          </div>
          <p class="text-xs text-gray-400 mt-1">仅当服务端配置了 API_KEY 环境变量时才生效</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api, setApiKey } from '../services/api.js'

export default {
  name: 'SettingsPanel',
  emits: ['close', 'dirs-updated'],
  setup(props, { emit }) {
    const dirs = ref([])
    const newDir = ref('')
    const adding = ref(false)
    const addError = ref('')
    const apiKeySet = ref(false)

    // 弹窗遮罩关闭：仅当 mousedown 与 mouseup 都落在遮罩层（.self）时才触发，
    // 避免在弹窗内拖选文字超出范围时误触发关闭
    let mouseDownOnMask = false
    const onMaskMouseDown = () => { mouseDownOnMask = true }
    const onMaskMouseUp = () => {
      if (mouseDownOnMask) {
        mouseDownOnMask = false
        emit('close')
      }
    }

    const refreshApiKeySet = () => {
      try {
        apiKeySet.value = !!localStorage.getItem('nas_api_key')
      } catch {
        apiKeySet.value = false
      }
    }
    const editApiKey = () => {
      const key = window.prompt('请输入 API Key：')
      if (key !== null) {
        setApiKey(key.trim())
        refreshApiKeySet()
      }
    }
    const clearApiKey = () => {
      setApiKey('')
      refreshApiKeySet()
    }

    const fetchDirs = async () => {
      try {
        dirs.value = await api.getDirs()
      } catch (e) {
        console.error('Failed to fetch dirs:', e)
      }
    }

    const addDir = async () => {
      if (!newDir.value.trim()) return
      adding.value = true
      addError.value = ''
      try {
        await api.addDir(newDir.value.trim())
        newDir.value = ''
        await fetchDirs()
        emit('dirs-updated')
      } catch (e) {
        addError.value = e.message || '添加失败'
      } finally {
        adding.value = false
      }
    }

    const deleteDir = async (id) => {
      try {
        await api.deleteDir(id)
        await fetchDirs()
        emit('dirs-updated')
      } catch (e) {
        console.error('Failed to delete dir:', e)
      }
    }

    onMounted(() => {
      refreshApiKeySet()
      fetchDirs()
    })

    return {
      dirs, newDir, adding, addError, apiKeySet,
      onMaskMouseDown, onMaskMouseUp, editApiKey, clearApiKey, addDir, deleteDir,
    }
  },
}
</script>
