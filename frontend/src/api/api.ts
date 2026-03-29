import axios, { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { message } from 'antd'
import { authApi } from './auth'
import { getAccessToken, getRefreshToken, useAuthStore } from '@/stores/authStore'

// 创建xios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 是否正在刷新token
let isRefreshing = false
// 等待token刷新的请求队列
let refreshSubscribers: ((token: string) => void)[] = []

// 订阅token刷新
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

// 通知所有订阅者新的token
function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach((callback) => callback(newToken))
  refreshSubscribers = []
}

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 获取 token（包含 fallback 到 localStorage 的逻辑）
    const token = getAccessToken()
    
    console.log('[Request Interceptor]', {
      url: config.url,
      method: config.method,
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 30)}...` : 'null',
      headersBefore: { ...config.headers },
    })
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('[Request Interceptor] 已添加 Authorization 头')
    } else {
      console.warn('[Request Interceptor] 警告: 没有找到 access_token!')
      // 打印 localStorage 内容以便调试
      try {
        const raw = localStorage.getItem('auth-storage')
        console.log('[Request Interceptor] localStorage raw:', raw)
      } catch (e) {
        console.log('[Request Interceptor] 无法读取 localStorage')
      }
    }
    
    console.log('[Request Interceptor] Final headers:', config.headers)
    return config
  },
  (error) => {
    console.error('[Request Interceptor] 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message: msg } = response.data
    
    // 业务错误
    if (code !== 200) {
      message.error(msg || '请求失败')
      return Promise.reject(new Error(msg))
    }
    
    return response.data
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    if (error.response) {
      const { status, data, config } = error.response
      
      // 调试日志
      console.error(`[API Error ${status}]:`, {
        url: config?.url,
        method: config?.method,
        headers: config?.headers,
        detail: (data as any)?.detail || (data as any)?.message,
      })
      
      // 401错误处理 - 尝试刷新token
      if (status === 401 && !originalRequest._retry) {
        const refreshToken = getRefreshToken()
        
        console.log('[API] 收到 401，检查 refresh token:', refreshToken ? '存圮' : '不存在')
        
        if (!refreshToken) {
          // 没有refresh token，直接登出
          console.error('[API] 没有 refresh token，执行登出')
          message.error('登录已过期，请重新登录')
          useAuthStore.getState().logout()
          window.location.href = '/login'
          return Promise.reject(error)
        }
        
        // 标记请求已重试
        originalRequest._retry = true
        
        // 如果正在刷新token，将请求加入队列等待
        if (isRefreshing) {
          console.log('[API] 正在刷新 token，加入等待队列')
          return new Promise((resolve) => {
            subscribeTokenRefresh((newToken: string) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              resolve(api(originalRequest))
            })
          })
        }
        
        isRefreshing = true
        
        try {
          // 调用刷新token API
          console.log('[API] 调用刷新 token API')
          const res = await authApi.refreshToken(refreshToken)
          
          if (res.code === 200 && res.data.access_token) {
            console.log('[API] 刷新 token 成功')
            // 保存新的access token
            useAuthStore.getState().setAuth(
              res.data.access_token,
              refreshToken,
              useAuthStore.getState().user!
            )
            
            // 通知所有等待的请求
            onTokenRefreshed(res.data.access_token)
            
            // 重试原始请求
            originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`
            return api(originalRequest)
          } else {
            throw new Error('刷新token失败')
          }
        } catch (refreshError) {
          // 刷新token失败，清除所有token并登出
          console.error('[API] 刷新 token 失败:', refreshError)
          message.error('登录已过期，请重新登录')
          useAuthStore.getState().logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }
      
      switch (status) {
        case 403:
          message.error('权限不足')
          break
        case 404:
          message.error((data as any)?.detail || '资源不存在')
          break
        case 422:
          message.error((data as any)?.detail || '请求参数错误')
          break
        default:
          message.error((data as any)?.detail || '服务器错误')
      }
    } else {
      message.error('网络错误')
    }
    
    return Promise.reject(error)
  }
)

export default api
