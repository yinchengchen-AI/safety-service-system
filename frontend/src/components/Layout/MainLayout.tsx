import { useState, useMemo } from 'react'
import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom'
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Badge,
  Space,
  theme,
  Breadcrumb,
} from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  FileTextOutlined,
  DollarOutlined,
  FolderOutlined,
  BellOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BarChartOutlined,
  LoginOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '@/stores'
import { authApi } from '@/api/auth'
import './style.css'

const { Header, Sider, Content } = Layout

// 菜单配置
const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: '工作台',
  },
  {
    key: 'user-management',
    icon: <UserOutlined />,
    label: '用户管理',
    children: [
      { key: '/users', label: '用户列表', permission: 'user:view' },
      { key: '/roles', label: '角色管理', permission: 'role:view' },
      { key: '/departments', label: '部门管理', permission: 'department:view' },
    ],
  },
  {
    key: 'customer-management',
    icon: <TeamOutlined />,
    label: '客户管理',
    children: [
      { key: '/companies', label: '企业客户', permission: 'company:view' },
    ],
  },
  {
    key: 'contract-management',
    icon: <FileTextOutlined />,
    label: '合同管理',
    children: [
      { key: '/contracts', label: '合同列表', permission: 'contract:view' },
    ],
  },
  {
    key: 'service-management',
    icon: <SafetyCertificateOutlined />,
    label: '服务管理',
    children: [
      { key: '/services', label: '服务列表', permission: 'service:view' },
    ],
  },
  {
    key: 'finance-management',
    icon: <DollarOutlined />,
    label: '财务管理',
    children: [
      { key: '/invoices', label: '开票管理', permission: 'invoice:view' },
      { key: '/payments', label: '收款管理', permission: 'payment:view' },
    ],
  },
  {
    key: 'document-management',
    icon: <FolderOutlined />,
    label: '文档管理',
    children: [
      { key: '/documents', label: '文档列表', permission: 'document:view' },
    ],
  },
  {
    key: 'statistics-analysis',
    icon: <BarChartOutlined />,
    label: '统计分析',
    children: [
      { key: '/statistics', label: '统计概览', permission: 'statistics:view' },
      { key: '/login-logs', label: '登录日志', permission: 'log:view' },
    ],
  },
  {
    key: 'system-settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    children: [
      { key: '/notices', label: '通知公告', permission: 'notice:view' },
      { key: '/logs', label: '操作日志', permission: 'log:view' },
    ],
  },
]

const MainLayout = () => {
  const [collapsed, setCollapsed] = useState(false)
  const [openKeys, setOpenKeys] = useState<string[]>(['user-management'])
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  // 处理菜单展开/收起 - 手风琴效果
  const handleOpenChange = (keys: string[]) => {
    // 只保留最后展开的一个菜单
    setOpenKeys(keys.length > 0 ? [keys[keys.length - 1]] : [])
  }

  // 处理登出
  const handleLogout = async () => {
    try {
      await authApi.logout()
    } finally {
      logout()
      navigate('/login')
    }
  }

  // 生成面包屑
  const breadcrumbItems = useMemo(() => {
    const items: { title: React.ReactNode }[] = [{ title: <Link to="/">首页</Link> }]
    
    const currentPath = location.pathname
    
    // 首页
    if (currentPath === '/') {
      items.push({ title: '工作台' })
      return items
    }

    // 个人中心
    if (currentPath === '/profile') {
      items.push({ title: '个人中心' })
      return items
    }
    
    // 查找匹配的菜单项
    for (const menu of menuItems) {
      if (menu.children) {
        // 有子菜单的情况
        for (const child of menu.children) {
          if (child.key === currentPath) {
            items.push({ title: menu.label })
            items.push({ title: child.label })
            return items
          }
        }
      } else {
        // 没有子菜单的情况
        if (menu.key === currentPath) {
          items.push({ title: menu.label })
          return items
        }
      }
    }
    
    // 未匹配到，显示当前路径
    items.push({ title: currentPath })
    return items
  }, [location.pathname])

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '账号设置',
      onClick: () => navigate('/profile?tab=settings'),
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <Layout className="main-layout">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="light"
        width={220}
      >
        <div className="logo">
          <SafetyCertificateOutlined />
          {!collapsed && <span className="logo-text">安全服务系统</span>}
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          openKeys={openKeys}
          onOpenChange={handleOpenChange}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <Layout>
        <Header style={{ background: colorBgContainer }} className="layout-header">
          <div className="header-left">
            <div
              className="trigger"
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </div>
            <Breadcrumb items={breadcrumbItems} />
          </div>
          
          <div className="header-right">
            <Space size={24}>
              <Badge count={5} size="small">
                <BellOutlined className="header-icon" />
              </Badge>
              
              <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                <Space className="user-info">
                  <Avatar 
                    icon={<UserOutlined />} 
                    src={user?.avatar}
                    style={{ backgroundColor: user?.avatar ? 'transparent' : '#1890ff' }}
                  />
                  <span className="username">{user?.real_name || user?.username}</span>
                </Space>
              </Dropdown>
            </Space>
          </div>
        </Header>
        
        <Content className="layout-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
