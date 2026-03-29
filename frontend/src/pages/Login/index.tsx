import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message } from 'antd'
import { 
  UserOutlined, 
  LockOutlined, 
  SafetyCertificateOutlined,
  CheckCircleFilled,
  SafetyOutlined,
  WarningFilled
} from '@ant-design/icons'
import { useAuthStore } from '@/stores'
import { authApi } from '@/api/auth'
import './style.css'

const Login = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const res = await authApi.login({
        username: values.username,
        password: values.password,
      })

      if (res.code === 200) {
        const { access_token, refresh_token, user } = res.data
        setAuth(access_token, refresh_token, user)
        message.success('登录成功，欢迎回来！')
        navigate('/')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* 左侧装饰区域 - 大屏显示 */}
      <div className="login-decoration">
        <h2>安全生产<br />第三方服务业务管理系统</h2>
        <p>
          专业的安全生产管理服务平台，为企业提供安全评价、
          安全咨询、安全培训等全方位服务，助力企业安全生产标准化建设。
        </p>
        <div className="safety-slogan">
          <span><WarningFilled /> 安全第一</span>
          <span><CheckCircleFilled /> 预防为主</span>
          <span><SafetyOutlined /> 综合治理</span>
        </div>
      </div>

      {/* 背景装饰形状 */}
      <div className="decoration-shapes">
        <div className="shape" />
        <div className="shape" />
      </div>

      {/* 登录卡片 */}
      <Card className="login-card" bordered={false}>
        <div className="login-header">
          <div className="login-logo-wrapper">
            <div className="login-logo">
              <SafetyCertificateOutlined />
            </div>
            <div className="safety-badge">
              <SafetyOutlined />
            </div>
          </div>
          <h1 className="login-title">安全生产服务管理系统</h1>
          <p className="login-subtitle">Safety Service Management System</p>
        </div>

        <Form
          name="login"
          size="large"
          onFinish={handleSubmit}
          autoComplete="off"
          className="login-form"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入用户名"
              autoFocus
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              onPressEnter={() => {}}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              className="login-button"
            >
              {loading ? '登录中...' : '安全登录'}
            </Button>
          </Form.Item>
        </Form>

        <div className="login-footer">
          <p>© 2024 安全生产服务管理系统 · 安全可控 专业可靠</p>
          <div className="safety-tips">
            <SafetyOutlined />
            <span>系统已通过安全等级保护认证</span>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default Login
