import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 样式
import './assets/styles/main.css'


// 认证store
import { useAuthStore } from './stores/auth'

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth()

app.use(router)
app.use(ElementPlus)

app.mount('#app')