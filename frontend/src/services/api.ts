import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { 
  SearchQuery, 
  SearchResponse, 
  SearchByFile,
  SearchStatus,
  DocumentRead,
  DocumentList,
  ProjectCreate,
  ProjectRead,
  ProjectList,
  ProjectUpdate,
  CompareRequest,
  CompareResponse,
  CompareFilesRequest,
  FileUploadResponse,
  SuccessResponse
} from '@/types/api'

// API 基础配置
const API_BASE_URL = '/scdlsearch/api'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,  // 120秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('auth_token')
    console.log('请求拦截器 - 请求URL:', config.url)
    console.log('请求拦截器 - 请求方法:', config.method)
    console.log('请求拦截器 - 认证token存在:', !!token)
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.warn('请求拦截器 - 未找到认证token')
    }
    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const defaultMessage = '请求失败，请稍后重试'
    
    // 处理401 Unauthorized错误
    if (error.response && error.response.status === 401) {
      if (window.location.hash !== '#/login') {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        
        ElMessage.error('会话已过期，请重新登录。')
        
        window.location.href = '/scdlsearch/#/login'
      }
    } else {
      // 对于其他错误，显示后端返回的错误信息
      const message = error.response?.data?.detail || error.message || defaultMessage;
      ElMessage.error(message);
      console.error('API Error:', message);
    }
    
    return Promise.reject(error)
  }
)

// 搜索服务
export const searchService = {
  // 文本搜索
  async textSearch(params: SearchQuery): Promise<SearchResponse> {
    return apiClient.post('/search/text', params)
  },

  // 文件搜索
  async fileSearch(file: File, params: SearchByFile = {}): Promise<SearchResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    // 添加其他参数
    if (params.top_k) formData.append('top_k', params.top_k.toString())
    if (params.bm25_weight) formData.append('bm25_weight', params.bm25_weight.toString())
    if (params.tfidf_weight) formData.append('tfidf_weight', params.tfidf_weight.toString())
    if (params.project_id) formData.append('project_id', params.project_id)
    
    return apiClient.post('/search/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 重建搜索索引
  async rebuildIndex(): Promise<{ message: string }> {
    return apiClient.post('/search/rebuild-index')
  },

  // 获取搜索状态
  async getStatus(): Promise<SearchStatus> {
    return apiClient.get('/search/status')
  }
}

// 文档服务
export const documentService = {
  // 获取文档列表
  async getDocuments(params: { 
    project_id?: string, 
    page?: number, 
    per_page?: number 
  } = {}): Promise<DocumentList> {
    return apiClient.get('/documents/', { params })
  },

  // 上传文档
  async uploadDocument(file: File, project_id?: string): Promise<DocumentRead> {
    console.log('documentService.uploadDocument 调用参数:')
    console.log('- file:', file.name, file.size)
    console.log('- project_id:', project_id)
    
    const formData = new FormData()
    formData.append('file', file)
    if (project_id) {
      formData.append('project_id', project_id)
      console.log('已添加 project_id 到 FormData:', project_id)
    } else {
      console.log('project_id 为空，未添加到 FormData')
    }
    
    console.log('FormData 内容:')
    for (let pair of formData.entries()) {
      console.log(`- ${pair[0]}:`, pair[1])
    }
    
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('上传API响应:', response)
    return response as unknown as DocumentRead
  },

  // 删除文档
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return apiClient.delete(`/documents/${documentId}`)
  },

  // 获取文档详情
  async getDocument(documentId: string): Promise<DocumentRead> {
    return apiClient.get(`/documents/${documentId}`)
  },

  // 获取文档错误信息
  async getDocumentError(documentId: string): Promise<{ error_log: string, status: string }> {
    return apiClient.get(`/documents/${documentId}/error`)
  }
}

// 项目服务
export const projectService = {
  // 创建项目
  async createProject(data: ProjectCreate): Promise<ProjectRead> {
    return apiClient.post('/projects/', data)
  },

  // 获取项目列表
  async getProjects(params: { page?: number, per_page?: number } = {}): Promise<ProjectList> {
    return apiClient.get('/projects/', { params })
  },

  // 获取项目详情
  async getProject(projectId: string): Promise<ProjectRead> {
    return apiClient.get(`/projects/${projectId}`)
  },

  // 更新项目
  async updateProject(projectId: string, data: ProjectUpdate): Promise<ProjectRead> {
    return apiClient.put(`/projects/${projectId}`, data)
  },

  // 删除项目
  async deleteProject(projectId: string): Promise<{ message: string }> {
    console.log('projectService.deleteProject 调用参数:', projectId)
    console.log('即将发送DELETE请求到:', `/projects/${projectId}`)
    console.log('完整URL:', `${API_BASE_URL}/projects/${projectId}`)
    
    try {
      const response = await apiClient.delete(`/projects/${projectId}`)
      console.log('删除项目API响应:', response)
      return response as unknown as { message: string }
    } catch (error: any) {
      console.error('删除项目API请求失败:', error)
      console.error('错误详情:', error.response?.data)
      console.error('错误状态:', error.response?.status)
      console.error('请求配置:', error.config)
      throw error
    }
  },

  // 添加文档到项目
  async addDocumentToProject(projectId: string, documentId: string): Promise<{ message: string }> {
    return apiClient.post(`/projects/${projectId}/documents/${documentId}`)
  },

  // 从项目移除文档
  async removeDocumentFromProject(projectId: string, documentId: string): Promise<{ message: string }> {
    return apiClient.delete(`/projects/${projectId}/documents/${documentId}`)
  },

  // 获取项目文档列表
  async getProjectDocuments(projectId: string, params: { page?: number, per_page?: number } = {}): Promise<DocumentList> {
    return apiClient.get(`/projects/${projectId}/documents`, { params })
  }
}

// 用户服务
export const userService = {
  // 用户注册
  async register(userData: { username: string; email: string; password: string }) {
    return apiClient.post('/users/register', userData)
  },

  // 用户登录
  async login(credentials: { email: string; password: string }): Promise<{ access_token: string; token_type: string }> {
    return apiClient.post('/users/login', credentials)
  }
}

// 文档比对服务
export const compareService = {
  // 比较文本文档
  async compareTexts(data: CompareRequest): Promise<CompareResponse> {
    return apiClient.post('/compare/text', data)
  },

  // 上传文件用于比较
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    return apiClient.post('/compare/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 比较已上传的文件
  async compareFiles(data: CompareFilesRequest): Promise<CompareResponse> {
    return apiClient.post('/compare/files', data)
  },

  // 获取已上传文件信息
  async getFileInfo(fileId: string): Promise<FileUploadResponse> {
    return apiClient.get(`/compare/files/${fileId}`)
  },

  // 删除已上传的文件
  async deleteFile(fileId: string): Promise<SuccessResponse> {
    return apiClient.delete(`/compare/files/${fileId}`)
  },

  // 列出所有已上传的文件
  async listFiles(): Promise<Record<string, FileUploadResponse>> {
    return apiClient.get('/compare/files')
  }
}

export default {
  searchService,
  documentService,
  projectService,
  userService,
  compareService
}