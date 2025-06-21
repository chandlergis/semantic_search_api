<template>
  <div class="login-view">
    <!-- 背景装饰 -->
    <div class="background-decorations">
      <div class="decoration decoration-1"></div>
      <div class="decoration decoration-2"></div>
      <div class="decoration decoration-3"></div>
    </div>

    <!-- 登录容器 -->
    <div class="login-container">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content animate-fadeInLeft">
          <div class="logo-container">
            <el-icon class="brand-logo" :size="60">
              <Search />
            </el-icon>
          </div>
          <h1 class="brand-title gradient-text">语义匹配</h1>
          <p class="brand-subtitle">
            智能文档搜索平台<br>
            让信息检索变得简单高效
          </p>
          <div class="feature-list">
            <div class="feature-item">
              <el-icon><DocumentChecked /></el-icon>
              <span>多格式文档支持</span>
            </div>
            <div class="feature-item">
              <el-icon><MagicStick /></el-icon>
              <span>智能语义分析</span>
            </div>
            <div class="feature-item">
              <el-icon><TrendCharts /></el-icon>
              <span>精准搜索结果</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-section">
        <div class="form-container glass-effect animate-fadeInUp">
          <!-- 切换标签 -->
          <div class="form-tabs">
            <button 
              :class="['tab-button', { active: currentTab === 'login' }]"
              @click="currentTab = 'login'"
            >
              登录
            </button>
            <button 
              :class="['tab-button', { active: currentTab === 'register' }]"
              @click="currentTab = 'register'"
            >
              注册
            </button>
          </div>

          <!-- 登录表单 -->
          <div v-if="currentTab === 'login'" class="form-content">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账户以继续使用</p>

            <el-form 
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              size="large"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="email">
                <el-input
                  v-model="loginForm.email"
                  placeholder="邮箱地址"
                  :prefix-icon="Message"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>

              <div class="form-options">
                <el-checkbox v-model="loginForm.remember">
                  记住我
                </el-checkbox>
                <el-link type="primary" :underline="false">
                  忘记密码？
                </el-link>
              </div>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-button"
                  :loading="authStore.isLoading"
                  @click="handleLogin"
                >
                  登录
                </el-button>
              </el-form-item>
            </el-form>


            <div class="social-login">
            </div>
          </div>

          <!-- 注册表单 -->
          <div v-if="currentTab === 'register'" class="form-content">
            <h2 class="form-title">创建账户</h2>
            <p class="form-subtitle">注册新账户开始您的搜索之旅</p>

            <el-form 
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              size="large"
              @submit.prevent="handleRegister"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="用户名"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="邮箱地址"
                  :prefix-icon="Message"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="密码"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="确认密码"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>

              <el-form-item prop="agree">
                <el-checkbox v-model="registerForm.agree">
                  我同意
                  <el-link type="primary" :underline="false">用户协议</el-link>
                  和
                  <el-link type="primary" :underline="false">隐私政策</el-link>
                </el-checkbox>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-button"
                  :loading="authStore.isLoading"
                  @click="handleRegister"
                >
                  注册
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { 
  Search, 
  User, 
  Lock, 
  Message, 
  DocumentChecked,
  MagicStick,
  TrendCharts
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginFormData, RegisterFormData } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

// 当前标签页
const currentTab = ref<'login' | 'register'>('login')

// 表单引用
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

// 登录表单
const loginForm = reactive<LoginFormData>({
  email: '',
  password: '',
  remember: false
})

// 注册表单
const registerForm = reactive<RegisterFormData>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 表单验证规则
const loginRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  agree: [
    {
      validator: (_rule, value, callback) => {
        if (!value) {
          callback(new Error('请同意用户协议'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  const result = await authStore.login({
    email: loginForm.email,
    password: loginForm.password
  })

  if (result.success) {
    ElMessage.success({
      message: '登录成功',
      duration: 1500
    })
    router.push('/search')
  } else {
    ElMessage.error(result.message)
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  const result = await authStore.register({
    username: registerForm.username,
    email: registerForm.email,
    password: registerForm.password
  })

  if (result.success) {
    ElMessage.success('注册成功')
    router.push('/search')
  } else {
    ElMessage.error(result.message)
  }
}
</script>

<style scoped>
.login-view {
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 25%, #ec4899 75%, #f43f5e 100%);
}

/* 背景装饰 */
.background-decorations {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.decoration {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.decoration-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation: float 6s ease-in-out infinite;
}

.decoration-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite reverse;
}

.decoration-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: 20%;
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 主容器 */
.login-container {
  height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  position: relative;
  z-index: 1;
}

/* 品牌区域 */
.brand-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: white;
}

.brand-content {
  text-align: center;
  max-width: 400px;
}

.logo-container {
  margin-bottom: 2rem;
}

.brand-logo {
  color: rgba(255, 255, 255, 0.9);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.brand-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  opacity: 0.8;
}

.feature-item .el-icon {
  font-size: 1.2rem;
  color: #fbbf24;
}

/* 表单区域 */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.form-container {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  border-radius: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 标签切换 */
.form-tabs {
  display: flex;
  margin-bottom: 2rem;
  background: #f3f4f6;
  border-radius: 0.75rem;
  padding: 0.25rem;
}

.tab-button {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  border-radius: 0.5rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all var(--transition-medium);
}

.tab-button.active {
  background: white;
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

/* 表单内容 */
.form-content {
  animation: fadeInUp 0.6s ease-out;
}

.form-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--gray-800);
  margin-bottom: 0.5rem;
  text-align: center;
}

.form-subtitle {
  color: var(--gray-600);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.submit-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  background: var(--gradient-primary);
  border: none;
  border-radius: 0.75rem;
  transition: all var(--transition-medium);
}

.submit-button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

/* 分割线 */
.divider {
  position: relative;
  text-align: center;
  margin: 2rem 0;
  color: var(--gray-500);
  font-size: 0.875rem;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--gray-200);
}

.divider span {
  background: white;
  padding: 0 1rem;
}

/* 社交登录 */
.social-login {
  display: flex;
  gap: 0.75rem;
}

.social-button {
  flex: 1;
  height: 44px;
  border-radius: 0.75rem;
  font-weight: 500;
  transition: all var(--transition-medium);
}

.social-button:hover {
  transform: translateY(-1px);
}

.github {
  background: #24292e;
  color: white;
  border: none;
}

.google {
  background: #ea4335;
  color: white;
  border: none;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-container {
    grid-template-columns: 1fr;
  }
  
  .brand-section {
    display: none;
  }
  
  .form-section {
    background: rgba(255, 255, 255, 0.2);
  }
}

@media (max-width: 640px) {
  .form-section {
    padding: 1rem;
  }
  
  .form-container {
    padding: 1.5rem;
  }
  
  .brand-title {
    font-size: 2rem;
  }
}
</style>