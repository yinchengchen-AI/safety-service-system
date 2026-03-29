import api from './api'
import { ApiResponse, LoginRequest, LoginResponse, UserProfile } from '@/types'

export const authApi = {
  // 登录
  login: (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
    return api.post('/auth/login', data)
  },

  // 刷新token
  refreshToken: (refreshToken: string): Promise<ApiResponse<{ access_token: string; token_type: string; expires_in: number }>> => {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },

  // 获取用户信息
  getProfile: (): Promise<ApiResponse<UserProfile>> => {
    return api.get('/auth/profile')
  },

  // 更新个人资料
  updateProfile: (data: { real_name?: string; phone?: string; email?: string; avatar?: string }): Promise<ApiResponse<UserProfile>> => {
    return api.put('/auth/profile', data)
  },

  // 上传头像
  uploadAvatar: (file: File): Promise<ApiResponse<{ avatar_url: string }>> => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 修改密码
  updatePassword: (data: { old_password: string; new_password: string; confirm_password: string }): Promise<ApiResponse<null>> => {
    return api.put('/auth/password', data)
  },

  // 登出
  logout: (): Promise<ApiResponse<null>> => {
    return api.post('/auth/logout')
  },
}
