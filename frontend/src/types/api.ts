// API 接口类型定义

// 搜索相关
export interface SearchQuery {
  query: string
  top_k?: number
  bm25_weight?: number
  tfidf_weight?: number
  project_id?: string
}

export interface SearchByFile {
  top_k?: number
  bm25_weight?: number
  tfidf_weight?: number
  project_id?: string
}

export interface ChunkSearchResult {
  chunk_id: string
  document_id: string
  document_title: string
  content: string
  chunk_index: number
  bm25_score: number
  tfidf_score: number
  final_score: number
}

export interface DocumentSearchResult {
  document_id: string
  document_title: string
  file_type: string
  max_score: number
  avg_score: number
  matched_chunks_count: number
  top_chunks: ChunkSearchResult[]
}

export interface SearchResponse {
  query: string
  total_chunks: number
  total_documents: number
  chunks: ChunkSearchResult[]
  documents: DocumentSearchResult[]
  search_time_ms: number
}

export interface SearchStatus {
  user_id: string
  total_documents: number
  total_chunks: number
  index_built: boolean
  last_index_update: string | null
}

// 文档相关
export enum DocumentStatus {
  PENDING_PROCESS = "PENDING_PROCESS",
  PROCESSING = "PROCESSING", 
  PENDING_CHUNK = "PENDING_CHUNK",
  SYNCING = "SYNCING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

export enum FileType {
  PDF = "PDF",
  DOCX = "DOCX", 
  PPTX = "PPTX",
  XLSX = "XLSX",
  HTML = "HTML",
  TXT = "TXT",
  CSV = "CSV",
  JSON = "JSON",
  XML = "XML"
}

export interface DocumentRead {
  id: string
  filename: string
  original_filename: string
  file_type: FileType
  file_size: number
  status: DocumentStatus
  owner_id: string
  project_id: string | null
  title: string | null
  source_info: Record<string, any> | null
  created_at: string
  updated_at: string
}

export interface DocumentList {
  documents: DocumentRead[]
  total: number
  page: number
  per_page: number
}

// 项目相关
export interface ProjectCreate {
  name: string
  description?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
}

export interface ProjectRead {
  id: string
  name: string
  description: string | null
  owner_id: string
  created_at: string
  updated_at: string
}

export interface ProjectWithDocuments extends ProjectRead {
  document_count: number
}

export interface ProjectList {
  projects: ProjectWithDocuments[]
  total: number
  page: number
  per_page: number
}