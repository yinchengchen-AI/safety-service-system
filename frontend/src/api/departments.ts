import api from './api'
import { ApiResponse } from '@/types'

export interface Department {
  id: number
  name: string
  code: string
  parent_id: number | null
  sort_order: number
  description: string | null
  created_at: string
  updated_at: string
  children?: Department[]
}

export const departmentApi = {
  // 获取部门树形列表
  getDepartments: (): Promise<ApiResponse<Department[]>> => {
    return api.get('/departments')
  },

  // 获取部门扁平列表（用于下拉选择）
  getDepartmentsFlat: (): Promise<ApiResponse<Department[]>> => {
    return api.get('/departments/flat')
  },

  // 创建部门
  createDepartment: (data: Partial<Department>): Promise<ApiResponse<Department>> => {
    return api.post('/departments', data)
  },

  // 更新部门
  updateDepartment: (id: number, data: Partial<Department>): Promise<ApiResponse<Department>> => {
    return api.put(`/departments/${id}`, data)
  },

  // 删除部门
  deleteDepartment: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/departments/${id}`)
  },
}
