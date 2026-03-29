import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

// 合同类型
export interface Contract {
  id: number
  code: string
  name: string
  type: string
  amount: number
  company_id: number
  company?: {
    id: number
    name: string
  }
  sign_date: string | null
  start_date: string | null
  end_date: string | null
  status: string
  service_content: string | null
  service_cycle: string | null
  service_times: number
  payment_terms: string | null
  manager_id: number | null
  manager?: {
    id: number
    real_name: string
  }
  remark: string | null
  created_at: string
  updated_at: string
}

export interface ContractQuery {
  keyword?: string
  status?: string
  page?: number
  page_size?: number
}

export const contractApi = {
  // 获取合同列表
  getContracts: (params: ContractQuery): Promise<ApiResponse<PaginatedData<Contract>>> => {
    return api.get('/contracts', { params })
  },

  // 获取合同详情
  getContract: (id: number): Promise<ApiResponse<Contract>> => {
    return api.get(`/contracts/${id}`)
  },

  // 创建合同
  createContract: (data: Partial<Contract>): Promise<ApiResponse<Contract>> => {
    return api.post('/contracts', data)
  },

  // 更新合同
  updateContract: (id: number, data: Partial<Contract>): Promise<ApiResponse<Contract>> => {
    return api.put(`/contracts/${id}`, data)
  },

  // 删除合同
  deleteContract: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/contracts/${id}`)
  },
}
