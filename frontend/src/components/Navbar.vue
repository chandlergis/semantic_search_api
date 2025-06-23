<template>
  <nav class="navbar">
    <ul class="nav-menu">
      <li
        v-for="item in navItems"
        :key="item.path"
        :class="{ active: activeIndex === item.path }"
        @click="navigate(item.path)"
      >
        <el-icon>
          <component :is="item.icon" />
        </el-icon>
        <span>{{ item.label }}</span>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Folder, Document, Upload } from '@element-plus/icons-vue'

const router = useRouter()

const navItems = [
  { path: '/search', label: '搜索', icon: Search },
  { path: '/projects', label: '项目', icon: Folder },
  { path: '/documents', label: '文档', icon: Document },
  { path: '/upload', label: '上传', icon: Upload }
]

const activeIndex = computed(() => router.currentRoute.value.path)

const navigate = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.navbar {
  display: flex;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 2rem;
  height: 64px;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-menu li {
  display: flex;
  align-items: center;
  margin-right: 1.5rem;
  cursor: pointer;
  transition: color 0.3s;
}

.nav-menu li.active {
  color: var(--primary-color);
}

.nav-menu li:hover {
  color: var(--primary-color);
}

.nav-menu li el-icon {
  margin-right: 0.5rem;
}
</style>