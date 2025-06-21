<template>
  <div class="upload-view">
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

    <!-- 上传区域 -->
    <div class="content">
      <div class="upload-container">
        <h2>上传文档</h2>
        
        <!-- 项目选择 -->
        <div class="project-selector">
          <el-form-item label="选择项目：">
            <el-select
              v-model="selectedProjectId"
              placeholder="选择项目（可选）"
              clearable
              style="width: 300px"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
        </div>
        
        <div class="upload-area">
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="customUpload"
            multiple
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、TXT、Markdown 文件，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
        </div>

        <!-- 上传列表 -->
        <div v-if="uploadList.length > 0" class="upload-list">
          <h3>上传队列</h3>
          <div class="file-list">
            <div 
              v-for="file in uploadList" 
              :key="file.id"
              class="file-item"
            >
              <div class="file-info">
                <el-icon class="file-icon">
                  <Document />
                </el-icon>
                <div class="file-details">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-size">{{ formatFileSize(file.size) }}</div>
                </div>
              </div>
              
              <div class="file-status">
                <div v-if="file.status === 'uploading'" class="uploading">
                  <el-progress 
                    :percentage="file.progress" 
                    :stroke-width="6"
                    status="primary"
                  />
                </div>
                
                <div v-else-if="file.status === 'success'" class="success">
                  <el-icon color="#67c23a"><CircleCheck /></el-icon>
                  <span>上传成功</span>
                </div>
                
                <div v-else-if="file.status === 'error'" class="error">
                  <el-icon color="#f56c6c"><CircleClose /></el-icon>
                  <span>{{ file.error || '上传失败' }}</span>
                </div>
                
                <div v-else class="waiting">
                  <el-icon><Clock /></el-icon>
                  <span>等待上传</span>
                </div>
              </div>
              
              <el-button 
                v-if="file.status !== 'uploading'"
                size="small" 
                type="danger" 
                text
                @click="removeFile(file.id)"
              >
                移除
              </el-button>
            </div>
          </div>
          
          <div class="upload-actions">
            <el-button 
              type="primary" 
              @click="startUpload"
              :loading="isUploading"
              :disabled="uploadList.every(f => ['success', 'uploading'].includes(f.status))"
            >
              开始上传
            </el-button>
            <el-button @click="clearAll">清空列表</el-button>
          </div>
        </div>

        <!-- 上传统计 -->
        <div v-if="uploadList.length > 0" class="upload-stats">
          <el-card>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">{{ uploadList.length }}</div>
                <div class="stat-label">总文件数</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ successCount }}</div>
                <div class="stat-label">成功</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ errorCount }}</div>
                <div class="stat-label">失败</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ formatFileSize(totalSize) }}</div>
                <div class="stat-label">总大小</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Search, 
  Document, 
  UploadFilled, 
  CircleCheck, 
  CircleClose, 
  Clock,
  User,
  ArrowDown,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { documentService, projectService } from '@/services/api'
import type { ProjectRead } from '@/types/api'
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

// 文件上传相关
interface UploadFile {
  id: string
  name: string
  size: number
  file: File
  status: 'waiting' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

const uploadRef = ref()
const uploadList = ref<UploadFile[]>([])
const isUploading = ref(false)

// 项目相关
const projects = ref<ProjectRead[]>([])
const selectedProjectId = ref<string>('')

// 计算属性
const successCount = computed(() => 
  uploadList.value.filter(f => f.status === 'success').length
)

const errorCount = computed(() => 
  uploadList.value.filter(f => f.status === 'error').length
)

const totalSize = computed(() => 
  uploadList.value.reduce((total, file) => total + file.size, 0)
)

// 上传前检查
const beforeUpload = (file: File) => {
  // 检查文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件类型')
    return false
  }
  
  // 检查文件大小 (50MB)
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  return false // 阻止自动上传，改为手动控制
}

// 自定义上传
const customUpload = (options: any) => {
  const file = options.file
  
  // 添加到上传列表
  const uploadFile: UploadFile = {
    id: Date.now() + Math.random().toString(),
    name: file.name,
    size: file.size,
    file: file,
    status: 'waiting',
    progress: 0
  }
  
  uploadList.value.push(uploadFile)
  ElMessage.success(`${file.name} 已添加到上传队列`)
}

// 开始上传
const startUpload = async () => {
  const waitingFiles = uploadList.value.filter(f => f.status === 'waiting')
  
  if (waitingFiles.length === 0) {
    ElMessage.warning('没有待上传的文件')
    return
  }
  
  isUploading.value = true
  
  // 逐个上传文件
  for (const uploadFile of waitingFiles) {
    await uploadSingleFile(uploadFile)
  }
  
  isUploading.value = false
  ElMessage.success('批量上传完成')
}

// 上传单个文件
const uploadSingleFile = async (uploadFile: UploadFile) => {
  uploadFile.status = 'uploading'
  uploadFile.progress = 0
  
  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadFile.progress < 90) {
        uploadFile.progress += Math.random() * 20
      }
    }, 200)
    
    await documentService.uploadDocument(uploadFile.file, selectedProjectId.value || undefined)
    
    clearInterval(progressInterval)
    uploadFile.progress = 100
    uploadFile.status = 'success'
    
  } catch (error: any) {
    uploadFile.status = 'error'
    uploadFile.error = error.message || '上传失败'
    console.error('上传失败:', error)
  }
}

// 移除文件
const removeFile = (fileId: string) => {
  const index = uploadList.value.findIndex(f => f.id === fileId)
  if (index > -1) {
    uploadList.value.splice(index, 1)
  }
}

// 清空列表
const clearAll = () => {
  uploadList.value = []
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await projectService.getProjects({ per_page: 100 })
    projects.value = response.projects
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 组件挂载时获取项目列表
onMounted(() => {
  fetchProjects()
})

</script>

<style scoped>
.upload-view {
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
  background: #f5f5f5;
}

.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-container h2 {
  margin-bottom: 24px;
  color: #303133;
}

.project-selector {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.upload-area {
  margin-bottom: 24px;
}

.upload-dragger {
  width: 100%;
}

.upload-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.upload-list h3 {
  margin-bottom: 16px;
  color: #303133;
}

.file-list {
  space-y: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  margin-bottom: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  color: #409eff;
  font-size: 24px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.uploading, .success, .error, .waiting {
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.upload-stats {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.upload-view {
  padding: 2rem;
}
</style>