<template>
  <div class="modern-header">
    <div class="header-content">
      <div class="logo-section">
        <el-icon class="app-logo" :size="32">
          <Search />
        </el-icon>
        <h3 class="app-name">语义匹配</h3>
      </div>

      <div class="nav-menu">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: activeIndex === item.path }"
          active-class="active"
        >
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </div>

      <div class="user-section">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="user-avatar">
            <el-avatar :size="36" :src="userAvatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ authStore.user?.username }}</span>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Search,
  Document,
  User,
  Setting,
  ArrowDown,
  SwitchButton,
  Folder,
  ChatLineRound,
} from '@element-plus/icons-vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 导航配置
const navItems = [
  { path: '/search', label: '搜索', icon: Search },
  { path: '/projects', label: '项目', icon: Folder },
  { path: '/documents', label: '文档', icon: Document },
  { path: '/chat', label: '聊天', icon: ChatLineRound },
];

const activeIndex = computed(() => router.currentRoute.value.path);
const userAvatar = computed(() =>
  `https://api.dicebear.com/7.x/initials/svg?seed=${authStore.user?.username}`
);

// 处理用户菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile');
      break;
    case 'settings':
      router.push('/settings');
      break;
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        });
        authStore.logout();
        ElMessage.success('已退出登录');
        router.push('/login');
      } catch {
        // 用户取消
      }
      break;
  }
};
</script>

<style scoped>
/* CSS 变量定义 */
:root {
  --primary-color: #6366f1;
  --primary-hover: #5856eb;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --transition-fast: 0.15s ease-in-out;
  --transition-medium: 0.3s ease-in-out;
}

/* 导航栏样式 */
.modern-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 64px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.app-logo {
  color: var(--primary-color);
}

.app-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--gray-800);
  margin: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--gray-600);
  font-weight: 500;
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  position: relative;
}

.nav-item:hover {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.1);
}

.nav-item.active {
  color: var(--primary-color);
  background: rgba(99, 102, 241, 0.15);
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--primary-color);
  border-radius: 1px;
}

.user-section {
  flex-shrink: 0;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.user-avatar:hover {
  background: var(--gray-50);
  border-color: var(--gray-200);
}

.username {
  font-weight: 500;
  color: var(--gray-700);
  font-size: 0.875rem;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  color: var(--gray-400);
  font-size: 0.75rem;
  transition: transform var(--transition-fast);
}

.user-avatar:hover .dropdown-icon {
  transform: rotate(180deg);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    padding: 0 1rem;
  }

  .nav-menu {
    gap: 0.25rem;
  }

  .nav-item {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .username {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 1rem;
    gap: 1rem;
  }

  .nav-menu {
    order: 3;
    width: 100%;
    justify-content: space-around;
    background: var(--gray-50);
    padding: 0.5rem;
    border-radius: 0.5rem;
    margin-top: 0.5rem;
  }

  .nav-item {
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .nav-item span {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .app-name {
    font-size: 1rem;
  }
}
</style>
