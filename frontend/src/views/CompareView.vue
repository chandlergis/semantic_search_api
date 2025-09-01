<template>
  <div class="compare-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">文档对比</h1>
      <p class="page-description">上传或输入两个文档进行智能比对，系统将自动识别相似内容并高亮显示</p>
    </div>

    <!-- 输入区域 -->
    <div v-if="!result" class="input-area">
      <!-- 输入方式选择 -->
      <div class="input-panel">
        <div class="input-header">
          <span class="input-title">查重文档输入</span>
        </div>

        <!-- 文件上传模式 -->
        <div class="file-input-mode">
          <div class="upload-container">
            <div class="upload-column">
              <div class="upload-section">
                <h3>📄 原文文件</h3>
                <el-upload ref="uploadA" class="upload-area" drag :auto-upload="false" :show-file-list="false" :on-change="handleFileAChange" accept=".pdf,.docx,.doc,.txt,.md">
                  <div v-if="!fileData.file_a" class="upload-placeholder">
                    <el-icon class="el-icon--upload" size="48"><upload-filled /></el-icon>
                    <div class="el-upload__text">拖拽原文文件到此处或<em>点击上传</em></div>
                    <div class="el-upload__tip">支持 PDF, DOCX, DOC, TXT, MD 格式</div>
                  </div>
                  <div v-else class="file-info">
                    <el-icon size="32"><document /></el-icon>
                    <div class="file-details">
                      <span class="file-name">{{ fileData.file_a.name }}</span>
                      <span class="file-size">{{ formatFileSize(fileData.file_a.size) }}</span>
                    </div>
                    <el-button type="danger" size="small" @click.stop="removeFileA">删除</el-button>
                  </div>
                </el-upload>
              </div>
            </div>
            <div class="upload-divider">
              <div class="divider-text">VS</div>
            </div>
            <div class="upload-column">
              <div class="upload-section">
                <h3>🔍 待查重文件</h3>
                <el-upload ref="uploadB" class="upload-area" drag :auto-upload="false" :show-file-list="false" :on-change="handleFileBChange" accept=".pdf,.docx,.doc,.txt,.md">
                  <div v-if="!fileData.file_b" class="upload-placeholder">
                    <el-icon class="el-icon--upload" size="48"><upload-filled /></el-icon>
                    <div class="el-upload__text">拖拽待查重文件到此处或<em>点击上传</em></div>
                    <div class="el-upload__tip">支持 PDF, DOCX, DOC, TXT, MD 格式</div>
                  </div>
                  <div v-else class="file-info">
                    <el-icon size="32"><document /></el-icon>
                    <div class="file-details">
                      <span class="file-name">{{ fileData.file_b.name }}</span>
                      <span class="file-size">{{ formatFileSize(fileData.file_b.size) }}</span>
                    </div>
                    <el-button type="danger" size="small" @click.stop="removeFileB">删除</el-button>
                  </div>
                </el-upload>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 开始比对按钮 -->
      <div class="compare-action">
        <el-button type="primary" size="large" :loading="comparing" :disabled="!fileData.file_a || !fileData.file_b" @click="compareFiles">
          <el-icon><search /></el-icon>
          开始查重比对
        </el-button>
      </div>
    </div>

    <!-- 主内容区域 - 4/5 对比 + 1/5 结果 -->
    <div v-if="result" class="main-content">
      <!-- 文档对比视图 (4/5) -->
      <div class="compare-section">
        <div class="view-header">
          <span class="view-title">文档对比视图</span>
          <div class="view-controls">
            <el-switch
              v-model="showHighlighted"
              active-text="显示高亮"
              inactive-text="原始文档"
              size="small"
              style="margin-right: 16px;"
              :disabled="!hasHighlightedVersion"
            />
            <el-switch
              v-model="syncScrolling"
              active-text="同步滚动"
              inactive-text="独立滚动"
              size="small"
            />
          </div>
        </div>
        
        <div class="side-by-side-view">
          <el-row :gutter="20" style="height: 100%;">
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header">
                  <h4>{{ result.document_a.filename }}</h4>
                </div>
                <div class="document-preview" ref="documentPreviewA">
                  <!-- 先加载第一页获取PDF信息 -->
                  <VuePdfEmbed 
                    v-if="result && fileData.file_a_id && !pdfDocA"
                    :source="`/scdlsearch/api/compare/download/${fileData.file_a_id}?token=${authToken}`"
                    :page="1"
                    style="display: none;"
                    @loaded="(pdf) => handlePdfLoaded(pdf, 'a')"
                  />
                  <!-- 显示所有页面 -->
                  <div v-if="pdfDocA && !pdfLoading" class="pdf-viewer">
                    <VuePdfEmbed 
                      v-for="pageNum in pdfDocA.numPages"
                      :key="`pdf-a-page-${pageNum}`"
                      :source="`/scdlsearch/api/compare/download/${fileData.file_a_id}?token=${authToken}`"
                      :page="pageNum"
                      class="pdf-page"
                      @rendered="() => handlePdfPageRendered('a', pageNum)"
                    />
                  </div>
                  <div v-if="pdfLoading" class="pdf-loading">
                    <el-icon class="loading-icon"><Loading /></el-icon>
                    <span>加载中...</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header">
                  <h4>{{ result.document_b.filename }}</h4>
                  <div v-if="hasHighlightedVersion" class="header-controls">
                    <el-tag v-if="showHighlighted" type="warning" size="small">高亮版本</el-tag>
                    <el-tag v-else type="info" size="small">原始版本</el-tag>
                  </div>
                </div>
                <div class="document-preview" ref="documentPreviewB">
                  <!-- 先加载第一页获取PDF信息 -->
                  <VuePdfEmbed 
                    v-if="result && fileData.file_b_id && !pdfDocB"
                    :source="getPdfSource('b')"
                    :page="1"
                    style="display: none;"
                    @loaded="(pdf) => handlePdfLoaded(pdf, 'b')"
                  />
                  <!-- 显示所有页面 -->
                  <div v-if="pdfDocB && !pdfLoading" class="pdf-viewer">
                    <VuePdfEmbed 
                      v-for="pageNum in pdfDocB.numPages"
                      :key="`pdf-b-page-${pageNum}-${forceReloadTimestamp}`"
                      :source="getPdfSource('b')"
                      :page="pageNum"
                      class="pdf-page"
                      @rendered="() => handlePdfPageRendered('b', pageNum)"
                    />
                  </div>
                  <div v-if="pdfLoading" class="pdf-loading">
                    <el-icon class="loading-icon"><Loading /></el-icon>
                    <span>加载中...</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 比对结果 (1/5) -->
      <div class="result-section">
        <div class="summary-header">
          <span class="summary-title">比对结果分析</span>
          <el-button type="danger" plain size="small" @click="clearResult">
            <el-icon><CloseBold /></el-icon>
            <span>清空比对</span>
          </el-button>
        </div>
        
        <div class="summary-content">
          <div class="similarity-score">
            <el-progress type="circle" :percentage="Math.round(result.comparison.overall_similarity * 100)" :color="getSimilarityColor(result.comparison.overall_similarity)" :width="120" :stroke-width="10" />
            <div class="score-label">总体相似度</div>
          </div>
          
          <div class="statistics">
            <div class="stat-item">
              <span class="stat-label">匹配数</span>
              <span class="stat-value">{{ result.comparison.total_matches }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">高相似</span>
              <span class="stat-value high-sim">{{ result.comparison.high_similarity_matches }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">中相似</span>
              <span class="stat-value medium-sim">{{ result.comparison.medium_similarity_matches }}</span>
            </div>
          </div>
        </div>
        <div class="result-actions">
          <el-button type="primary" @click="downloadResult">
            <el-icon><Download /></el-icon>
            <span>导出比对报告</span>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, onBeforeUnmount } from 'vue'
import { ElMessage, ElLoading, type UploadFile } from 'element-plus'
import { Document, UploadFilled, Search, CloseBold, Download, Loading } from '@element-plus/icons-vue'
import { compareService } from '@/services/api'
import type {
  CompareResponse,
  CompareFilesRequest
} from '@/types/api'
import VuePdfEmbed from 'vue-pdf-embed'
import '@/assets/styles/pdf-embed.css'
import { PDFSyncScroller } from '@/utils/PDFSyncScroller'

// 响应式数据
const comparing = ref(false)

// 配置数据
const config = reactive({
  similarity_threshold_high: 0.9,
  similarity_threshold_medium: 0.7,
  chunk_size: 300
})


// 文件上传数据
const fileData = reactive({
  file_a: null as File | null,
  file_b: null as File | null,
  file_a_id: '',
  file_b_id: ''
})

// PDF加载状态
const pdfLoading = ref(false)
const pdfLoadCount = ref(0)
const pdfDocA = ref<any>(null)
const pdfDocB = ref<any>(null)

// 同步滚动控制
const syncScrolling = ref(true)
let pdfSyncScroller: PDFSyncScroller | null = null

// 高亮版本控制
const showHighlighted = ref(true)
const hasHighlightedVersion = ref(false)
const forceReloadTimestamp = ref(0)

// PDF容器引用
const documentPreviewA = ref<HTMLElement>()
const documentPreviewB = ref<HTMLElement>()

// PDF渲染状态跟踪
const pdfRenderingStatus = reactive({
  a: { rendering: false, rendered: false, pagesRendered: 0 },
  b: { rendering: false, rendered: false, pagesRendered: 0 }
})

// 比对结果
const result = ref<CompareResponse | null>(null)


const handlePdfLoaded = (pdf: any, docKey: 'a' | 'b') => {
  console.log(`PDF ${docKey} 加载完成，页数:`, pdf.numPages)
  if (docKey === 'a') {
    pdfDocA.value = pdf
  } else {
    pdfDocB.value = pdf
  }
  pdfLoadCount.value++
  
  // 重置渲染计数
  pdfRenderingStatus[docKey].pagesRendered = 0
  pdfRenderingStatus[docKey].rendered = false
  
  if (pdfLoadCount.value >= 2) {
    pdfLoading.value = false
    console.log('所有PDF加载完成，开始渲染页面')
  }
}

// 处理PDF页面渲染事件
const handlePdfPageRendered = (docKey: 'a' | 'b', pageNum: number) => {
  console.log(`PDF ${docKey} 第${pageNum}页渲染完成`)
  pdfRenderingStatus[docKey].pagesRendered++
  
  const totalPages = docKey === 'a' ? pdfDocA.value?.numPages : pdfDocB.value?.numPages
  if (pdfRenderingStatus[docKey].pagesRendered >= totalPages) {
    pdfRenderingStatus[docKey].rendered = true
    console.log(`PDF ${docKey} 所有页面渲染完成`)
  }
  
  // 检查是否两个PDF都渲染完成
  const allRendered = pdfRenderingStatus.a.rendered && pdfRenderingStatus.b.rendered
  if (allRendered) {
    console.log('所有PDF渲染完成，设置同步滚动')
    // 延迟一点确保DOM完全渲染
    setTimeout(() => {
      if (syncScrolling.value) {
        setupSyncScrolling()
      }
    }, 300)
  }
}

// DOM引用
const uploadA = ref()
const uploadB = ref()

// 监听同步滚动开关变化
watch(syncScrolling, (newValue) => {
  if (newValue && pdfLoadCount.value >= 2) {
    // 启用同步滚动
    setupSyncScrolling()
  } else {
    // 禁用同步滚动
    removeSyncScrolling()
  }
})

// 监听高亮模式切换
watch(showHighlighted, () => {
  // 切换高亮模式时重新加载PDF B
  if (hasHighlightedVersion.value) {
    console.log(`切换到${showHighlighted.value ? '高亮' : '原始'}模式`)
    // 重置PDF B的加载状态
    pdfDocB.value = null
    pdfRenderingStatus.b = { rendering: false, rendered: false, pagesRendered: 0 }
    pdfLoadCount.value = 1  // 保持A文档已加载
    
    // 强制重新加载PDF - 通过改变时间戳触发重新渲染
    forceReloadTimestamp.value = Date.now()
  }
})

// 同步滚动功能
const setupSyncScrolling = () => {
  console.log('设置PDF同步滚动')
  
  const containerA = documentPreviewA.value
  const containerB = documentPreviewB.value

  if (containerA && containerB) {
    try {
      removeSyncScrolling() // 先清除现有的滚动监听器
      pdfSyncScroller = new PDFSyncScroller(containerA, containerB)
      console.log('PDF同步滚动设置成功')
    } catch (error) {
      console.error('设置PDF同步滚动失败:', error)
    }
  } else {
    console.warn('无法找到PDF容器元素')
  }
}

// 移除同步滚动
const removeSyncScrolling = () => {
  if (pdfSyncScroller) {
    pdfSyncScroller.destroy()
    pdfSyncScroller = null
  }
}


// 认证token
const authToken = ref(localStorage.getItem('auth_token') || '')

// 获取PDF源URL
const getPdfSource = (docKey: 'a' | 'b') => {
  const timestamp = Date.now() + forceReloadTimestamp.value
  if (docKey === 'a') {
    const url = `/scdlsearch/api/compare/download/${fileData.file_a_id}?token=${authToken.value}&t=${timestamp}`
    console.log('文档A URL:', url)
    return url
  } else {
    // 文档B：根据高亮模式选择不同URL
    if (showHighlighted.value && hasHighlightedVersion.value) {
      const url = `/scdlsearch/api/compare/download/${fileData.file_b_id}/highlighted?token=${authToken.value}&t=${timestamp}`
      console.log('文档B高亮URL:', url)
      return url
    } else {
      const url = `/scdlsearch/api/compare/download/${fileData.file_b_id}?token=${authToken.value}&t=${timestamp}`
      console.log('文档B原始URL:', url)
      return url
    }
  }
}

const handleFileAChange = (file: UploadFile) => {
  fileData.file_a = file.raw || null
}

const handleFileBChange = (file: UploadFile) => {
  fileData.file_b = file.raw || null
}

const removeFileA = () => {
  fileData.file_a = null
  uploadA.value?.clearFiles()
}

const removeFileB = () => {
  fileData.file_b = null
  uploadB.value?.clearFiles()
}


const compareFiles = async () => {
  if (!fileData.file_a || !fileData.file_b) {
    ElMessage.warning('请选择两个文件')
    return
  }

  const loading = ElLoading.service({
    lock: true,
    text: '正在上传并比对文档...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  try {
    comparing.value = true
    
    loading.setText('正在上传文档A...')
    const uploadAResult = await compareService.uploadFile(fileData.file_a as File)
    fileData.file_a_id = uploadAResult.file_id
    
    loading.setText('正在上传文档B...')
    const uploadBResult = await compareService.uploadFile(fileData.file_b as File)
    fileData.file_b_id = uploadBResult.file_id
    
    loading.setText('正在比对文档...')
    const request: CompareFilesRequest = {
      file_a_id: fileData.file_a_id,
      file_b_id: fileData.file_b_id,
      similarity_threshold_high: config.similarity_threshold_high,
      similarity_threshold_medium: config.similarity_threshold_medium,
      chunk_size: config.chunk_size
    }

    console.log('开始调用compareFiles API', request)
    result.value = await compareService.compareFiles(request)
    console.log('compareFiles API调用成功', result.value)
    
    // 检查是否有高亮版本
    console.log('完整比对结果:', JSON.stringify(result.value, null, 2))
    console.log('metadata:', result.value.metadata)
    console.log('highlighted_files:', result.value.metadata?.highlighted_files)
    
    if (result.value.metadata?.highlighted_files?.file_b) {
      hasHighlightedVersion.value = true
      showHighlighted.value = true
      console.log('检测到高亮版本PDF:', result.value.metadata.highlighted_files.file_b)
    } else {
      hasHighlightedVersion.value = false
      showHighlighted.value = false
      console.log('未检测到高亮版本')
    }
    
    ElMessage.success('文档比对完成')
    
  } catch (error: any) {
    console.error('文档比对失败:', error)
    ElMessage.error(error.response?.data?.detail || '文档比对失败')
  } finally {
    comparing.value = false
    loading.close()
  }
}

const getSimilarityColor = (similarity: number) => {
  if (similarity >= 0.9) return '#f56c6c'  // 红色 - 高
  if (similarity >= 0.7) return '#e6a23c'  // 橙色 - 中
  return '#67c23a'  // 绿色 - 低
}


const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const downloadResult = () => {
  if (!result.value) return
  
  const content = {
    summary: {
      overall_similarity: result.value.comparison.overall_similarity,
      total_matches: result.value.comparison.total_matches,
      high_similarity_matches: result.value.comparison.high_similarity_matches,
      medium_similarity_matches: result.value.comparison.medium_similarity_matches
    },
    documents: {
      document_a: {
        filename: result.value.document_a.filename,
        chunks_count: result.value.document_a.chunks_count
      },
      document_b: {
        filename: result.value.document_b.filename,
        chunks_count: result.value.document_b.chunks_count
      }
    },
    match_links: result.value.comparison.match_links,
    metadata: result.value.metadata
  }
  
  const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `文档比对结果_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success('结果已导出')
}

const clearResult = () => {
  result.value = null
  pdfLoadCount.value = 0
  pdfDocA.value = null
  pdfDocB.value = null
  
  // 重置渲染状态
  pdfRenderingStatus.a = { rendering: false, rendered: false, pagesRendered: 0 }
  pdfRenderingStatus.b = { rendering: false, rendered: false, pagesRendered: 0 }
  
  // 重置高亮状态
  hasHighlightedVersion.value = false
  showHighlighted.value = false
  
  
  // 移除同步滚动监听器
  removeSyncScrolling()
  
  ElMessage.info('已清除比对结果')
}

// 生命周期
onMounted(() => {
  // 可以在这里初始化一些数据
})

onBeforeUnmount(() => {
  removeSyncScrolling()
})
</script>

<style scoped>
.compare-container {
  padding: 24px;
  background: #ffffff;
  color: #333333;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px); /* Adjust based on actual navbar height */
}

.page-header {
  margin-bottom: 24px;
  flex-shrink: 0;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #333333;
}

.page-description {
  margin: 0;
  color: #666666;
  font-size: 14px;
}

.input-area {
  flex-shrink: 0;
}

.input-panel {
  margin-bottom: 24px;
  background: #fafafa;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 20px;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e6e6e6;
}

.input-title {
  font-size: 16px;
  color: #333333;
}

.text-input-mode,
.file-input-mode {
  display: flex;
  flex-direction: column;
}

.upload-container {
  display: flex;
  gap: 32px;
  align-items: stretch;
  min-height: 350px;
}

.upload-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.upload-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 0 16px;
}

.divider-text {
  background: #409eff;
  color: white;
  padding: 8px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.input-section {
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333333;
}

.upload-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333333;
}

.upload-area {
  width: 100%;
  flex: 1;
  display: flex;
}

.upload-area :deep(.el-upload-dragger) {
  background: #ffffff;
  border: 2px dashed #d0d0d0;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f8faff;
}

.upload-placeholder,
.file-info {
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.file-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.file-name {
  font-weight: 500;
  color: #333;
  word-break: break-all;
  max-width: 200px;
}

.file-size {
  font-size: 12px;
  color: #666;
}

.compare-action {
  text-align: center;
  margin: 24px 0;
}

/* 主内容布局 */
.main-content {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0; /* Crucial for flexbox scrolling */
  margin-top: 24px;
}

.compare-section {
  flex: 4;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fafafa;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 20px;
}

.result-section {
  flex: 1;
  min-width: 280px;
  max-width: 320px;
  background: #fafafa;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.view-header, .summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  padding-bottom: 12px;
  border-bottom: 1px solid #e6e6e6;
  flex-shrink: 0;
}

.view-title, .summary-title {
  font-size: 16px;
  color: #333333;
}

.side-by-side-view {
  flex: 1;
  min-height: 0;
  padding-top: 20px;
}

.document-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
}

.document-header {
  padding: 12px 16px;
  background: #f8f8f8;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.document-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333333;
  font-weight: 600;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chunk-count {
  font-size: 12px;
  color: #666666;
  background: #e8e8e8;
  padding: 2px 8px;
  border-radius: 10px;
}

.document-preview {
  flex: 1;
  position: relative;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.pdf-viewer {
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  display: block;
  padding: 10px;
  background: #f5f5f5;
}

.pdf-page {
  display: block;
  margin: 0 auto 20px auto;
  max-width: 100%;
}

.pdf-page:last-child {
  margin-bottom: 10px;
}

.pdf-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px; /* 减少最小高度 */
  color: #666;
}

.loading-icon {
  font-size: 32px;
  margin-bottom: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.html-content {
  padding: 20px;
  line-height: 1.6;
  white-space: pre-wrap;
  font-family: 'Microsoft YaHei', sans-serif;
  font-size: 14px;
}

.html-content .highlight-high {
  background-color: #ffcccc;
  border: 1px solid #ff6666;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
}

.html-content .highlight-medium {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
}

.html-content .highlight-low {
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
}

.html-content .highlight-high:hover,
.html-content .highlight-medium:hover,
.html-content .highlight-low:hover {
  opacity: 0.8;
}

.document-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  overflow-y: auto;
  line-height: 1.8;
  font-size: 14px;
  color: #333333;
  font-family: 'SimSun', '宋体', serif;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.similarity-score {
  text-align: center;
}

.score-label {
  margin-top: 12px;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.statistics {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  padding: 0 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #eef;
  font-size: 14px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  font-family: monospace;
}

.stat-value.high-sim { color: #f56c6c; }
.stat-value.medium-sim { color: #e6a23c; }

.stat-label {
  color: #333;
  font-weight: 500;
}

:deep(.highlight-high) {
  background-color: rgba(245, 108, 108, 0.2);
}

:deep(.highlight-medium) {
  background-color: rgba(230, 162, 60, 0.2);
}

.result-actions {
  margin-top: auto; /* Pushes button to the bottom */
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}

.result-actions .el-button {
  width: 100%;
  height: 40px;
  font-size: 15px;
}

.summary-header .el-button .el-icon {
  margin-right: 4px;
}

</style>
