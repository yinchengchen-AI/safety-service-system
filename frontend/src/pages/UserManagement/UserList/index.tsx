import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Avatar,
  Dropdown,
  Modal,
  Form,
  Select,
  message,
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  LockOutlined,
  UnlockOutlined,
  KeyOutlined,
} from '@ant-design/icons'
import { userApi, departmentApi } from '@/api'
import { User, UserQuery } from '@/types'
import './style.css'

const { Search } = Input
const { Option } = Select

interface UserFormData {
  username: string
  real_name?: string
  phone?: string
  email?: string
  password?: string
  department_id?: number
  status: 'active' | 'inactive' | 'locked'
  role_ids: number[]
}

const UserList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState<UserQuery>({
    page: 1,
    page_size: 10,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [form] = Form.useForm()

  // 获取用户列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['users', query],
    queryFn: () => userApi.getUsers(query),
  })

  // 获取部门列表
  const { data: deptsData } = useQuery({
    queryKey: ['departments', 'flat'],
    queryFn: () => departmentApi.getDepartmentsFlat(),
  })

  // 获取角色列表
  const { data: rolesData } = useQuery({
    queryKey: ['roles', 'all'],
    queryFn: () => userApi.getRoles({ page: 1, page_size: 100 }),
  })

  const users = data?.data?.items || []
  const total = data?.data?.total || 0
  const departments = deptsData?.data || []
  const roles = rolesData?.data?.items || []

  // 创建用户 mutation
  const createMutation = useMutation({
    mutationFn: userApi.createUser,
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  // 更新用户 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      userApi.updateUser(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  // 删除用户 mutation
  const deleteMutation = useMutation({
    mutationFn: userApi.deleteUser,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  // 重置密码 mutation
  const resetPasswordMutation = useMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) =>
      userApi.resetPassword(id, password),
    onSuccess: () => {
      message.success('密码重置成功，新密码为: 123456')
    },
  })

  // 切换状态 mutation
  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: 'active' | 'inactive' | 'locked' }) =>
      userApi.updateUser(id, { status }),
    onSuccess: (_, variables) => {
      message.success(variables.status === 'active' ? '已启用' : '已禁用')
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const columns = [
    {
      title: '用户',
      key: 'user',
      render: (_: any, record: User) => (
        <Space>
          <Avatar icon={record.real_name?.[0] || record.username[0]} />
          <div>
            <div className="user-name">{record.real_name || record.username}</div>
            <div className="user-username">@{record.username}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '联系方式',
      key: 'contact',
      render: (_: any, record: User) => (
        <div className="contact-info">
          {record.phone && <div>{record.phone}</div>}
          {record.email && <div>{record.email}</div>}
        </div>
      ),
    },
    {
      title: '部门',
      dataIndex: ['department', 'name'],
      render: (dept: string) => dept || '-',
    },
    {
      title: '角色',
      key: 'roles',
      render: (_: any, record: User) => (
        <Space wrap>
          {record.is_superuser ? (
            <Tag color="red">超级管理员</Tag>
          ) : (
            record.roles?.map((role) => (
              <Tag key={role.id} color="blue">
                {role.name}
              </Tag>
            ))
          )}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          active: { color: 'success', text: '正常' },
          inactive: { color: 'default', text: '禁用' },
          locked: { color: 'error', text: '锁定' },
        }
        const { color, text } = statusMap[status] || { color: 'default', text: status }
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      render: (date: string) => date ? new Date(date).toLocaleString() : '从未登录',
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: any, record: User) => {
        const items = [
          {
            key: 'edit',
            icon: <EditOutlined />,
            label: '编辑',
            onClick: () => handleEdit(record),
          },
          {
            key: 'reset',
            icon: <KeyOutlined />,
            label: '重置密码',
            onClick: () => handleResetPassword(record),
          },
          {
            type: 'divider' as const,
          },
          {
            key: 'toggle',
            icon: record.status === 'active' ? <LockOutlined /> : <UnlockOutlined />,
            label: record.status === 'active' ? '禁用' : '启用',
            onClick: () => handleToggleStatus(record),
          },
          {
            key: 'delete',
            icon: <DeleteOutlined />,
            label: '删除',
            danger: true,
            onClick: () => handleDelete(record),
          },
        ]
        return (
          <Dropdown menu={{ items }} placement="bottomRight">
            <Button type="text" icon={<MoreOutlined />} />
          </Dropdown>
        )
      },
    },
  ]

  const handleSearch = (value: string) => {
    setQuery((prev) => ({ ...prev, keyword: value, page: 1 }))
  }

  const handleRefresh = () => {
    refetch()
    message.success('刷新成功')
  }

  const handleAdd = () => {
    setEditingUser(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue({
      username: user.username,
      real_name: user.real_name,
      phone: user.phone,
      email: user.email,
      department_id: user.department_id,
      status: user.status,
      role_ids: user.roles?.map(r => r.id) || [],
    })
    setModalVisible(true)
  }

  const handleResetPassword = (user: User) => {
    Modal.confirm({
      title: '重置密码',
      content: `确定要重置用户 "${user.real_name || user.username}" 的密码吗？`,
      onOk: () => {
        resetPasswordMutation.mutate({ id: user.id, password: '123456' })
      },
    })
  }

  const handleToggleStatus = (user: User) => {
    const newStatus = user.status === 'active' ? 'inactive' : 'active'
    toggleStatusMutation.mutate({ id: user.id, status: newStatus })
  }

  const handleDelete = (user: User) => {
    Modal.confirm({
      title: '删除用户',
      content: `确定要删除用户 "${user.real_name || user.username}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(user.id)
      },
    })
  }

  const handleSubmit = async (values: UserFormData) => {
    if (editingUser) {
      updateMutation.mutate({ id: editingUser.id, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  return (
    <div className="user-list-page">
      <Card
        title="用户管理"
        extra={
          <Space>
            <Search
              placeholder="搜索用户名/姓名/手机号"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增用户
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={isLoading}
          pagination={{
            total,
            current: query.page,
            pageSize: query.page_size,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setQuery((prev) => ({ ...prev, page, page_size: pageSize || 10 }))
            },
          }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: -8 }}>
          <div className="form-section">
            <div className="form-section-title basic">基本信息</div>
            <Form.Item
              name="username"
              label="用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input disabled={!!editingUser} placeholder="请输入用户名" />
            </Form.Item>

            <Form.Item name="real_name" label="真实姓名">
              <Input placeholder="请输入真实姓名" />
            </Form.Item>

            <Form.Item name="phone" label="手机号">
              <Input placeholder="请输入手机号" />
            </Form.Item>

            <Form.Item name="email" label="邮箱">
              <Input placeholder="请输入邮箱" />
            </Form.Item>

            {!editingUser && (
              <Form.Item
                name="password"
                label="初始密码"
                rules={[{ required: true, message: '请输入初始密码' }]}
              >
                <Input.Password placeholder="请输入初始密码" />
              </Form.Item>
            )}
          </div>

          <div className="form-section">
            <div className="form-section-title business">组织信息</div>
            <Form.Item name="department_id" label="所属部门">
              <Select 
                placeholder="请选择部门" 
                allowClear
                showSearch
                optionFilterProp="children"
              >
                {departments.map((dept) => (
                  <Option key={dept.id} value={dept.id}>
                    {dept.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="role_ids" label="角色">
              <Select 
                mode="multiple" 
                placeholder="请选择角色"
                showSearch
                optionFilterProp="children"
              >
                {roles.map((role) => (
                  <Option key={role.id} value={role.id}>
                    {role.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="status" label="状态" initialValue="active">
              <Select placeholder="请选择状态">
                <Option value="active">正常</Option>
                <Option value="inactive">禁用</Option>
              </Select>
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default UserList
