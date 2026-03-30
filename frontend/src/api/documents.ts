import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

export interface DocumentCategory {
  id: number
  name: string
  code: string
  parent_id: number | null
  sort_order: number
  description: string | null
  created_at: string
  updated_at: string
  children?: DocumentCategory[]
}

export interface DocumentItem {
  id: number
  title: string
  description: string | null
  category_id: number | null
  type: string
  file_name: string
  file_path: string
  file_size: number
  file_type: string
  file_ext: string
  version: string
  status: string
  is_public: boolean
  allow_download: boolean
  view_count: number
  download_count: number
  uploader_id: number
  created_at: string
  updated_at: string
  category: {
    id: number
    name: string
    code: string
  } | null
  uploader: {
    id: number
    real_name: string
    username: string
  } | null
}

export interface DocumentQuery {
  keyword?: string
  category_id?: number
  type?: string
  status?: string
  page?: number
  page_size?: number
}

export const documentApi = {
  // 获取文档列表
  getDocuments: (params: DocumentQuery): Promise<ApiResponse<PaginatedData<DocumentItem>>> => {
    return api.get('/documents', { params })
  },

  // 获取文档详情
  getDocument: (id: number): Promise<ApiResponse<DocumentItem>> => {
    return api.get(`/documents/${id}`)
  },

  // 上传文档
  uploadDocument: (
    file: File,
    data: {
      title: string
      type: string
      category_id?: number
      description?: string
      version?: string
      is_public?: boolean
      allow_download?: boolean
    }
  ): Promise<ApiResponse<{
    id: number
    title: string
    file_name: string
    file_size: number
    file_ext: string
    preview_url: string
  }>> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    formData.append('type', data.type)
    if (data.category_id !== undefined) {
      formData.append('category_id', String(data.category_id))
    }
    if (data.description) {
      formData.append('description', data.description)
    }
    if (data.version) {
      formData.append('version', data.version)
    }
    if (data.is_public !== undefined) {
      formData.append('is_public', String(data.is_public))
    }
    if (data.allow_download !== undefined) {
      formData.append('allow_download', String(data.allow_download))
    }

    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 更新文档
  updateDocument: (
    id: number,
    data: {
      title?: string
      description?: string
      category_id?: number
      type?: string
      version?: string
      status?: string
      is_public?: boolean
      allow_download?: boolean
    }
  ): Promise<ApiResponse<DocumentItem>> => {
    return api.put(`/documents/${id}`, null, { params: data })
  },

  // 删除文档
  deleteDocument: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/documents/${id}`)
  },

  // 获取下载链接
  getDownloadUrl: (id: number): Promise<ApiResponse<{
    download_url: string
    file_name: string
  }>> => {
    return api.get(`/documents/${id}/download`)
  },

  // 获取预览链接
  getPreviewUrl: (id: number): Promise<ApiResponse<{
    preview_url: string
    file_name: string
    file_type: string
  }>> => {
    return api.get(`/documents/${id}/preview`)
  },

  // ========== 分类管理 ==========

  // 获取分类列表
  getCategories: (): Promise<ApiResponse<DocumentCategory[]>> => {
    return api.get('/documents/categories')
  },

  // 获取分类树
  getCategoryTree: (): Promise<ApiResponse<DocumentCategory[]>> => {
    return api.get('/documents/categories/tree')
  },

  // 创建分类
  createCategory: (data: {
    name: string
    code: string
    parent_id?: number
    sort_order?: number
    description?: string
  }): Promise<ApiResponse<DocumentCategory>> => {
    return api.post('/documents/categories', null, { params: data })
  },

  // 更新分类
  updateCategory: (
    id: number,
    data: {
      name?: string
      code?: string
      parent_id?: number
      sort_order?: number
      description?: string
    }
  ): Promise<ApiResponse<DocumentCategory>> => {
    return api.put(`/documents/categories/${id}`, null, { params: data })
  },

  // 删除分类
  deleteCategory: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/documents/categories/${id}`)
  },
}
