<template>
  <div class="project-documents-view">
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
            :class="{ active: isActivePath(item.path) }"
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

    <!-- 项目面包屑 -->
    <div class="project-breadcrumb-section">
      <div class="breadcrumb-container">
        <div class="project-breadcrumb">
          <router-link to="/projects" class="breadcrumb-item">
            <el-icon><Folder /></el-icon>
            项目
          </router-link>
          <el-icon class="breadcrumb-separator"><ArrowRight /></el-icon>
          <span class="current-project">{{ project?.name || '加载中...' }}</span>
        </div>

        <div class="header-actions">
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Plus /></el-icon>
            上传文档
          </el-button>
          <el-dropdown @command="handleCommand" trigger="click">
            <el-button>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="search">
                  <el-icon><Search /></el-icon>
                  在此项目中搜索
                </el-dropdown-item>
                <el-dropdown-item command="edit">
                  <el-icon><Edit /></el-icon>
                  编辑项目
                </el-dropdown-item>
                <el-dropdown-item divided command="delete">
                  <el-icon><Delete /></el-icon>
                  删除项目
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 项目信息卡片 -->
    <div class="content">
      <div class="project-info-card">
        <div class="project-header">
          <div class="project-meta">
            <h1 class="project-title">{{ project?.name }}</h1>
            <p v-if="project?.description" class="project-description">{{ project.description }}</p>
          </div>
          <div class="project-stats">
            <div class="stat-item">
              <el-icon class="stat-icon"><Document /></el-icon>
              <div class="stat-details">
                <div class="stat-value">{{ documents.length }}</div>
                <div class="stat-label">文档</div>
              </div>
            </div>
            <div class="stat-item">
              <el-icon class="stat-icon"><Calendar /></el-icon>
              <div class="stat-details">
                <div class="stat-value">{{ formatDate(project?.created_at) }}</div>
                <div class="stat-label">创建时间</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文档列表 -->
      <div class="documents-section">
        <div class="section-header">
          <h2>项目文档</h2>
          <div class="section-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文档..."
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <!-- 文档表格 -->
        <div v-else-if="filteredDocuments.length > 0" class="documents-table">
          <el-table :data="filteredDocuments" style="width: 100%">
            <el-table-column prop="filename" label="文件名" min-width="200">
              <template #default="{ row }">
                <div class="document-cell">
                  <el-icon class="file-icon">
                    <Document />
                  </el-icon>
                  <span class="filename">{{ row.filename }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="file_size" label="大小" width="100">
              <template #default="{ row }">
                <span>{{ formatFileSize(row.file_size) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag
                  :type="getStatusType(row.status)"
                  size="small"
                >
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="created_at" label="上传时间" width="150">
              <template #default="{ row }">
                <span>{{ formatDateTime(row.created_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  type="primary"
                  text
                  @click="downloadDocument(row)"
                >
                  下载
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  text
                  @click="deleteDocument(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="此项目暂无文档">
            <el-button type="primary" @click="showUploadDialog = true">
              上传第一个文档
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档到项目"
      width="600px"
    >
      <div class="upload-dialog-content">
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
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF、Word、TXT、Markdown 文件，单个文件不超过 50MB
            </div>
          </template>
        </el-upload>

        <!-- 上传列表 -->
        <div v-if="uploadList.length > 0" class="upload-list">
          <div class="upload-header">
            <span>待上传文件 ({{ uploadList.length }})</span>
            <el-button size="small" text @click="clearUploadList">清空</el-button>
          </div>
          
          <div class="file-list">
            <div 
              v-for="file in uploadList" 
              :key="file.id"
              class="file-item"
            >
              <div class="file-info">
                <el-icon><Document /></el-icon>
                <span class="filename">{{ file.name }}</span>
                <span class="filesize">{{ formatFileSize(file.size) }}</span>
              </div>
              <el-button 
                size="small" 
                text 
                type="danger"
                @click="removeUploadFile(file.id)"
              >
                移除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="uploadDocuments"
            :loading="uploading"
            :disabled="uploadList.length === 0"
          >
            上传 {{ uploadList.length > 0 ? `(${uploadList.length})` : '' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Folder,
  ArrowRight,
  Plus,
  MoreFilled,
  Search,
  Edit,
  Delete,
  Document,
  Calendar,
  UploadFilled,
  User,
  ArrowDown,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { projectService, documentService } from '@/services/api'
import type { ProjectRead, DocumentRead } from '@/types/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 导航配置
const navItems = [
  { path: '/search', label: '搜索', icon: 'Search' },
  { path: '/projects', label: '项目', icon: 'Folder' },
  { path: '/documents', label: '文档', icon: 'Document' },
  { path: '/upload', label: '上传', icon: 'Upload' }
]

// 判断当前路径是否激活（项目页面特殊处理）
const isActivePath = (path: string) => {
  if (path === '/projects') {
    return route.path.startsWith('/projects')
  }
  return route.path === path
}

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

// 数据状态
const project = ref<ProjectRead | null>(null)
const documents = ref<DocumentRead[]>([])
const loading = ref(false)
const searchKeyword = ref('')

// 上传相关
const showUploadDialog = ref(false)
const uploadRef = ref()
const uploadList = ref<Array<{ id: string; name: string; size: number; file: File }>>([])
const uploading = ref(false)

// 计算属性
const projectId = computed(() => route.params.id as string)

const filteredDocuments = computed(() => {
  if (!searchKeyword.value) return documents.value
  return documents.value.filter(doc => 
    doc.filename.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 获取项目信息
const fetchProject = async () => {
  try {
    project.value = await projectService.getProject(projectId.value)
  } catch (error) {
    console.error('获取项目信息失败:', error)
    ElMessage.error('获取项目信息失败')
  }
}

// 获取项目文档
const fetchDocuments = async () => {
  loading.value = true
  try {
    console.log('正在获取项目文档，项目ID:', projectId.value)
    const response = await projectService.getProjectDocuments(projectId.value)
    console.log('API响应完整内容:', response)
    console.log('响应中的documents字段:', response.documents)
    documents.value = response.documents || []
    console.log('设置后的documents数组:', documents.value)
    console.log('文档数量:', documents.value.length)
    
    // 额外调试：检查每个文档的project_id
    if (documents.value.length > 0) {
      documents.value.forEach((doc, index) => {
        console.log(`文档${index + 1}:`, {
          id: doc.id,
          filename: doc.filename,
          project_id: doc.project_id,
          owner_id: doc.owner_id
        })
      })
    }
  } catch (error: any) {
    console.error('获取文档列表失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error('获取文档列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 文件上传前检查
const beforeUpload = (file: File) => {
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
  
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  // 手动添加到上传列表
  const uploadFile = {
    id: Date.now() + Math.random().toString(),
    name: file.name,
    size: file.size,
    file: file
  }
  
  uploadList.value.push(uploadFile)
  ElMessage.success(`${file.name} 已添加到上传队列`)
  
  return false // 阻止自动上传，由我们手动控制
}

// 自定义上传处理（空函数，实际处理在beforeUpload中）
const customUpload = () => {
  // 不需要处理，文件已在beforeUpload中添加到队列
}

// 上传文档到项目
const uploadDocuments = async () => {
  if (uploadList.value.length === 0) return
  
  uploading.value = true
  try {
    console.log('开始上传文档到项目:', projectId.value)
    console.log('待上传文件:', uploadList.value.map(f => f.name))
    
    const uploadResults = []
    for (const uploadFile of uploadList.value) {
      console.log('正在上传文件:', uploadFile.name, '到项目:', projectId.value)
      const result = await documentService.uploadDocument(uploadFile.file, projectId.value)
      console.log('上传结果:', result)
      console.log('上传成功的文档project_id:', result.project_id)
      uploadResults.push(result)
    }
    
    console.log('所有文档上传结果:', uploadResults)
    ElMessage.success({
    message: `成功上传 ${uploadList.value.length} 个文档`,
    duration: 1500
  })
    showUploadDialog.value = false
    uploadList.value = []
    
    console.log('上传完成，刷新文档列表...')
    console.log('刷新前文档数量:', documents.value.length)
    await fetchDocuments() // 刷新文档列表
    console.log('刷新后文档数量:', documents.value.length)
  } catch (error: any) {
    console.error('上传失败:', error)
    console.error('上传失败详情:', error.response?.data)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 移除上传文件
const removeUploadFile = (fileId: string) => {
  const index = uploadList.value.findIndex(f => f.id === fileId)
  if (index > -1) {
    uploadList.value.splice(index, 1)
  }
}

// 清空上传列表
const clearUploadList = () => {
  uploadList.value = []
}

// 删除文档
const deleteDocument = async (doc: DocumentRead) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${doc.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await documentService.deleteDocument(doc.id)
    ElMessage.success('文档删除成功')
    await fetchDocuments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 下载文档
const downloadDocument = (doc: DocumentRead) => {
  ElMessage.info(`下载 "${doc.filename}" 功能开发中...`)
}

// 处理命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'search':
      router.push({
        path: '/search',
        query: { project_id: projectId.value }
      })
      break
    case 'edit':
      ElMessage.info('编辑项目功能开发中...')
      break
    case 'delete':
      try {
        if (!project.value) {
          ElMessage.error('项目信息加载中，请稍后再试')
          return
        }
        
        console.log('开始删除项目:', projectId.value, project.value.name)
        
        await ElMessageBox.confirm(
          `确定要删除项目 "${project.value.name}" 吗？此操作无法撤销，项目下的所有文档将被移出项目。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        console.log('用户确认删除，开始调用API')
        const result = await projectService.deleteProject(projectId.value)
        console.log('删除API调用结果:', result)
        
        ElMessage.success('项目删除成功')
        console.log('跳转到项目列表')
        router.push('/projects')
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('删除项目失败:', error)
          console.error('错误详情:', error.response?.data)
          ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
        } else {
          console.log('用户取消删除')
        }
      }
      break
  }
}

// 工具函数
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      'PENDING_PROCESS': '待处理',
      'PROCESSING': '处理中',
      'PENDING_CHUNK': '待分块',
      'SYNCING': '同步中',
      'COMPLETED': '已完成',
      'FAILED': '失败'
    }
    return statusMap[status] || '未知'
  }
// 组件挂载时获取数据
onMounted(() => {
  fetchProject()
  fetchDocuments()
})
</script>

<style scoped>
.project-documents-view {
  min-height: 100vh;
  background: #f8fafc;
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

/* 项目面包屑区域 */
.project-breadcrumb-section {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 0;
}

.breadcrumb-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
}

.project-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #3b82f6;
}

.breadcrumb-separator {
  color: #d1d5db;
}

.current-project {
  font-weight: 600;
  color: #111827;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* 内容区域 */
.content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* 项目信息卡片 */
.project-info-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.project-meta {
  flex: 1;
}

.project-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.project-description {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
  line-height: 1.5;
}

.project-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon {
  font-size: 1.5rem;
  color: #3b82f6;
}

.stat-details {
  text-align: left;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

/* 文档区域 */
.documents-section {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 1rem;
}

/* 文档表格 */
.documents-table {
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.document-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-icon {
  color: #3b82f6;
}

.filename {
  font-weight: 500;
}

/* 上传对话框 */
.upload-dialog-content {
  margin-bottom: 1rem;
}

.upload-dragger {
  width: 100%;
  margin-bottom: 1rem;
}

.upload-list {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.file-list {
  space-y: 0.5rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.filesize {
  font-size: 0.875rem;
  color: #6b7280;
  margin-left: auto;
  margin-right: 1rem;
}

/* 加载和空状态 */
.loading-container {
  padding: 2rem;
}

.empty-state {
  padding: 3rem 0;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .project-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .project-stats {
    justify-content: space-around;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>