<template>
  <div class="search-view">
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

    <!-- 优化的搜索区域 -->
    <div class="search-hero" :class="{ collapsed: isSearchCollapsed }">
      <div class="search-container">
        <div class="search-content animate-fadeInUp" v-show="!isSearchCollapsed">
          <h1 class="hero-title">
            智能查重，精准发现
          </h1>
          <p class="hero-subtitle">
            利用AI技术为您提供最相关的结果
          </p>
          
          <!-- 搜索方式选择 -->
          <div class="search-mode-selector">
            <el-radio-group v-model="searchMode" size="large" class="mode-group">
              <el-radio-button label="text">文本搜索</el-radio-button>
              <el-radio-button label="document">文档匹配</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 文本搜索框 -->
          <div v-if="searchMode === 'text'" class="main-search-box">
            <div class="search-input-wrapper">
              <el-input
                v-model="searchQuery"
                placeholder="输入关键词开始搜索..."
                size="large"
                class="main-search-input"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <el-icon class="search-icon"><Search /></el-icon>
                </template>
              </el-input>
              <el-button 
                type="primary" 
                size="large"
                class="search-button"
                @click="handleSearch"
                :loading="loading"
              >
                搜索
              </el-button>
            </div>
          </div>

          <!-- 文档匹配上传区 -->
          <div v-else class="document-match-box">
            <el-upload
              ref="uploadRef"
              class="document-upload"
              :auto-upload="false"
              :show-file-list="true"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              accept=".pdf,.docx,.pptx,.xlsx,.txt,.html,.csv,.json,.xml"
              drag
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将文档拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、Word、PowerPoint、Excel、TXT、HTML、CSV、JSON、XML 格式
                </div>
              </template>
            </el-upload>
            <el-button 
              type="primary" 
              size="large"
              class="match-button"
              @click="handleDocumentMatch"
              :loading="loading"
              :disabled="!selectedFile"
            >
              开始匹配
            </el-button>
          </div>

          <!-- 快速选项 -->
          <div class="quick-options">
            <el-button-group class="option-group">
              <el-button @click="searchOptions.top_k = 5" size="small">
                精确搜索
              </el-button>
              <el-button @click="searchOptions.top_k = 20" size="small">
                广泛搜索
              </el-button>
            </el-button-group>
            
            <el-link 
              @click="showAdvanced = !showAdvanced" 
              :underline="false"
              class="advanced-toggle"
            >
              <el-icon><Setting /></el-icon>
              高级选项
            </el-link>
          </div>

          <!-- 高级搜索面板 -->
          <el-collapse-transition>
            <div v-if="showAdvanced" class="advanced-panel glass-effect">
              <div class="panel-title">高级搜索选项</div>
              <div class="advanced-grid">
                <div class="control-item">
                  <label>结果数量</label>
                  <el-slider
                    v-model="searchOptions.top_k"
                    :min="1"
                    :max="50"
                    :step="1"
                    show-input
                    input-size="small"
                  />
                </div>
                <div class="control-item">
                  <label>BM25权重</label>
                  <el-slider
                    v-model="searchOptions.bm25_weight"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    input-size="small"
                  />
                </div>
                <div class="control-item">
                  <label>TF-IDF权重</label>
                  <el-slider
                    v-model="searchOptions.tfidf_weight"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    input-size="small"
                  />
                </div>
              </div>
            </div>
          </el-collapse-transition>
        </div>
        
        <!-- 收起/展开按钮 -->
        <div class="collapse-toggle" v-if="hasSearched">
          <el-button 
            @click="toggleSearchArea"
            type="text"
            class="toggle-button"
          >
            <el-icon>
              <ArrowDown v-if="isSearchCollapsed" />
              <ArrowUp v-else />
            </el-icon>
            {{ isSearchCollapsed ? '展开搜索' : '收起搜索' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="results-container" v-if="searchResults">
      <div class="results-header">
        <h3>{{ searchMode === 'text' ? '搜索结果' : '文档匹配结果' }}</h3>
        <div class="results-stats">
          <el-tag>{{ searchResults.total_chunks }} 个片段</el-tag>
          <el-tag type="success">{{ searchResults.total_documents }} 个文档</el-tag>
          <el-tag type="info">{{ searchResults.search_time_ms.toFixed(2) }}ms</el-tag>
          <el-tag v-if="searchMode === 'document'" type="warning">
            {{ selectedFile?.name }} 的匹配结果
          </el-tag>
        </div>
      </div>

      <!-- 结果列表 -->
      <div class="results-list">
        <el-card 
          v-for="chunk in searchResults.chunks" 
          :key="chunk.chunk_id"
          class="result-card"
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <h4>{{ chunk.document_title }}</h4>
              <div class="scores">
                <el-tag size="small">总分: {{ chunk.final_score.toFixed(3) }}</el-tag>
                <el-tag size="small" type="warning">BM25: {{ chunk.bm25_score.toFixed(3) }}</el-tag>
                <el-tag size="small" type="success">TF-IDF: {{ chunk.tfidf_score.toFixed(3) }}</el-tag>
              </div>
            </div>
          </template>
          
          <div class="result-content">
            <p v-html="highlightText(chunk.content, searchMode === 'text' ? searchQuery : '')"></p>
          </div>
          
          <div class="result-footer">
            <span class="chunk-index">片段 #{{ chunk.chunk_index + 1 }}</span>
            <el-button size="small" type="text" @click="copyContent(chunk.content)">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="hasSearched && !loading">
      <el-empty description="没有找到相关结果" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  CopyDocument,
  User,
  Setting,
  ArrowDown,
  ArrowUp,
  SwitchButton,
  UploadFilled
} from '@element-plus/icons-vue'
import type { SearchResponse } from '@/types/api'
import { searchService } from '@/services/api'
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
  // 这里可以根据用户信息生成头像URL
  return `https://api.dicebear.com/7.x/initials/svg?seed=${authStore.user?.username}`
})

// 搜索相关状态
const searchMode = ref<'text' | 'document'>('text')
const searchQuery = ref('')
const loading = ref(false)
const hasSearched = ref(false)
const searchResults = ref<SearchResponse | null>(null)
const showAdvanced = ref(false)
const selectedFile = ref<File | null>(null)
const uploadRef = ref()
const isSearchCollapsed = ref(false)

// 搜索选项
const searchOptions = reactive({
  top_k: 10,
  bm25_weight: 0.6,
  tfidf_weight: 0.4
})

// 执行文本搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const response = await searchService.textSearch({
      query: searchQuery.value,
      ...searchOptions
    })
    searchResults.value = response
    
    if (response.chunks.length === 0) {
      ElMessage.info('没有找到相关结果')
    } else {
      // 有结果时自动收起搜索区域
      setTimeout(() => {
        isSearchCollapsed.value = true
      }, 500)
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请检查网络连接')
    searchResults.value = null
  } finally {
    loading.value = false
  }
}

// 处理文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  console.log('选择文件:', file.name)
}

// 处理文件移除
const handleFileRemove = () => {
  selectedFile.value = null
  console.log('移除文件')
}

// 执行文档匹配
const handleDocumentMatch = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要匹配的文档')
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const response = await searchService.fileSearch(selectedFile.value, searchOptions)
    searchResults.value = response
    
    if (response.chunks.length === 0) {
      ElMessage.info('没有找到匹配的文档内容')
    } else {
      ElMessage.success(`找到 ${response.total_documents} 个相关文档`)
      // 有结果时自动收起搜索区域
      setTimeout(() => {
        isSearchCollapsed.value = true
      }, 500)
    }
  } catch (error) {
    console.error('文档匹配失败:', error)
    ElMessage.error('文档匹配失败，请检查网络连接')
    searchResults.value = null
  } finally {
    loading.value = false
  }
}

// 切换搜索区域显示/隐藏
const toggleSearchArea = () => {
  isSearchCollapsed.value = !isSearchCollapsed.value
}

// 高亮搜索关键词
const highlightText = (text: string, query: string) => {
  if (!query.trim()) return text
  
  const keywords = query.trim().split(/\s+/)
  let highlighted = text
  
  keywords.forEach(keyword => {
    const regex = new RegExp(`(${keyword})`, 'gi')
    highlighted = highlighted.replace(regex, '<mark>$1</mark>')
  })
  
  return highlighted
}

// 复制内容
const copyContent = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 处理用户菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '退出确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.search-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 现代化导航栏 */
.modern-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  position: sticky;
  top: 0;
  z-index: 100;
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
}

.app-logo {
  color: var(--primary-color);
}

.app-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--gray-800);
  margin: 0;
}

.nav-menu {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  color: var(--gray-600);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-medium);
}

.nav-item:hover {
  background: var(--gray-100);
  color: var(--primary-color);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.user-section {
  position: relative;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-medium);
}

.user-avatar:hover {
  background: var(--gray-100);
}

.username {
  font-weight: 500;
  color: var(--gray-700);
}

.dropdown-icon {
  color: var(--gray-400);
  font-size: 0.875rem;
}

/* 搜索英雄区域 */
.search-hero {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-medium);
}

.search-hero.collapsed {
  padding: 1rem 2rem;
  min-height: 80px;
}

.search-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='7' cy='7' r='7'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  min-height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-content {
  text-align: center;
  color: white;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 3rem;
  opacity: 0.9;
  font-weight: 400;
}

.main-search-box {
  margin-bottom: 2rem;
}

.search-input-wrapper {
  display: flex;
  gap: 0.75rem;
  max-width: 600px;
  margin: 0 auto;
}

.main-search-input {
  flex: 1;
  font-size: 1.1rem;
}

.main-search-input :deep(.el-input__wrapper) {
  border-radius: 1rem;
  padding: 0 1.25rem;
  height: 56px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.search-icon {
  color: var(--primary-color);
  font-size: 1.25rem;
}

.search-button {
  height: 56px;
  padding: 0 2rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all var(--transition-medium);
}

.search-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.quick-options {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.option-group .el-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
}

.option-group .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.advanced-toggle {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all var(--transition-medium);
}

.advanced-toggle:hover {
  color: white;
}

/* 搜索模式选择器 */
.search-mode-selector {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.mode-group .el-radio-button__inner {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  font-weight: 500;
}

.mode-group .el-radio-button__inner:hover {
  background: rgba(255, 255, 255, 0.2);
}

.mode-group .el-radio-button.is-active .el-radio-button__inner {
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
  border-color: rgba(255, 255, 255, 0.9);
}

/* 文档匹配上传区 */
.document-match-box {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.document-upload {
  width: 100%;
}

.document-upload :deep(.el-upload) {
  width: 100%;
}

.document-upload :deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  transition: all var(--transition-medium);
}

.document-upload :deep(.el-upload-dragger:hover) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
}

.document-upload :deep(.el-upload-dragger .el-icon--upload) {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1rem;
}

.document-upload :deep(.el-upload__text) {
  color: white;
  font-size: 1.1rem;
  font-weight: 500;
}

.document-upload :deep(.el-upload__text em) {
  color: rgba(255, 255, 255, 0.9);
  font-style: normal;
  text-decoration: underline;
}

.document-upload :deep(.el-upload__tip) {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.document-upload :deep(.el-upload-list) {
  margin-top: 1rem;
}

.document-upload :deep(.el-upload-list__item) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  backdrop-filter: blur(10px);
}

.match-button {
  height: 56px;
  padding: 0 2rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all var(--transition-medium);
  align-self: flex-end; /* 右对齐 */
  width: fit-content;   /* 宽度自适应 */
}

.match-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.match-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 收起/展开按钮区域 */
.collapse-toggle {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.toggle-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
  border-radius: 1rem 1rem 0 0;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all var(--transition-medium);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.advanced-panel {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: white;
  text-align: center;
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
}

.control-item label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
}

.results-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.results-stats .el-tag {
  margin-left: 8px;
}

.results-list {
  space-y: 16px;
}

.result-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: #303133;
}

.scores .el-tag {
  margin-left: 8px;
}

.result-content {
  margin: 16px 0;
  line-height: 1.6;
}

.result-content :deep(mark) {
  background-color: #fff2cc;
  padding: 2px 4px;
  border-radius: 2px;
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 14px;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>