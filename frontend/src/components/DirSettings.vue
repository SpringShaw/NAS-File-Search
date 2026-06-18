<template>
  <div class="w-full max-w-3xl mx-auto px-4">
    <div class="bg-white rounded-xl border border-gray-100 p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-semibold text-gray-700">搜索目录</h3>
        <button
          @click="showAdd = !showAdd"
          class="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
        >
          {{ showAdd ? '取消' : '+ 添加目录' }}
        </button>
      </div>

      <!-- Add form -->
      <div v-if="showAdd" class="mb-4 p-3 bg-gray-50 rounded-lg">
        <input
          v-model="newPath"
          @keydown.enter="addNewDir"
          placeholder="输入目录路径，如 /nas/media"
          class="w-full px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg
                 focus:outline-none focus:border-blue-400 transition-colors"
        />
        <input
          v-model="newExclude"
          placeholder="排除目录（逗号分隔，如 .git,node_modules）"
          class="w-full px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg mt-2
                 focus:outline-none focus:border-blue-400 transition-colors"
        />
        <div v-if="addError" class="text-xs text-red-500 mt-1">{{ addError }}</div>
        <button
          @click="addNewDir"
          :disabled="!newPath.trim() || adding"
          class="mt-2 px-4 py-1.5 text-xs font-medium bg-blue-500 text-white rounded-lg
                 hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {{ adding ? '添加中...' : '确认添加' }}
        </button>
      </div>

      <!-- Directory list -->
      <div v-if="dirs.length === 0" class="text-center py-6 text-gray-400 text-sm">
        还没有配置搜索目录
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="dir in dirs"
          :key="dir.id"
          class="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg group hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-sm">📂</span>
            <span class="text-sm text-gray-700 truncate" :title="dir.path">{{ dir.path }}</span>
            <span v-if="dir.exclude_dirs" class="text-xs text-gray-400 hidden sm:inline">
              排除: {{ dir.exclude_dirs }}
            </span>
          </div>
          <button
            @click="$emit('delete', dir.id)"
            class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all text-sm"
            title="删除"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { addDir } from '../services/api'

const props = defineProps({
  dirs: { type: Array, default: () => [] },
})

const emit = defineEmits(['delete', 'added'])

const showAdd = ref(false)
const newPath = ref('')
const newExclude = ref('')
const addError = ref('')
const adding = ref(false)

async function addNewDir() {
  if (!newPath.value.trim()) return
  adding.value = true
  addError.value = ''
  try {
    await addDir(newPath.value.trim(), newExclude.value.trim())
    newPath.value = ''
    newExclude.value = ''
    showAdd.value = false
    emit('added')
  } catch (e) {
    addError.value = e.message
  } finally {
    adding.value = false
  }
}
</script>
