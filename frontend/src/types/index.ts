// 通用响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// 用户类型
export interface User {
  id: number
  username: string
  real_name: string | null
  phone: string | null
  email: string | null
  avatar: string | null
  status: 'active' | 'inactive' | 'locked'
  is_superuser: boolean
  department_id: number | null
  last_login_at: string | null
  created_at: string
  updated_at: string
  department?: Department
  roles?: Role[]
}

export interface UserProfile {
  id: number
  username: string
  real_name: string | null
  phone: string | null
  email: string | null
  avatar: string | null
  department: Department | null
  roles: string[]
  permissions: string[]
  is_superuser: boolean
}

// 角色类型
export interface Role {
  id: number
  name: string
  code: string
  description: string | null
  is_system: boolean
  sort_order: number
  created_at: string
  updated_at: string
  permissions?: Permission[]
}

// 权限类型
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

// 部门类型
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

// 登录相关
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: UserProfile
}

// 查询参数
export interface UserQuery {
  keyword?: string
  department_id?: number
  status?: string
  page?: number
  page_size?: number
}

export interface RoleQuery {
  keyword?: string
  page?: number
  page_size?: number
}

// 菜单项
export interface MenuItem {
  key: string
  label: string
  icon?: React.ReactNode
  path?: string
  children?: MenuItem[]
  permission?: string
}
