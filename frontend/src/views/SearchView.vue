<template>
  <div class="search-view">
    <AppHeader />

    <div class="search-hero" :class="{ collapsed: isSearchCollapsed }">
      <div class="search-container">
        <div class="search-content animate-fadeInUp" v-show="!isSearchCollapsed">
          <h1 class="hero-title">
            智能查重，精准发现
          </h1>
          <p class="hero-subtitle">
            利用AI技术为您提供最相关的结果
          </p>
          
          <div class="search-mode-selector">
            <el-radio-group v-model="searchMode" size="large" class="mode-group">
              <el-radio-button label="text">文本搜索</el-radio-button>
              <el-radio-button label="document">文档匹配</el-radio-button>
            </el-radio-group>
          </div>

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

          <el-collapse-transition>
            <div v-if="showAdvanced" class="advanced-panel">
              <div class="panel-title">高级搜索选项</div>
              <div class="advanced-grid">
                <div class="control-item project-selector">
                  <label>限定项目范围</label>
                  <el-select
                    v-model="searchOptions.project_id"
                    placeholder="默认所有项目"
                    clearable
                    filterable
                    class="full-width-select"
                  >
                    <el-option
                      v-for="project in projects"
                      :key="project.id"
                      :label="project.name"
                      :value="project.id"
                    />
                  </el-select>
                </div>
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
                  <label>每文档分块数</label>
                  <el-slider
                    v-model="searchOptions.top_k_chunks"
                    :min="1"
                    :max="20"
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

      <div class="results-list">
        <el-card 
          v-for="doc in searchResults.documents" 
          :key="doc.document_id"
          class="result-card"
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <h4>{{ doc.document_title }}</h4>
              <div class="scores">
                <el-tag size="small" type="success">最高相似度: {{ (doc.max_score * 100).toFixed(1) }}%</el-tag>
                <el-tag size="small" type="info">平均相似度: {{ (doc.avg_score * 100).toFixed(1) }}%</el-tag>
              </div>
            </div>
          </template>
          
          <div class="chunk-scores">
            <div 
              v-for="chunk in doc.top_chunks" 
              :key="chunk.chunk_id"
              class="chunk-item"
            >
              <p class="chunk-content" v-html="highlightText(chunk.content, searchQuery)"></p>
              <div class="chunk-footer">
                <el-tag size="small">分块匹配度: {{ (chunk.final_score * 100).toFixed(1) }}%</el-tag>
                <el-tag size="small" type="warning">BM25: {{ chunk.bm25_score.toFixed(3) }}</el-tag>
                <el-tag size="small" type="danger">TF-IDF: {{ chunk.tfidf_score.toFixed(3) }}</el-tag>
                <el-button size="small" type="text" @click="copyContent(chunk.content)">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div class="empty-state" v-else-if="hasSearched && !loading">
      <el-empty description="没有找到相关结果" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  Search, 
  CopyDocument,
  Setting,
  ArrowDown,
  ArrowUp,
  UploadFilled
} from '@element-plus/icons-vue';
import type { SearchResponse, ProjectRead } from '@/types/api';
import { searchService, projectService } from '@/services/api';
import AppHeader from '@/components/AppHeader.vue';

// 搜索相关状态
const searchMode = ref<'text' | 'document'>('text');
const searchQuery = ref('');
const loading = ref(false);
const hasSearched = ref(false);
const searchResults = ref<SearchResponse | null>(null);
const showAdvanced = ref(false);
const selectedFile = ref<File | null>(null);
const uploadRef = ref();
const isSearchCollapsed = ref(false);
const projects = ref<ProjectRead[]>([]);
const route = useRoute();


// 搜索选项
const searchOptions = reactive({
  top_k: 10,
  top_k_chunks: 10, // 新增：控制每个文档显示的分块数量
  bm25_weight: 0.6,
  tfidf_weight: 0.4,
  project_id: undefined as string | undefined
});

// 执行文本搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容');
    return;
  }

  loading.value = true;
  hasSearched.value = true;

  try {
    const response = await searchService.textSearch({
      query: searchQuery.value,
      ...searchOptions,
      top_k_chunks: searchOptions.top_k_chunks // 确保传递分块数量参数
    });
    searchResults.value = response;
    
    if (response.documents.length === 0) {
      ElMessage.info('没有找到相关结果');
    } else {
      // 有结果时自动收起搜索区域
      setTimeout(() => {
        isSearchCollapsed.value = true;
      }, 500);
    }
  } catch (error) {
    console.error('搜索失败:', error);
    ElMessage.error('搜索失败，请检查网络连接');
    searchResults.value = null;
  } finally {
    loading.value = false;
  }
};

// 处理文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw;
  console.log('选择文件:', file.name);
};

// 处理文件移除
const handleFileRemove = () => {
  selectedFile.value = null;
  console.log('移除文件');
};

// 执行文档匹配
const handleDocumentMatch = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要匹配的文档');
    return;
  }

  loading.value = true;
  hasSearched.value = true;

  try {
    const response = await searchService.fileSearch(selectedFile.value, {
      ...searchOptions,
      top_k_chunks: searchOptions.top_k_chunks // 确保传递分块数量参数
    });
    searchResults.value = response;
    
    if (response.documents.length === 0) {
      ElMessage.info('没有找到匹配的文档内容');
    } else {
      ElMessage.success(`找到 ${response.total_documents} 个相关文档`);
      // 有结果时自动收起搜索区域
      setTimeout(() => {
        isSearchCollapsed.value = true;
      }, 500);
    }
  } catch (error) {
    console.error('文档匹配失败:', error);
    ElMessage.error('文档匹配失败，请检查网络连接');
    searchResults.value = null;
  } finally {
    loading.value = false;
  }
};

// 切换搜索区域显示/隐藏
const toggleSearchArea = () => {
  isSearchCollapsed.value = !isSearchCollapsed.value;
};

// 高亮搜索关键词
const highlightText = (text: string, query: string) => {
  if (!query || !query.trim()) return text;
  
  const keywords = query.trim().split(/\s+/);
  let highlighted = text;
  
  keywords.forEach(keyword => {
    const regex = new RegExp(`(${keyword})`, 'gi');
    highlighted = highlighted.replace(regex, '<mark>$1</mark>');
  });
  
  return highlighted;
};

// 复制内容
const copyContent = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success('内容已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败');
  }
};

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await projectService.getProjects({ page: 1, per_page: 100 });
    projects.value = response.projects;
  } catch (error) {
    console.error("获取项目列表失败:", error);
    ElMessage.error('获取项目列表失败');
  }
};

onMounted(() => {
  fetchProjects();
  const { project_id, project_name } = route.query;
  if (typeof project_id === 'string') {
    searchOptions.project_id = project_id;
    if (typeof project_name === 'string') {
      ElMessage.info(`已限定在项目 "${project_name}" 中搜索`);
    }
  } else {
    searchOptions.project_id = undefined;
  }
});

watch(() => route.query.project_id, (newProjectId) => {
  if (typeof newProjectId === 'string') {
    searchOptions.project_id = newProjectId;
  } else if (!newProjectId) {
    searchOptions.project_id = undefined;
  }
});
</script>

<style scoped>
/* General View Layout */
.search-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* Hero Search Area */
.search-hero {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
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
}

.search-content {
  text-align: center;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
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

/* Search Input & Buttons */
.main-search-box {
  width: 100%;
  max-width: 600px;
  margin-bottom: 2rem;
}

.search-input-wrapper {
  display: flex;
  gap: 0.75rem;
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
  color: #6366f1; /* Using a theme color */
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
  transition: all 0.3s ease-in-out;
}

.search-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

/* Quick Options & Advanced Toggle */
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
  transition: all 0.3s ease-in-out;
}

.advanced-toggle:hover {
  color: white;
}

/* Search Mode Selector */
.search-mode-selector {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.mode-group :deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  font-weight: 500;
  border-radius: 0.75rem;
}

.mode-group :deep(.el-radio-button:first-child .el-radio-button__inner) {
    border-top-left-radius: 0.75rem;
    border-bottom-left-radius: 0.75rem;
}

.mode-group :deep(.el-radio-button:last-child .el-radio-button__inner) {
    border-top-right-radius: 0.75rem;
    border-bottom-right-radius: 0.75rem;
}

.mode-group :deep(.el-radio-button__inner:hover) {
  background: rgba(255, 255, 255, 0.2);
}

.mode-group :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.9);
  color: #6366f1; /* Using a theme color */
  border-color: rgba(255, 255, 255, 0.9);
}

/* Document Match Area */
.document-match-box {
  max-width: 600px;
  width: 100%;
  margin: 0 auto 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.document-upload :deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.document-upload :deep(.el-upload-dragger:hover) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
}

.document-upload :deep(.el-icon--upload) {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
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

.document-upload :deep(.el-upload-list__item) {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  color: white;
  backdrop-filter: blur(10px);
  margin-top: 1rem;
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
  transition: all 0.3s ease-in-out;
}

.match-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.match-button:disabled {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  opacity: 0.6;
  cursor: not-allowed;
}


/* Advanced Panel - REDESIGNED */
.advanced-panel {
  width: 100%;
  max-width: 700px;
  margin: 1rem auto 0;
  padding: 2rem;
  border-radius: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}

.panel-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: white;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem 2rem;
}

.control-item {
  display: flex;
  flex-direction: column;
}

.control-item.project-selector {
  grid-column: 1 / -1;
}

.control-item label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.95);
  font-size: 0.9rem;
  text-align: left;
}

.full-width-select {
  width: 100%;
}

/* Deep Styling for Element Plus components in Advanced Panel */
.advanced-panel :deep(.el-select .el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: none !important;
  border-radius: 0.5rem;
}
.advanced-panel :deep(.el-select .el-input__inner) { color: white !important; }
.advanced-panel :deep(.el-slider__runway) { background-color: rgba(0, 0, 0, 0.2); height: 6px; border-radius: 3px; }
.advanced-panel :deep(.el-slider__bar) { background-color: white; height: 6px; border-radius: 3px;}
.advanced-panel :deep(.el-slider__button) { border: 2px solid white; background-color: #8b5cf6;}
.advanced-panel :deep(.el-input-number) { width: 110px; }
.advanced-panel :deep(.el-input-number .el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: none !important;
  padding: 0;
}
.advanced-panel :deep(.el-input-number .el-input__inner) { color: white !important; }
.advanced-panel :deep(.el-input-number__decrease),
.advanced-panel :deep(.el-input-number__increase) {
  background: transparent !important;
  color: white !important;
  font-weight: bold;
  border: none;
}
.advanced-panel :deep(.el-input-number__decrease) { border-right: 1px solid rgba(255, 255, 255, 0.3); }
.advanced-panel :deep(.el-input-number__increase) { border-left: 1px solid rgba(255, 255, 255, 0.3); }

/* Collapse/Expand Toggle */
.collapse-toggle {
  display: none;
}
.search-hero.collapsed .search-container {
    min-height: auto;
    display: block;
}
.search-hero.collapsed .collapse-toggle {
  display: block;
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}
.toggle-button {
  background: #f1f5f9;
  border: none;
  color: #334155;
  border-radius: 1rem;
  padding: 0.5rem 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
}
.toggle-button:hover {
  background: white;
  color: #6366f1;
  transform: translateY(-2px);
}

/* Results Area */
.results-container {
  flex: 1;
  padding: 40px 20px 20px;
  overflow-y: auto;
  background-color: #f1f5f9;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.results-stats .el-tag {
  margin-left: 8px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-card {
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
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

.chunk-item {
  padding: 12px;
  margin-bottom: 12px;
  border-radius: 4px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
}
.chunk-item:last-child {
  margin-bottom: 0;
}

.chunk-content {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #475569;
}
.chunk-content :deep(mark) {
    background-color: #fde047; /* yellow-300 */
    color: #422006; /* yellow-950 */
    border-radius: 2px;
    padding: 1px 2px;
}

.chunk-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
  padding-bottom: 20vh;
}
</style>

