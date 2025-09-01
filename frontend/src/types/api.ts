// API 接口类型定义

// 搜索相关
export interface SearchQuery {
  query: string
  top_k?: number
  top_k_chunks?: number // 新增
  bm25_weight?: number
  tfidf_weight?: number
  project_id?: string
}

export interface SearchByFile {
  top_k?: number
  top_k_chunks?: number // 新增
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

// 文档比对相关
export interface DocumentInfo {
  filename: string
  content: string
  html_content: string
  chunks_count: number
}

export interface MatchLink {
  chunk_a_id: string
  chunk_b_id: string
  chunk_a: string
  chunk_b: string
  similarity: number
  match_type: 'high' | 'medium' | 'low'
  link_id: string
}

export interface ComparisonResult {
  overall_similarity: number
  total_matches: number
  high_similarity_matches: number
  medium_similarity_matches: number
  match_links: MatchLink[]
}

export interface AlgorithmParams {
  similarity_threshold_high: number
  similarity_threshold_medium: number
  chunk_size: number
}

export interface ComparisonMetadata {
  comparison_time: string | null
  algorithm_params: AlgorithmParams
  highlighted_files?: {
    file_a?: string
    file_b?: string
  }
}

export interface CompareResponse {
  document_a: DocumentInfo
  document_b: DocumentInfo
  comparison: ComparisonResult
  metadata: ComparisonMetadata
}

export interface CompareRequest {
  text_a: string
  text_b: string
  filename_a?: string
  filename_b?: string
  similarity_threshold_high?: number
  similarity_threshold_medium?: number
  chunk_size?: number
}

export interface FileUploadResponse {
  filename: string
  file_id: string
  content_preview: string
  file_size: number
  upload_time: string
}

export interface CompareFilesRequest {
  file_a_id: string
  file_b_id: string
  similarity_threshold_high?: number
  similarity_threshold_medium?: number
  chunk_size?: number
}

export interface ErrorResponse {
  error: string
  detail?: string
  code?: string
}

export interface SuccessResponse {
  message: string
  data?: any
}