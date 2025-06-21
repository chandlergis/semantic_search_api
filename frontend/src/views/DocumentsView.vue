<template>
  <div class="documents-view">
    <AppHeader />

    <!-- 文档列表 -->
    <div class="content">
      <div class="content-header">
        <h2>文档管理</h2>
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
          </el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Document, 
  EditPen, 
  DocumentCopy,
} from '@element-plus/icons-vue';
import AppHeader from '@/components/AppHeader.vue';
import type { DocumentRead } from '@/types/api';
import { documentService } from '@/services/api';

const router = useRouter();

// 状态
const loading = ref(false);
const documents = ref<DocumentRead[]>([]);

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true;
  try {
    const response = await documentService.getDocuments();
    documents.value = response.documents;
  } catch (error) {
    console.error('获取文档列表失败:', error);
    ElMessage.error('获取文档列表失败');
  } finally {
    loading.value = false;
  }
};

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
    );

    await documentService.deleteDocument(document.id);
    ElMessage.success({
      message: '删除成功',
      duration: 1500
    });
    await fetchDocuments(); // 重新获取列表
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 在文档中搜索
const searchInDocument = (document: DocumentRead) => {
  router.push({
    path: '/search',
    query: { file_id: document.id }
  });
};

// 获取文件类型颜色
const getFileTypeColor = (fileType: string) => {
  const colors: Record<string, string> = {
    pdf: 'danger',
    docx: 'primary',
    doc: 'primary',
    txt: 'info',
    md: 'success'
  };
  return colors[fileType.toLowerCase()] || 'info';
};

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN');
};

// 组件挂载时获取数据
onMounted(() => {
  fetchDocuments();
});
</script>

<style scoped>
.documents-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  display: flex;
  flex-direction: column;
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
