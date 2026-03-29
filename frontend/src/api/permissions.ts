import api from './api'
import { ApiResponse } from '@/types'

export interface Permission {
  id: number
  name: string
  code: string
  type: 'menu' | 'button' | 'api'
  parent_id: number | null
  path: string | null
  icon: string | null
  sort_order: number
  description: string | null
  created_at: string
  updated_at: string
  children?: Permission[]
}

export const permissionApi = {
  // 获取权限树
  getPermissionTree: (): Promise<ApiResponse<Permission[]>> => {
    return api.get('/permissions/tree')
  },

  // 获取所有权限
  getPermissions: (): Promise<ApiResponse<Permission[]>> => {
    return api.get('/permissions')
  },
}
