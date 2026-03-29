import api from './api'
import { ApiResponse, PaginatedData, User, UserQuery, Role, RoleQuery } from '@/types'

export const userApi = {
  // 用户管理
  getUsers: (params: UserQuery): Promise<ApiResponse<PaginatedData<User>>> => {
    return api.get('/users', { params })
  },

  getUser: (id: number): Promise<ApiResponse<User>> => {
    return api.get(`/users/${id}`)
  },

  createUser: (data: Partial<User>): Promise<ApiResponse<User>> => {
    return api.post('/users', data)
  },

  updateUser: (id: number, data: Partial<User>): Promise<ApiResponse<User>> => {
    return api.put(`/users/${id}`, data)
  },

  deleteUser: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/users/${id}`)
  },

  resetPassword: (id: number, newPassword: string): Promise<ApiResponse<null>> => {
    return api.post(`/users/${id}/reset-password`, { new_password: newPassword })
  },

  // 角色管理
  getRoles: (params?: RoleQuery): Promise<ApiResponse<PaginatedData<Role>>> => {
    return api.get('/roles', { params })
  },

  getRole: (id: number): Promise<ApiResponse<Role>> => {
    return api.get(`/roles/${id}`)
  },

  createRole: (data: Partial<Role>): Promise<ApiResponse<Role>> => {
    return api.post('/roles', data)
  },

  updateRole: (id: number, data: Partial<Role>): Promise<ApiResponse<Role>> => {
    return api.put(`/roles/${id}`, data)
  },

  deleteRole: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/roles/${id}`)
  },
}
