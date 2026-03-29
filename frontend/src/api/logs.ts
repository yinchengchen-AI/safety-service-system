import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

export interface OperationLog {
  id: number
  user_id: number | null
  username: string | null
  real_name: string | null
  log_type: string
  module: string
  action: string
  description: string | null
  request_method: string | null
  request_url: string | null
  ip_address: string | null
  user_agent: string | null
  execution_time: number | null
  status: string
  error_msg: string | null
  operation_time: string
}

export interface OperationLogDetail extends OperationLog {
  request_params: string | null
  response_data: string | null
}

export interface LoginLog {
  id: number
  user_id: number | null
  username: string | null
  real_name: string | null
  login_type: string
  login_status: string
  ip_address: string | null
  user_agent: string | null
  browser: string | null
  os: string | null
  device: string | null
  fail_reason: string | null
  login_time: string
}

export interface OperationLogQuery {
  page?: number
  page_size?: number
  username?: string
  module?: string
  log_type?: string
  status?: string
  start_time?: string
  end_time?: string
}

export interface LoginLogQuery {
  page?: number
  page_size?: number
  username?: string
  login_status?: string
  start_time?: string
  end_time?: string
}

export const logsApi = {
  // 获取操作日志列表
  getOperationLogs: (params: OperationLogQuery): Promise<ApiResponse<PaginatedData<OperationLog>>> => {
    return api.get('/logs/operation', { params })
  },

  // 获取操作日志详情
  getOperationLogDetail: (id: number): Promise<ApiResponse<OperationLogDetail>> => {
    return api.get(`/logs/operation/${id}`)
  },

  // 删除单条操作日志
  deleteOperationLog: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/logs/operation/${id}`)
  },

  // 批量删除操作日志
  batchDeleteOperationLogs: (ids: number[]): Promise<ApiResponse<null>> => {
    return api.delete('/logs/operation', { data: ids })
  },

  // 获取登录日志列表
  getLoginLogs: (params: LoginLogQuery): Promise<ApiResponse<PaginatedData<LoginLog>>> => {
    return api.get('/logs/login', { params })
  },

  // 获取操作模块列表
  getLogModules: (): Promise<ApiResponse<string[]>> => {
    return api.get('/logs/modules')
  },
}
