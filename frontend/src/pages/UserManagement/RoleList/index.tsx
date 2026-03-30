import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Dropdown,
  Modal,
  Form,
  Tree,
  message,
  Tooltip,
  Descriptions,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import { userApi, permissionApi } from '@/api'
import { Role, RoleQuery } from '@/types'
import './style.css'

const { Search } = Input

const RoleList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState<RoleQuery>({
    page: 1,
    page_size: 10,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
  const [form] = Form.useForm()

  // 获取角色列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['roles', query],
    queryFn: () => userApi.getRoles(query),
  })

  // 获取权限树
  const { data: permissionsData } = useQuery({
    queryKey: ['permissions', 'tree'],
    queryFn: () => permissionApi.getPermissionTree(),
  })

  const roles = data?.data?.items || []
  const total = data?.data?.total || 0
  const permissions = permissionsData?.data || []

  // 构建权限树数据 - 适配后端返回的树形结构
  const permissionTreeData = useMemo(() => {
    return permissions.map((perm) => ({
      title: perm.name,
      key: perm.id?.toString() || perm.code, // 模块节点用 id 或 code
      children: perm.children?.map((child) => ({
        title: child.name,
        key: child.code, // 实际权限用 code
      })) || [],
    }))
  }, [permissions])

  // 创建角色 mutation
  const createMutation = useMutation({
    mutationFn: userApi.createRole,
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      setSelectedPermissions([])
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
  })

  // 更新角色 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      userApi.updateRole(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
  })

  // 删除角色 mutation
  const deleteMutation = useMutation({
    mutationFn: userApi.deleteRole,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
  })

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      render: (name: string, record: Role) => (
        <div>
          <div className="role-name">{name}</div>
          <div className="role-code">{record.code}</div>
        </div>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: '权限数量',
      key: 'permissions',
      render: (_: any, record: Role) => (
        <Tag color="blue">{record.permissions?.length || 0} 项权限</Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'is_system',
      render: (isSystem: boolean) =>
        isSystem ? (
          <Tag color="red">系统内置</Tag>
        ) : (
          <Tag color="default">自定义</Tag>
        ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Role) => {
        const items = [
          {
            key: 'view',
            icon: <EyeOutlined />,
            label: '查看详情',
            onClick: () => handleView(record),
          },
          {
            key: 'edit',
            icon: <EditOutlined />,
            label: '编辑',
            disabled: record.is_system,
            onClick: () => handleEdit(record),
          },
          {
            type: 'divider' as const,
          },
          {
            key: 'delete',
            icon: <DeleteOutlined />,
            label: '删除',
            danger: true,
            disabled: record.is_system,
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

  // 生成随机编码
  const generateCode = () => {
    const prefix = 'ROLE'
    const random = Math.random().toString(36).substring(2, 6).toUpperCase()
    const timestamp = Date.now().toString(36).substring(0, 4).toUpperCase()
    return `${prefix}_${timestamp}${random}`
  }

  const handleAdd = () => {
    setEditingRole(null)
    setSelectedPermissions([])
    form.resetFields()
    // 自动生成编码
    form.setFieldsValue({ code: generateCode() })
    setModalVisible(true)
  }

  const handleView = (role: Role) => {
    setEditingRole(role)
    setDetailVisible(true)
  }

  const handleEdit = (role: Role) => {
    if (role.is_system) {
      message.warning('系统内置角色不能编辑')
      return
    }
    setEditingRole(role)
    // 设置选中的权限（用 code 作为 key）
    const selectedCodes = role.permissions?.map((p) => p.code).filter(Boolean) || []
    setSelectedPermissions(selectedCodes)
    form.setFieldsValue({
      name: role.name,
      code: role.code,
      description: role.description,
    })
    setModalVisible(true)
  }

  const handleDelete = (role: Role) => {
    if (role.is_system) {
      message.warning('系统内置角色不能删除')
      return
    }
    Modal.confirm({
      title: '删除角色',
      content: `确定要删除角色 "${role.name}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(role.id)
      },
    })
  }

  // 构建权限 ID 映射表
  const permissionIdMap = useMemo(() => {
    const map: Record<string, number> = {}
    permissions.forEach((perm) => {
      perm.children?.forEach((child) => {
        if (child.code && child.id) {
          map[child.code] = child.id
        }
      })
    })
    return map
  }, [permissions])

  const handleSubmit = async (values: any) => {
    // 从选中的 keys 中过滤出实际权限 code（包含:的是权限，如 user:view）
    const selectedCodes = selectedPermissions.filter((key) => key.includes(':'))
    // 转换为 permission_ids
    const permission_ids = selectedCodes
      .map((code) => permissionIdMap[code])
      .filter(Boolean)

    const data = {
      ...values,
      permission_ids,
    }

    if (editingRole) {
      updateMutation.mutate({ id: editingRole.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  return (
    <div className="role-list-page">
      <Card
        title="角色管理"
        extra={
          <Space>
            <Search
              placeholder="搜索角色名称/编码"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增角色
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={roles}
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
        title={editingRole ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: -8 }}>
          <div className="form-section">
            <div className="form-section-title basic">基本信息</div>
            <Form.Item
              name="name"
              label="角色名称"
              rules={[{ required: true, message: '请输入角色名称' }]}
            >
              <Input placeholder="请输入角色名称" />
            </Form.Item>

            <Form.Item
              name="code"
              label="角色编码"
              rules={[{ required: true, message: '请输入角色编码' }]}
            >
              <Input
                readOnly
                placeholder="系统自动生成"
                style={{ backgroundColor: '#f5f5f5', color: '#666' }}
              />
            </Form.Item>

            <Form.Item name="description" label="描述">
              <Input.TextArea rows={2} placeholder="请输入角色描述" />
            </Form.Item>
          </div>

          <div className="form-section">
            <div className="form-section-title business">权限配置</div>
            <Form.Item label="权限配置">
              <Tree
                checkable
                treeData={permissionTreeData}
                checkedKeys={selectedPermissions}
                onCheck={(checkedKeys) => setSelectedPermissions(checkedKeys as string[])}
              />
            </Form.Item>
          </div>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="角色详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {editingRole && (
          <>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="角色名称">{editingRole.name}</Descriptions.Item>
              <Descriptions.Item label="角色编码">{editingRole.code}</Descriptions.Item>
              <Descriptions.Item label="类型">
                {editingRole.is_system ? (
                  <Tag color="red">系统内置</Tag>
                ) : (
                  <Tag>自定义</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="权限数量">
                {editingRole.permissions?.length || 0} 项
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {editingRole.description || '-'}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <h4>权限列表</h4>
              <Space wrap style={{ marginTop: 12 }}>
                {editingRole.permissions?.map((perm) => (
                  <Tag key={perm.id} color="blue">
                    {perm.name}
                  </Tag>
                ))}
              </Space>
            </div>
          </>
        )}
      </Modal>
    </div>
  )
}

export default RoleList
