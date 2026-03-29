import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { UserProfile } from '@/types'

interface AuthState {
  // 状态
  token: string | null
  refreshToken: string | null
  user: UserProfile | null
  isAuthenticated: boolean
  isHydrated: boolean // 新增：标记是否已完成 hydration

  // 操作
  setAuth: (token: string, refreshToken: string, user: UserProfile) => void
  updateUser: (user: Partial<UserProfile>) => void
  logout: () => void
  setHydrated: (value: boolean) => void // 新增：设置 hydration 状态
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      isHydrated: false, // 默认为 false

      setAuth: (token, refreshToken, user) => {
        console.log('[AuthStore] setAuth:', { token: token ? 'exists' : 'null', user: user?.username })
        set({
          token,
          refreshToken,
          user,
          isAuthenticated: true,
        })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },

      logout: () => {
        console.log('[AuthStore] logout')
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        })
      },

      setHydrated: (value: boolean) => {
        console.log('[AuthStore] setHydrated:', value)
        set({ isHydrated: value })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化特定字段
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      // hydration 完成后设置标志
      onRehydrateStorage: () => (state) => {
        console.log('[AuthStore] hydration 完成:', state)
        state?.setHydrated(true)
      },
    }
  )
)

// 导出获取 token 的辅助函数
// 使用 fallback 机制：如果 store 中没有，直接从 localStorage 读取
export const getAccessToken = (): string | null => {
  const state = useAuthStore.getState()
  if (state.token) {
    return state.token
  }
  // Fallback: 直接从 localStorage 读取（处理 hydration 延迟问题）
  try {
    const storage = localStorage.getItem('auth-storage')
    if (storage) {
      const parsed = JSON.parse(storage)
      return parsed?.state?.token || null
    }
  } catch (e) {
    console.error('[getAccessToken] 解析 localStorage 失败:', e)
  }
  return null
}

export const getRefreshToken = (): string | null => {
  const state = useAuthStore.getState()
  if (state.refreshToken) {
    return state.refreshToken
  }
  // Fallback: 直接从 localStorage 读取
  try {
    const storage = localStorage.getItem('auth-storage')
    if (storage) {
      const parsed = JSON.parse(storage)
      return parsed?.state?.refreshToken || null
    }
  } catch (e) {
    console.error('[getRefreshToken] 解析 localStorage 失败:', e)
  }
  return null
}

// 检查 store 是否已完成 hydration
export const isStoreHydrated = (): boolean => {
  return useAuthStore.getState().isHydrated
}
