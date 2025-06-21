<template>
  <div class="documents-view">
    <!-- 现代化导航栏 -->
    <div class="modern-header">
      <div class="header-content">
        <!-- Logo区域 -->
        <div class="logo-section">
          <el-icon class="app-logo" :size="32">
            <Search />
          </el-icon>
          <h3 class="app-name">语义匹配</h3>
        </div>

        <!-- 导航菜单 -->
        <div class="nav-menu">
          <router-link 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: activeIndex === item.path }"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </div>

        <!-- 用户区域 -->
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

    <!-- 文档列表 -->
    <div class="content">
      <div class="content-header">
        <h2>文档管理</h2>
        <el-button type="primary" @click="$router.push('/upload')">
          <el-icon><Plus /></el-icon>
          上传文档
        </el-button>
      </div>

      <div class="documents-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <!-- 文档表格 -->
        <el-table 
          v-else-if="documents.length > 0"
          :data="documents" 
          style="width: 100%"
          stripe
        >
          <el-table-column prop="title" label="文档标题" min-width="200">
            <template #default="{ row }">
              <div class="document-title">
                <el-icon class="file-icon">
                  <Document v-if="row.file_type === 'pdf'" />
                  <EditPen v-else-if="row.file_type === 'docx'" />
                  <DocumentCopy v-else />
                </el-icon>
                {{ row.title }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="file_type" label="文件类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getFileTypeColor(row.file_type)">
                {{ row.file_type.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="file_size" label="文件大小" width="120">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="chunk_count" label="片段数" width="100" />
          
          <el-table-column prop="upload_time" label="上传时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button 
                size="small" 
                type="primary" 
                @click="searchInDocument(row)"
              >
                搜索
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteDocument(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无文档">
            <el-button type="primary" @click="$router.push('/upload')">
              立即上传
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Document, 
  Plus, 
  EditPen, 
  DocumentCopy,
  User,
  ArrowDown,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import type { DocumentRead } from '@/types/api'
import { documentService } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 导航配置
const navItems = [
  { path: '/search', label: '搜索', icon: 'Search' },
  { path: '/projects', label: '项目', icon: 'Folder' },
  { path: '/documents', label: '文档', icon: 'Document' },
  { path: '/upload', label: '上传', icon: 'Upload' }
]

// 当前激活的菜单项
const activeIndex = computed(() => router.currentRoute.value.path)

// 用户头像
const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${authStore.user?.username}`
})

// 用户菜单处理
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // 设置页面
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}

// 状态
const loading = ref(false)
const documents = ref<DocumentRead[]>([])

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const response = await documentService.getDocuments()
    documents.value = response.documents
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 删除文档
const deleteDocument = async (document: DocumentRead) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await documentService.deleteDocument(document.id)
    ElMessage.success('删除成功')
    await fetchDocuments() // 重新获取列表
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 在文档中搜索
const searchInDocument = (document: DocumentRead) => {
  router.push({
    path: '/search',
    query: { file_id: document.id }
  })
}

// 获取文件类型颜色
const getFileTypeColor = (fileType: string) => {
  const colors: Record<string, string> = {
    pdf: 'danger',
    docx: 'primary',
    doc: 'primary',
    txt: 'info',
    md: 'success'
  }
  return colors[fileType.toLowerCase()] || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.documents-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 现代化导航栏样式 */
.modern-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 64px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-logo {
  color: #3b82f6;
}

.app-name {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #6b7280;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-avatar:hover {
  background: rgba(0, 0, 0, 0.05);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.dropdown-icon {
  font-size: 12px;
  color: #9ca3af;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h2 {
  margin: 0;
  color: #303133;
}

.documents-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-container {
  padding: 20px;
}

.document-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #409eff;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}
</style>