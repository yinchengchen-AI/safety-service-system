import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuthStore, getAccessToken, getRefreshToken } from '@/stores/authStore'
import { authApi } from '@/api/auth'

// 页面导入
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
import UserList from '@/pages/UserManagement/UserList'
import RoleList from '@/pages/UserManagement/RoleList'
import DepartmentList from '@/pages/UserManagement/DepartmentList'
import CompanyList from '@/pages/CustomerManagement/CompanyList'
import ContractList from '@/pages/ContractManagement/ContractList'
import InvoiceList from '@/pages/FinanceManagement/InvoiceList'
import PaymentList from '@/pages/FinanceManagement/PaymentList'
import ServiceList from '@/pages/ServiceManagement/ServiceList'
import DocumentList from '@/pages/DocumentManagement/DocumentList'
import DocumentUpload from '@/pages/DocumentManagement/DocumentUpload'
import LogManagement from '@/pages/SystemSettings/LogManagement'
import NoticeList from '@/pages/NoticeManagement/NoticeList'
import NoticeForm from '@/pages/NoticeManagement/NoticeForm'
import NoticeDetail from '@/pages/NoticeManagement/NoticeDetail'
import NoticeStats from '@/pages/NoticeManagement/NoticeStats'
import StatisticsDashboard from '@/pages/StatisticsAnalysis/StatisticsDashboard'
import LoginLogPage from '@/pages/StatisticsAnalysis/LoginLog'
import Profile from '@/pages/Profile'

// 布局组件
import MainLayout from '@/components/Layout/MainLayout'

// 路由守卫
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

// 初始化加载组件
const AppInitializer = ({ children }: { children: React.ReactNode }) => {
  const { setAuth, logout } = useAuthStore()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // 等待瞬间让 zustand persist 完成 hydration
    const timer = setTimeout(() => {
      const initAuth = async () => {
        const token = getAccessToken()
        console.log('[App Init] Token:', token ? `存在 (${token.substring(0, 30)}...)` : '不存在')
        
        if (token) {
          try {
            const res = await authApi.getProfile()
            if (res.code === 200) {
              const refreshToken = getRefreshToken() || ''
              setAuth(token, refreshToken, res.data)
              console.log('[App Init] 用户认证成功:', res.data.username)
            }
          } catch (error: any) {
            console.error('[App Init] 认证失败:', error?.response?.status, error?.response?.data)
            logout()
            if (error?.response?.status === 401) {
              window.location.href = '/login'
            }
          }
        } else {
          console.log('[App Init] 未登录状态')
        }
        setIsReady(true)
      }
      initAuth()
    }, 100) // 100ms 给 persist 时间完成 hydration

    return () => clearTimeout(timer)
  }, [])

  if (!isReady) {
    return <div style={{ display: 'none' }}>初始化中...</div>
  }

  return <>{children}</>
}

function App() {
  return (
    <AppInitializer>
      <BrowserRouter>
        <Routes>
          {/* 登录页 */}
          <Route path="/login" element={<Login />} />

          {/* 主布局 */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <MainLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<Dashboard />} />
            
            {/* 用户管理 */}
            <Route path="users" element={<UserList />} />
            <Route path="roles" element={<RoleList />} />
            <Route path="departments" element={<DepartmentList />} />
            
            {/* 客户管理 */}
            <Route path="companies" element={<CompanyList />} />
            
            {/* 合同管理 */}
            <Route path="contracts" element={<ContractList />} />
            
            {/* 服务管理 */}
            <Route path="services" element={<ServiceList />} />
            
            {/* 财务管理 */}
            <Route path="invoices" element={<InvoiceList />} />
            <Route path="payments" element={<PaymentList />} />
            
            {/* 文档管理 */}
            <Route path="documents" element={<DocumentList />} />
            <Route path="documents/upload" element={<DocumentUpload />} />
            
            {/* 系统设置 */}
            <Route path="logs" element={<LogManagement />} />
            <Route path="login-logs" element={<LoginLogPage />} />
            
            {/* 通知公告 */}
            <Route path="notices" element={<NoticeList />} />
            <Route path="notices/create" element={<NoticeForm />} />
            <Route path="notices/edit/:id" element={<NoticeForm />} />
            <Route path="notices/detail/:id" element={<NoticeDetail />} />
            <Route path="notices/stats/:id" element={<NoticeStats />} />
            
            {/* 统计分析 */}
            <Route path="statistics" element={<StatisticsDashboard />} />
            
            {/* 个人中心 */}
            <Route path="profile" element={<Profile />} />
            
            {/* 404 */}
            <Route path="*" element={<div>页面不存在</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppInitializer>
  )
}

export default App
