<template>
  <div class="compare-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">文档对比</h1>
      <p class="page-description">上传或输入两个文档进行智能比对，系统将自动识别相似内容并高亮显示</p>
    </div>

    <!-- 输入区域 -->
    <div v-if="!result" class="input-area">
      <div class="input-panel">
        <div class="input-header">
          <span class="input-title">查重文档输入</span>
        </div>
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
      <div class="compare-action">
        <el-button type="primary" size="large" :loading="comparing" :disabled="!fileData.file_a || !fileData.file_b" @click="compareFiles">
          <el-icon><search /></el-icon>
          开始查重比对
        </el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div v-if="result" class="main-content">
      <div class="compare-section">
        <div class="view-header">
          <span class="view-title">文档对比视图</span>
          <div class="view-controls" v-if="displayMode === 'pdf'">
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
        
        <!-- PDF 模式 -->
        <div v-if="displayMode === 'pdf'" class="side-by-side-view">
          <el-row :gutter="20" style="height: 100%;">
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header">
                  <h4>{{ result.document_a.filename }}</h4>
                </div>
                <div class="document-preview" ref="documentPreviewA">
                  <VuePdfEmbed 
                    v-if="result && fileData.file_a_id && !pdfDocA"
                    :source="getPdfSource('a')"
                    :page="1"
                    style="display: none;"
                    @loaded="(pdf) => handlePdfLoaded(pdf, 'a')"
                  />
                  <div v-if="pdfDocA && !pdfLoading" class="pdf-viewer">
                    <VuePdfEmbed 
                      v-for="pageNum in pdfDocA.numPages"
                      :key="`pdf-a-page-${pageNum}`"
                      :source="getPdfSource('a')"
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
                  <VuePdfEmbed 
                    v-if="result && fileData.file_b_id && !pdfDocB"
                    :source="getPdfSource('b')"
                    :page="1"
                    style="display: none;"
                    @loaded="(pdf) => handlePdfLoaded(pdf, 'b')"
                  />
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

        <!-- HTML 模式 -->
        <div v-else-if="displayMode === 'html'" class="side-by-side-view html-view">
          <el-row :gutter="20" style="height: 100%;">
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header"><h4>{{ result.document_a.filename }}</h4></div>
                <div class="document-content" v-html="result.document_a.html_content"></div>
              </div>
            </el-col>
            <el-col :span="12" style="height: 100%; display: flex; flex-direction: column;">
              <div class="document-panel">
                <div class="document-header"><h4>{{ result.document_b.filename }}</h4></div>
                <div class="document-content" v-html="result.document_b.html_content"></div>
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
import { ref, reactive, watch, onBeforeUnmount } from 'vue';
import { ElMessage, ElLoading, type UploadFile } from 'element-plus';
import { Document, UploadFilled, Search, CloseBold, Download, Loading } from '@element-plus/icons-vue';
import { compareService } from '@/services/api';
import type { CompareResponse, CompareFilesRequest } from '@/types/api';
import VuePdfEmbed from 'vue-pdf-embed';
import '@/assets/styles/pdf-embed.css';
import { PDFSyncScroller } from '@/utils/PDFSyncScroller';

const displayMode = ref<'pdf' | 'html'>('pdf');
const comparing = ref(false);
const config = reactive({
  similarity_threshold_high: 0.9,
  similarity_threshold_medium: 0.7,
  chunk_size: 300
});

const fileData = reactive({
  file_a: null as File | null,
  file_b: null as File | null,
  file_a_id: '',
  file_b_id: ''
});

const pdfLoading = ref(false);
const pdfLoadCount = ref(0);
const pdfDocA = ref<any>(null);
const pdfDocB = ref<any>(null);

const syncScrolling = ref(true);
let pdfSyncScroller: PDFSyncScroller | null = null;

const showHighlighted = ref(true);
const hasHighlightedVersion = ref(false);
const forceReloadTimestamp = ref(0);

const documentPreviewA = ref<HTMLElement>();
const documentPreviewB = ref<HTMLElement>();

const pdfRenderingStatus = reactive({
  a: { rendered: false, pagesRendered: 0 },
  b: { rendered: false, pagesRendered: 0 }
});

const result = ref<CompareResponse | null>(null);

const uploadA = ref();
const uploadB = ref();

const authToken = ref(localStorage.getItem('auth_token') || '');

const handlePdfLoaded = (pdf: any, docKey: 'a' | 'b') => {
  if (docKey === 'a') pdfDocA.value = pdf;
  else pdfDocB.value = pdf;
  pdfLoadCount.value++;
  pdfRenderingStatus[docKey].pagesRendered = 0;
  pdfRenderingStatus[docKey].rendered = false;
  if (pdfLoadCount.value >= 2) pdfLoading.value = false;
};

const handlePdfPageRendered = (docKey: 'a' | 'b', pageNum: number) => {
  console.log(`PDF ${docKey} page ${pageNum} rendered.`);
  pdfRenderingStatus[docKey].pagesRendered++;
  const totalPages = docKey === 'a' ? pdfDocA.value?.numPages : pdfDocB.value?.numPages;
  if (pdfRenderingStatus[docKey].pagesRendered >= totalPages) {
    pdfRenderingStatus[docKey].rendered = true;
  }
  if (pdfRenderingStatus.a.rendered && pdfRenderingStatus.b.rendered) {
    setTimeout(() => {
      if (syncScrolling.value) setupSyncScrolling();
    }, 300);
  }
};

watch(syncScrolling, (newValue) => {
  if (newValue) setupSyncScrolling();
  else removeSyncScrolling();
});

watch(showHighlighted, () => {
  if (hasHighlightedVersion.value) {
    pdfDocB.value = null;
    pdfRenderingStatus.b = { rendered: false, pagesRendered: 0 };
    pdfLoadCount.value = 1;
    forceReloadTimestamp.value = Date.now();
  }
});

const setupSyncScrolling = () => {
  const containerA = documentPreviewA.value;
  const containerB = documentPreviewB.value;
  if (containerA && containerB) {
    removeSyncScrolling();
    pdfSyncScroller = new PDFSyncScroller(containerA, containerB);
  }
};

const removeSyncScrolling = () => {
  if (pdfSyncScroller) {
    pdfSyncScroller.destroy();
    pdfSyncScroller = null;
  }
};

const getPdfSource = (docKey: 'a' | 'b') => {
  const timestamp = Date.now() + forceReloadTimestamp.value;
  if (docKey === 'a') return `/scdlsearch/api/compare/download/${fileData.file_a_id}?token=${authToken.value}&t=${timestamp}`;
  
  if (showHighlighted.value && hasHighlightedVersion.value) {
    return `/scdlsearch/api/compare/download/${fileData.file_b_id}/highlighted?token=${authToken.value}&t=${timestamp}`;
  }
  return `/scdlsearch/api/compare/download/${fileData.file_b_id}?token=${authToken.value}&t=${timestamp}`;
};

const handleFileAChange = (file: UploadFile) => { fileData.file_a = file.raw || null; };
const handleFileBChange = (file: UploadFile) => { fileData.file_b = file.raw || null; };
const removeFileA = () => { fileData.file_a = null; uploadA.value?.clearFiles(); };
const removeFileB = () => { fileData.file_b = null; uploadB.value?.clearFiles(); };

const compareFiles = async () => {
  if (!fileData.file_a || !fileData.file_b) return ElMessage.warning('请选择两个文件');

  const loading = ElLoading.service({ lock: true, text: '正在上传并比对文档...' });

  try {
    comparing.value = true;
    loading.setText('正在上传文档A...');
    const uploadAResult = await compareService.uploadFile(fileData.file_a as File);
    fileData.file_a_id = uploadAResult.file_id;
    
    loading.setText('正在上传文档B...');
    const uploadBResult = await compareService.uploadFile(fileData.file_b as File);
    fileData.file_b_id = uploadBResult.file_id;
    
    loading.setText('正在比对文档...');
    const request: CompareFilesRequest = {
      file_a_id: fileData.file_a_id,
      file_b_id: fileData.file_b_id,
      similarity_threshold_high: config.similarity_threshold_high,
      similarity_threshold_medium: config.similarity_threshold_medium,
      chunk_size: config.chunk_size
    };
    result.value = await compareService.compareFiles(request);
    
    displayMode.value = result.value.metadata?.display_mode || 'pdf';

    if (displayMode.value === 'pdf') {
      pdfLoading.value = true;
      if (result.value.metadata?.highlighted_files?.file_b) {
        hasHighlightedVersion.value = true;
        showHighlighted.value = true;
      } else {
        hasHighlightedVersion.value = false;
        showHighlighted.value = false;
      }
    }
    
    ElMessage.success('文档比对完成');
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '文档比对失败');
  } finally {
    comparing.value = false;
    loading.close();
  }
};

const getSimilarityColor = (similarity: number) => {
  if (similarity >= 0.9) return '#f56c6c';
  if (similarity >= 0.7) return '#e6a23c';
  return '#67c23a';
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const downloadResult = () => {
  if (!result.value) return;
  const content = { ...result.value };
  const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `比对结果_${result.value.document_a.filename}_vs_${result.value.document_b.filename}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

const clearResult = () => {
  result.value = null;
  displayMode.value = 'pdf';
  pdfLoadCount.value = 0;
  pdfDocA.value = null;
  pdfDocB.value = null;
  hasHighlightedVersion.value = false;
  showHighlighted.value = false;
  removeSyncScrolling();
  ElMessage.info('已清除比对结果');
};

onBeforeUnmount(() => { removeSyncScrolling(); });

</script>

<style scoped>
.compare-container {
  padding: 24px;
  background: #ffffff;
  color: #333333;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px); 
}

.page-header {
  margin-bottom: 24px;
  flex-shrink: 0;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
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
}

.file-input-mode {
  display: flex;
  flex-direction: column;
}

.upload-container {
  display: flex;
  gap: 32px;
  align-items: stretch;
  min-height: 250px;
}

.upload-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.upload-divider {
  display: flex;
  align-items: center;
  justify-content: center;
}

.divider-text {
  background: #409eff;
  color: white;
  padding: 8px 12px;
  border-radius: 20px;
  font-weight: bold;
}

.upload-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.upload-area {
  width: 100%;
  flex: 1;
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
}

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
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: #666;
}

.compare-action {
  text-align: center;
  margin: 24px 0;
}

.main-content {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0;
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
}

.view-header, .summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #e6e6e6;
  flex-shrink: 0;
}

.view-title, .summary-title {
  font-size: 16px;
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
  font-weight: 600;
}

.document-preview, .html-view .document-content {
  flex: 1;
  position: relative;
  min-height: 0;
  overflow-y: auto;
}

.pdf-viewer {
  padding: 10px;
  background: #f5f5f5;
}

.pdf-page {
  margin: 0 auto 20px auto;
}

.html-view .document-content {
  padding: 16px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.html-view .document-content :deep(.highlight-high) {
  background-color: rgba(255, 182, 193, 0.6);
}

.html-view .document-content :deep(.highlight-medium) {
  background-color: rgba(255, 255, 153, 0.7);
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
  font-size: 16px;
  font-weight: 500;
}

.statistics {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #eef;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.stat-value.high-sim { color: #f56c6c; }
.stat-value.medium-sim { color: #e6a23c; }

.result-actions {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}

.result-actions .el-button {
  width: 100%;
}

.pdf-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
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
</style>