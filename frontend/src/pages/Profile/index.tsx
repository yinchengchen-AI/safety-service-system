import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Row,
  Col,
  Form,
  Input,
  Button,
  Avatar,
  message,
  Tabs,
  List,
  Tag,
  Divider,
  Statistic,
  Descriptions,
  Upload,
  Modal,
} from 'antd'
import {
  UserOutlined,
  EditOutlined,
  LockOutlined,
  SafetyOutlined,
  MailOutlined,
  PhoneOutlined,
  HistoryOutlined,
  TeamOutlined,
  FileTextOutlined,
  CameraOutlined,
} from '@ant-design/icons'
import { useAuthStore, getAccessToken, getRefreshToken } from '@/stores'
import { authApi } from '@/api/auth'
import type { UserProfile } from '@/types'
import './style.css'

const { TabPane } = Tabs

// 头像上传前的验证
const beforeUpload = (file: File) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif'
  if (!isJpgOrPng) {
    message.error('只支持 JPG/PNG/GIF 格式的图片!')
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB!')
  }
  return isJpgOrPng && isLt5M
}

const Profile = () => {
  const queryClient = useQueryClient()
  const { setAuth } = useAuthStore()
  const [basicForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [isEditing, setIsEditing] = useState(false)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewImage, setPreviewImage] = useState('')
  const [avatarUrl, setAvatarUrl] = useState<string | undefined>(undefined)

  // 获取用户信息
  const { data: userData, isLoading } = useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => authApi.getProfile(),
  })

  // 同步头像URL
  useEffect(() => {
    if (userData?.data?.avatar) {
      setAvatarUrl(userData.data.avatar)
    }
  }, [userData])

  // 更新用户信息 mutation - 使用新的 updateProfile 接口
  const updateMutation = useMutation({
    mutationFn: (data: any) => authApi.updateProfile(data),
    onSuccess: async (res) => {
      message.success('个人信息更新成功')
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
      // 更新本地存储的用户信息
      if (res.data) {
        const token = getAccessToken() || ''
        const refreshToken = getRefreshToken() || ''
        setAuth(token, refreshToken, res.data as UserProfile)
      }
    },
    onError: () => {
      message.error('更新失败')
    },
  })

  // 修改密码 mutation
  const passwordMutation = useMutation({
    mutationFn: (data: { old_password: string; new_password: string; confirm_password: string }) => 
      authApi.updatePassword(data),
    onSuccess: () => {
      message.success('密码修改成功')
      passwordForm.resetFields()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '密码修改失败')
    },
  })

  // 设置表单值（仅在用户数据加载时设置）
  useEffect(() => {
    if (userData?.data) {
      basicForm.setFieldsValue({
        username: userData.data.username,
        real_name: userData.data.real_name,
        phone: userData.data.phone,
        email: userData.data.email,
      })
    }
  }, [userData])

  // 处理基本信息提交
  const handleBasicSubmit = (values: any) => {
    updateMutation.mutate(values)
  }

  // 处理密码修改
  const handlePasswordSubmit = (values: any) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致')
      return
    }
    passwordMutation.mutate({
      old_password: values.old_password,
      new_password: values.new_password,
      confirm_password: values.confirm_password,
    })
  }

  // 处理头像上传
  const handleAvatarChange = (info: any) => {
    if (info.file.status === 'uploading') {
      return
    }
    if (info.file.status === 'done') {
      // 上传成功，avatarUrl 已通过 mutation onSuccess 更新
    }
  }

  // 自定义上传
  const customUpload = async (options: any) => {
    const { file, onSuccess, onError } = options
    try {
      const res = await authApi.uploadAvatar(file)
      onSuccess?.(res, file)
      if (res.data?.avatar_url) {
        setAvatarUrl(res.data.avatar_url)
        // 更新本地用户信息
        const token = getAccessToken() || ''
        const refreshToken = getRefreshToken() || ''
        const profileRes = await authApi.getProfile()
        if (profileRes.data) {
          setAuth(token, refreshToken, profileRes.data as UserProfile)
          queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
        }
      }
    } catch (error: any) {
      onError?.(error)
      message.error(error.response?.data?.message || '头像上传失败')
    }
  }

  // 头像预览
  const handlePreview = () => {
    const url = avatarUrl || userData?.data?.avatar
    if (url) {
      setPreviewImage(url)
      setPreviewOpen(true)
    }
  }

  // 模拟操作日志数据
  const operationLogs = [
    { id: 1, action: '登录系统', time: '2024-01-15 09:30:00', ip: '192.168.1.100' },
    { id: 2, action: '修改客户信息', time: '2024-01-15 10:15:30', ip: '192.168.1.100' },
    { id: 3, action: '创建合同', time: '2024-01-15 14:20:00', ip: '192.168.1.100' },
    { id: 4, action: '导出报表', time: '2024-01-14 16:45:00', ip: '192.168.1.100' },
  ]

  return (
    <div className="profile-page">
      <Row gutter={24}>
        {/* 左侧用户信息卡片 */}
        <Col span={8}>
          <Card loading={isLoading} className="profile-card">
            <div className="profile-header">
              <div className="profile-avatar-wrapper">
                <Avatar
                  size={100}
                  icon={<UserOutlined />}
                  src={avatarUrl || userData?.data?.avatar}
                  className="profile-avatar"
                  onClick={handlePreview}
                  style={{ cursor: 'pointer' }}
                />
                <Upload
                  accept="image/jpeg,image/png,image/gif"
                  showUploadList={false}
                  beforeUpload={beforeUpload}
                  customRequest={customUpload}
                  onChange={handleAvatarChange}
                  className="avatar-upload"
                >
                  <div className="avatar-upload-overlay">
                    <CameraOutlined />
                    <span>更换头像</span>
                  </div>
                </Upload>
              </div>
              <h2 className="profile-name">
                {userData?.data?.real_name || userData?.data?.username}
              </h2>
              <p className="profile-role">
                {userData?.data?.roles?.map((role: string) => (
                  <Tag key={role} color="blue">{role}</Tag>
                ))}
              </p>
            </div>

            <Divider />

            <Descriptions column={1} size="small" className="profile-info">
              <Descriptions.Item label="用户名">
                {userData?.data?.username}
              </Descriptions.Item>
              <Descriptions.Item label="手机号">
                {userData?.data?.phone || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="邮箱">
                {userData?.data?.email || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="部门">
                {userData?.data?.department?.name || '-'}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <div className="profile-stats">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="负责客户"
                    value={12}
                    prefix={<TeamOutlined />}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="处理合同"
                    value={28}
                    prefix={<FileTextOutlined />}
                  />
                </Col>
              </Row>
            </div>
          </Card>
        </Col>

        {/* 右侧内容区域 */}
        <Col span={16}>
          <Card className="profile-tabs-card">
            <Tabs defaultActiveKey="basic">
              {/* 基本信息 */}
              <TabPane
                tab={<span><EditOutlined /> 基本信息</span>}
                key="basic"
              >
                <Form
                  form={basicForm}
                  layout="vertical"
                  onFinish={handleBasicSubmit}
                  className="profile-form"
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="username"
                        label="用户名"
                      >
                        <Input
                          prefix={<UserOutlined />}
                          disabled
                        />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="real_name"
                        label="真实姓名"
                      >
                        {isEditing ? (
                          <Input
                            prefix={<SafetyOutlined />}
                            placeholder="请输入真实姓名"
                          />
                        ) : (
                          <Input
                            prefix={<SafetyOutlined />}
                            placeholder="请输入真实姓名"
                            disabled
                          />
                        )}
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="phone"
                        label="手机号"
                        rules={[
                          { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误' }
                        ]}
                      >
                        {isEditing ? (
                          <Input
                            prefix={<PhoneOutlined />}
                            placeholder="请输入手机号"
                          />
                        ) : (
                          <Input
                            prefix={<PhoneOutlined />}
                            placeholder="请输入手机号"
                            disabled
                          />
                        )}
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="email"
                        label="邮箱"
                        rules={[
                          { type: 'email', message: '邮箱格式错误' }
                        ]}
                      >
                        {isEditing ? (
                          <Input
                            prefix={<MailOutlined />}
                            placeholder="请输入邮箱"
                          />
                        ) : (
                          <Input
                            prefix={<MailOutlined />}
                            placeholder="请输入邮箱"
                            disabled
                          />
                        )}
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item className="form-actions">
                    {isEditing ? (
                      <>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={updateMutation.isPending}
                        >
                          保存
                        </Button>
                        <Button
                          style={{ marginLeft: 8 }}
                          onClick={() => {
                            setIsEditing(false)
                            // 重置表单为原始值
                            if (userData?.data) {
                              basicForm.setFieldsValue({
                                username: userData.data.username,
                                real_name: userData.data.real_name,
                                phone: userData.data.phone,
                                email: userData.data.email,
                              })
                            }
                          }}
                        >
                          取消
                        </Button>
                      </>
                    ) : (
                      <Button
                        type="primary"
                        icon={<EditOutlined />}
                        onClick={() => setIsEditing(true)}
                      >
                        编辑信息
                      </Button>
                    )}
                  </Form.Item>
                </Form>
              </TabPane>

              {/* 修改密码 */}
              <TabPane
                tab={<span><LockOutlined /> 修改密码</span>}
                key="password"
              >
                <Form
                  form={passwordForm}
                  layout="vertical"
                  onFinish={handlePasswordSubmit}
                  className="profile-form"
                >
                  <Form.Item
                    name="old_password"
                    label="原密码"
                    rules={[{ required: true, message: '请输入原密码' }]}
                  >
                    <Input.Password
                      prefix={<LockOutlined />}
                      placeholder="请输入原密码"
                    />
                  </Form.Item>

                  <Form.Item
                    name="new_password"
                    label="新密码"
                    rules={[
                      { required: true, message: '请输入新密码' },
                      { min: 6, message: '密码长度至少6位' }
                    ]}
                  >
                    <Input.Password
                      prefix={<SafetyOutlined />}
                      placeholder="请输入新密码"
                    />
                  </Form.Item>

                  <Form.Item
                    name="confirm_password"
                    label="确认新密码"
                    rules={[
                      { required: true, message: '请确认新密码' }
                    ]}
                  >
                    <Input.Password
                      prefix={<SafetyOutlined />}
                      placeholder="请再次输入新密码"
                    />
                  </Form.Item>

                  <Form.Item className="form-actions">
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={passwordMutation.isPending}
                    >
                      修改密码
                    </Button>
                  </Form.Item>
                </Form>
              </TabPane>

              {/* 操作日志 */}
              <TabPane
                tab={<span><HistoryOutlined /> 操作日志</span>}
                key="logs"
              >
                <List
                  itemLayout="horizontal"
                  dataSource={operationLogs}
                  renderItem={(item) => (
                    <List.Item>
                      <List.Item.Meta
                        title={item.action}
                        description={`${item.time} · IP: ${item.ip}`}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>

      {/* 图片预览 */}
      <Modal
        open={previewOpen}
        title="头像预览"
        footer={null}
        onCancel={() => setPreviewOpen(false)}
      >
        <img alt="avatar" style={{ width: '100%' }} src={previewImage} />
      </Modal>
    </div>
  )
}

export default Profile
