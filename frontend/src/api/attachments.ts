import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

export interface Attachment {
  id: number
  file_name: string
  file_size: number
  file_type: string
  file_ext: string
  file_path: string
  ref_type: string
  ref_id: number
  description: string | null
  uploader: {
    id: number
    real_name: string
    username: string
  } | null
  created_at: string
}

export interface AttachmentQuery {
  ref_type?: string
  ref_id?: number
  page?: number
  page_size?: number
}

export const attachmentApi = {
  // 获取附件列表
  getAttachments: (params: AttachmentQuery): Promise<ApiResponse<PaginatedData<Attachment>>> => {
    return api.get('/attachments', { params })
  },

  // 上传附件
  uploadAttachment: (
    file: File,
    refType: string,
    refId: number,
    description?: string
  ): Promise<ApiResponse<{
    id: number
    file_name: string
    file_size: number
    file_ext: string
    preview_url: string
  }>> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const url = `/attachments/upload?ref_type=${refType}&ref_id=${refId}${description ? `&description=${encodeURIComponent(description)}` : ''}`
    
    return api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 获取下载链接
  getDownloadUrl: (id: number): Promise<ApiResponse<{
    download_url: string
    file_name: string
  }>> => {
    return api.get(`/attachments/${id}/download`)
  },

  // 获取预览链接
  getPreviewUrl: (id: number): Promise<ApiResponse<{
    preview_url: string
    file_name: string
    file_type: string
  }>> => {
    return api.get(`/attachments/${id}/preview`)
  },

  // 删除附件
  deleteAttachment: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/attachments/${id}`)
  },
}
