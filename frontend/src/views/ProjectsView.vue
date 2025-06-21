<template>
  <div class="projects-view">
    <AppHeader />

    <!-- 项目内容 -->
    <div class="content">
      <div class="content-header">
        <h2>项目管理</h2>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建项目
        </el-button>
      </div>

      <div class="projects-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <!-- 项目网格 -->
        <div v-else-if="projects.length > 0" class="projects-grid">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="project-card card-hover"
            @click="viewProject(project)"
          >
            <div class="card-header">
              <div class="project-info">
                <h3 class="project-name">{{ project.name }}</h3>
                <p class="project-description">{{ project.description || '暂无描述' }}</p>
              </div>
              <el-dropdown @command="(cmd: string) => handleProjectCommand(cmd, project)" trigger="click" @click.stop>
                <el-button type="text" class="more-btn">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">
                      <el-icon><Edit /></el-icon>
                      编辑
                    </el-dropdown-item>
                    <el-dropdown-item command="search">
                      <el-icon><Search /></el-icon>
                      在此项目中搜索
                    </el-dropdown-item>
                    <el-dropdown-item divided command="delete">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <div class="card-stats">
              <div class="stat-item">
                <el-icon><Document /></el-icon>
                <span>{{ project.document_count }} 个文档</span>
              </div>
              <div class="stat-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatDate(project.updated_at) }}</span>
              </div>
            </div>

            <div class="card-footer">
              <el-tag size="small" type="info">
                {{ formatDate(project.created_at) }} 创建
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无项目">
            <el-button type="primary" @click="showCreateDialog = true">
              立即创建
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalProjects > pageSize" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalProjects"
          layout="prev, pager, next, jumper"
          @current-change="fetchProjects"
        />
      </div>
    </div>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '创建项目'"
      width="500px"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectRules"
        label-width="80px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="projectForm.name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveProject"
            :loading="saving"
          >
            {{ editingProject ? '保存' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { 
  Search, 
  Document, 
  Plus,
  MoreFilled,
  Edit,
  Delete,
  Clock
} from '@element-plus/icons-vue';
import AppHeader from '@/components/AppHeader.vue';
import { projectService } from '@/services/api';
import type { ProjectRead, ProjectCreate, ProjectWithDocuments } from '@/types/api';

const router = useRouter();

// 项目管理
const loading = ref(false);
const saving = ref(false);
const projects = ref<ProjectWithDocuments[]>([]);
const totalProjects = ref(0);
const currentPage = ref(1);
const pageSize = ref(12);

// 对话框
const showCreateDialog = ref(false);
const editingProject = ref<ProjectRead | null>(null);
const projectFormRef = ref<FormInstance>();

// 表单
const projectForm = reactive<ProjectCreate & { id?: string }>({
  name: '',
  description: ''
});

const projectRules: FormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在2到50个字符', trigger: 'blur' }
  ]
};

// 获取项目列表
const fetchProjects = async (page = 1) => {
  loading.value = true;
  try {
    const response = await projectService.getProjects({
      page,
      per_page: pageSize.value
    });
    projects.value = response.projects;
    totalProjects.value = response.total;
    currentPage.value = page;
  } catch (error) {
    console.error('获取项目列表失败:', error);
    ElMessage.error('获取项目列表失败');
  } finally {
    loading.value = false;
  }
};

// 保存项目
const saveProject = async () => {
  if (!projectFormRef.value) return;
  
  const valid = await projectFormRef.value.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    if (editingProject.value) {
      // 编辑项目
      await projectService.updateProject(editingProject.value.id, {
        name: projectForm.name,
        description: projectForm.description
      });
      ElMessage.success('项目更新成功');
    } else {
      // 创建项目
      await projectService.createProject({
        name: projectForm.name,
        description: projectForm.description
      });
      ElMessage.success('项目创建成功');
    }
    
    showCreateDialog.value = false;
    await fetchProjects(currentPage.value);
  } catch (error: any) {
    console.error('保存项目失败:', error);
    ElMessage.error(error.response?.data?.detail || '保存失败');
  } finally {
    saving.value = false;
  }
};

// 取消编辑
const cancelEdit = () => {
  showCreateDialog.value = false;
  editingProject.value = null;
  projectForm.name = '';
  projectForm.description = '';
};

// 查看项目
const viewProject = (project: ProjectWithDocuments) => {
  router.push(`/projects/${project.id}/documents`);
};

// 处理项目命令
const handleProjectCommand = async (command: string, project: ProjectWithDocuments) => {
  switch (command) {
    case 'edit':
      editingProject.value = project;
      projectForm.name = project.name;
      projectForm.description = project.description || '';
      showCreateDialog.value = true;
      break;
    case 'search':
      router.push({
        path: '/search',
        query: { project_id: project.id }
      });
      break;
    case 'delete':
      try {
        console.log('开始删除项目:', project.id, project.name);
        
        await ElMessageBox.confirm(
          `确定要删除项目 \"${project.name}\" 吗？此操作无法撤销。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        );
        
        console.log('用户确认删除，开始调用API');
        const result = await projectService.deleteProject(project.id);
        console.log('删除API调用结果:', result);
        
        ElMessage.success('项目删除成功');
        console.log('刷新项目列表');
        await fetchProjects(currentPage.value);
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('删除项目失败:', error);
          console.error('错误详情:', error.response?.data);
          ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message));
        } else {
          console.log('用户取消删除');
        }
      }
      break;
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

// 组件挂载时获取数据
onMounted(() => {
  fetchProjects();
});
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

.projects-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 项目内容 */
.content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.content-header h2 {
  margin: 0;
  color: var(--gray-800);
  font-size: 1.875rem;
  font-weight: 700;
}

.projects-container {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: var(--shadow-md);
  margin-bottom: 2rem;
  border: 1px solid var(--gray-100);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all var(--transition-medium);
  position: relative;
  overflow: hidden;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), #8b5cf6);
  opacity: 0;
  transition: opacity var(--transition-medium);
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.project-card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-description {
  color: var(--gray-600);
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.more-btn {
  color: var(--gray-400);
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all var(--transition-fast);
}

.more-btn:hover {
  color: var(--gray-600);
  background: var(--gray-100);
}

.card-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem 0;
  border-top: 1px solid var(--gray-100);
  border-bottom: 1px solid var(--gray-100);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--gray-600);
  font-size: 0.875rem;
}

.stat-item .el-icon {
  color: var(--primary-color);
  font-size: 1rem;
}

.card-footer {
  padding-top: 0.75rem;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.loading-container {
  padding: 2rem;
}

.empty-state {
  padding: 3rem 0;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content {
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .content-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .projects-container {
    padding: 1rem;
    border-radius: 0.5rem;
  }
  
  .project-card {
    padding: 1rem;
  }
  
  .card-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
