import api from './api'
import { ApiResponse } from '@/types'

export interface DashboardStats {
  total_contract_amount: number
  total_payment_amount: number
  active_services: number
  total_customers: number
  contract_count: number
  invoice_count: number
  pending_tasks: number
}

export interface TodoItem {
  id: number
  title: string
  description: string
  type: 'warning' | 'processing' | 'default'
  date: string
}

export interface ActivityItem {
  id: number
  user: string
  action: string
  target: string
  time: string
}

export const dashboardApi = {
  // 获取统计数据
  getStats: (): Promise<ApiResponse<DashboardStats>> => {
    return api.get('/statistics/dashboard')
  },

  // 获取待办事项
  getTodos: (): Promise<ApiResponse<TodoItem[]>> => {
    return api.get('/statistics/todos')
  },

  // 获取最近动态
  getActivities: (): Promise<ApiResponse<ActivityItem[]>> => {
    return api.get('/statistics/activities')
  },
}
