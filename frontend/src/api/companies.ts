import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

// 公司/客户类型
export interface Company {
  id: number
  name: string
  short_name: string | null
  code: string
  unified_code: string | null
  industry: string | null
  scale: string | null
  province: string | null
  city: string | null
  district: string | null
  street: string | null
  address: string | null
  status: 'potential' | 'active' | 'inactive' | 'lost'
  source: string | null
  manager_id: number | null
  remark: string | null
  created_at: string
  updated_at: string
  manager?: {
    id: number
    real_name: string
  }
}

export interface CompanyQuery {
  keyword?: string
  status?: string
  page?: number
  page_size?: number
}

export const companyApi = {
  // 获取公司列表
  getCompanies: (params: CompanyQuery): Promise<ApiResponse<PaginatedData<Company>>> => {
    return api.get('/companies', { params })
  },

  // 获取公司详情
  getCompany: (id: number): Promise<ApiResponse<Company>> => {
    return api.get(`/companies/${id}`)
  },

  // 创建公司
  createCompany: (data: Partial<Company>): Promise<ApiResponse<Company>> => {
    return api.post('/companies', data)
  },

  // 更新公司
  updateCompany: (id: number, data: Partial<Company>): Promise<ApiResponse<Company>> => {
    return api.put(`/companies/${id}`, data)
  },

  // 删除公司
  deleteCompany: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/companies/${id}`)
  },

  // ========== 统计接口 ==========

  // 按区县统计
  getStatisticsByDistrict: (): Promise<ApiResponse<Array<{ district: string; count: number }>>> => {
    return api.get('/companies/statistics/by-district')
  },

  // 按镇街统计
  getStatisticsByStreet: (district?: string): Promise<ApiResponse<Array<{ district: string; street: string; count: number }>>> => {
    return api.get('/companies/statistics/by-street', { params: { district } })
  },

  // 区县详细统计（包含下属镇街）
  getDistrictDetailStatistics: (): Promise<ApiResponse<Array<{
    district: string
    total: number
    streets: Array<{ street: string; count: number }>
  }>>> => {
    return api.get('/companies/statistics/district-detail')
  },
}
