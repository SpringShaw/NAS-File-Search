import { createApp } from 'vue'
import App from './App.vue'
import { t, toggleLanguage, i18n } from './i18n.js'
import './style.css'

const app = createApp(App)
// 全局响应式翻译函数，任意组件可用 this.$t('key', { param })
// 切换语言时 i18n.lang 变化，依赖 $t 的计算属性自动重算
app.use({
  install(app) {
    app.config.globalProperties.$t = t
    app.config.globalProperties.$toggleLanguage = toggleLanguage
    app.config.globalProperties.$i18n = i18n
  },
})
app.mount('#app')
