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
          <el-radio-group v-model="inputMode" size="small">
            <el-radio-button label="text">文本输入</el-radio-button>
            <el-radio-button label="file">文件上传</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 文本输入模式 -->
        <div v-if="inputMode === 'text'" class="text-input-mode">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="input-section">
                <div class="section-header">
                  <h3>原文内容</h3>
                  <el-input v-model="textData.filename_a" placeholder="原文标题" size="small" style="width: 200px;" />
                </div>
                <el-input v-model="textData.text_a" type="textarea" placeholder="请输入或粘贴原文内容..." :rows="15" :maxlength="50000" show-word-limit resize="none" />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="input-section">
                <div class="section-header">
                  <h3>待查重内容</h3>
                  <el-input v-model="textData.filename_b" placeholder="待查重标题" size="small" style="width: 200px;" />
                </div>
                <el-input v-model="textData.text_b" type="textarea" placeholder="请输入或粘贴待查重内容..." :rows="15" :maxlength="50000" show-word-limit resize="none" />
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 文件上传模式 -->
        <div v-if="inputMode === 'file'" class="file-input-mode">
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
        <el-button v-if="inputMode === 'text'" type="primary" size="large" :loading="comparing" :disabled="!textData.text_a || !textData.text_b" @click="compareTexts">
          <el-icon><search /></el-icon>
          开始查重比对
        </el-button>
        <el-button v-else type="primary" size="large" :loading="comparing" :disabled="!fileData.file_a || !fileData.file_b" @click="compareFiles">
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
            <el-switch v-model="syncScroll" active-text="同步滚动" />
          </div>
        </div>
        
        <div class="side-by-side-view">
          <el-row :gutter="20" style="height: 100%;">
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header">
                  <h4>{{ result.document_a.filename }}</h4>
                  <span class="chunk-count">{{ result.document_a.chunks_count }} 段</span>
                </div>
                <div class="document-preview">
                  <div ref="documentA" class="document-content" v-html="result.document_a.html_content" @scroll="onScrollA" />
                </div>
              </div>
            </el-col>
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header">
                  <h4>{{ result.document_b.filename }}</h4>
                  <span class="chunk-count">{{ result.document_b.chunks_count }} 段</span>
                </div>
                <div class="document-preview">
                  <div ref="documentB" class="document-content" v-html="result.document_b.html_content" @scroll="onScrollB" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElLoading, type UploadFile } from 'element-plus'
import { Document, UploadFilled, Search, CloseBold, Download } from '@element-plus/icons-vue'
import { compareService } from '@/services/api'
import type {
  CompareRequest,
  CompareResponse,
  CompareFilesRequest
} from '@/types/api'

// 响应式数据
const inputMode = ref<'text' | 'file'>('text')
const comparing = ref(false)
const syncScroll = ref(true)

// 配置数据
const config = reactive({
  similarity_threshold_high: 0.9,
  similarity_threshold_medium: 0.7,
  chunk_size: 300
})

// 文本输入数据
const textData = reactive({
  text_a: '',
  text_b: '',
  filename_a: '文档A',
  filename_b: '文档B'
})

// 文件上传数据
const fileData = reactive({
  file_a: null as File | null,
  file_b: null as File | null,
  file_a_id: '',
  file_b_id: ''
})

// 比对结果
const result = ref<CompareResponse | null>(null)

// DOM引用
const documentA = ref<HTMLElement>()
const documentB = ref<HTMLElement>()
const uploadA = ref()
const uploadB = ref()


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

const compareTexts = async () => {
  if (!textData.text_a || !textData.text_b) {
    ElMessage.warning('请输入两个文档的内容')
    return
  }

  const loading = ElLoading.service({
    lock: true,
    text: '正在比对文档...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  try {
    comparing.value = true
    
    const request: CompareRequest = {
      text_a: textData.text_a,
      text_b: textData.text_b,
      filename_a: textData.filename_a || '文档A',
      filename_b: textData.filename_b || '文档B',
      similarity_threshold_high: config.similarity_threshold_high,
      similarity_threshold_medium: config.similarity_threshold_medium,
      chunk_size: config.chunk_size
    }

    result.value = await compareService.compareTexts(request)
    ElMessage.success('文档比对完成')
    
  } catch (error: any) {
    console.error('文档比对失败:', error)
    ElMessage.error(error.response?.data?.detail || '文档比对失败')
  } finally {
    comparing.value = false
    loading.close()
  }
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

    result.value = await compareService.compareFiles(request)
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

const onScrollA = () => {
  if (syncScroll.value && documentB.value && documentA.value) {
    documentB.value.scrollTop = documentA.value.scrollTop
  }
}

const onScrollB = () => {
  if (syncScroll.value && documentA.value && documentB.value) {
    documentA.value.scrollTop = documentB.value.scrollTop
  }
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
  ElMessage.info('已清除比对结果')
}

// 生命周期
onMounted(() => {
  // 可以在这里初始化一些数据
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

.document-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333333;
  font-weight: 600;
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
