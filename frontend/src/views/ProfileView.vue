<template>
  <div class="profile-view">
    <AppHeader />

    <!-- 个人资料内容 -->
    <div class="profile-content">
      <div class="container">
        <div class="profile-header">
          <div class="profile-avatar">
            <el-avatar :size="120" :src="userAvatar">
              <el-icon :size="60"><User /></el-icon>
            </el-avatar>
            <el-button size="small" class="change-avatar">
              <el-icon><Camera /></el-icon>
              更换头像
            </el-button>
          </div>
          
          <div class="profile-info">
            <h1 class="profile-name">{{ authStore.user?.username }}</h1>
            <p class="profile-email">{{ authStore.user?.email }}</p>
            <div class="profile-stats">
              <div class="stat-item">
                <span class="stat-number">12</span>
                <span class="stat-label">上传文档</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">48</span>
                <span class="stat-label">搜索次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">7</span>
                <span class="stat-label">使用天数</span>
              </div>
            </div>
          </div>
        </div>

        <div class="profile-tabs">
          <el-tabs v-model="activeTab" class="profile-tabs-container">
            <el-tab-pane label="基本信息" name="info">
              <div class="tab-content">
                <el-form :model="profileForm" label-width="100px" size="large">
                  <el-form-item label="用户名">
                    <el-input v-model="profileForm.username" />
                  </el-form-item>
                  <el-form-item label="邮箱">
                    <el-input v-model="profileForm.email" />
                  </el-form-item>
                  <el-form-item label="注册时间">
                    <el-input :value="formatDate(authStore.user?.created_at)" readonly />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary">保存更改</el-button>
                    <el-button>取消</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="安全设置" name="security">
              <div class="tab-content">
                <el-form label-width="120px" size="large">
                  <el-form-item label="当前密码">
                    <el-input type="password" placeholder="请输入当前密码" />
                  </el-form-item>
                  <el-form-item label="新密码">
                    <el-input type="password" placeholder="请输入新密码" />
                  </el-form-item>
                  <el-form-item label="确认密码">
                    <el-input type="password" placeholder="请确认新密码" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary">更新密码</el-button>
                  </el-form-item>
                </el-form>
                
                <el-divider />
                
                <div class="danger-zone">
                  <h3>危险操作</h3>
                  <p>删除账户将无法恢复，请谨慎操作</p>
                  <el-button type="danger" size="large">
                    删除账户
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="使用偏好" name="preferences">
              <div class="tab-content">
                <el-form label-width="120px" size="large">
                  <el-form-item label="默认搜索数量">
                    <el-slider v-model="preferences.defaultSearchCount" :min="5" :max="50" show-input />
                  </el-form-item>
                  <el-form-item label="搜索算法偏好">
                    <el-radio-group v-model="preferences.searchAlgorithm">
                      <el-radio label="balanced">平衡模式</el-radio>
                      <el-radio label="bm25">BM25优先</el-radio>
                      <el-radio label="tfidf">TF-IDF优先</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="自动保存搜索历史">
                    <el-switch v-model="preferences.saveHistory" />
                  </el-form-item>
                  <el-form-item label="结果高亮显示">
                    <el-switch v-model="preferences.highlightResults" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary">保存偏好</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { User, Camera } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()

const userAvatar = computed(() => 
  `https://api.dicebear.com/7.x/initials/svg?seed=${authStore.user?.username}`
)

// 标签页
const activeTab = ref('info')

// 个人资料表单
const profileForm = reactive({
  username: authStore.user?.username || '',
  email: authStore.user?.email || ''
})

// 用户偏好
const preferences = reactive({
  defaultSearchCount: 10,
  searchAlgorithm: 'balanced',
  saveHistory: true,
  highlightResults: true
})

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 个人资料内容 */
.profile-content {
  padding: 2rem;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-header {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-md);
  display: flex;
  gap: 2rem;
  align-items: center;
}

.profile-avatar {
  text-align: center;
  position: relative;
}

.change-avatar {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  border-radius: 1rem;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 2rem;
  font-weight: 700;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
}

.profile-email {
  color: var(--gray-600);
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.profile-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--gray-500);
}

.profile-tabs {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: var(--shadow-md);
}

.profile-tabs-container {
  --el-tabs-header-height: 50px;
}

.tab-content {
  padding-top: 1rem;
}

.danger-zone {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-top: 2rem;
}

.danger-zone h3 {
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.danger-zone p {
  color: #7f1d1d;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-stats {
    justify-content: center;
  }
  
  .profile-content {
    padding: 1rem;
  }
}
</style>