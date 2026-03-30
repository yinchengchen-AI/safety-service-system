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
  TreeSelect,
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
  ApartmentOutlined,
  DownOutlined,
  RightOutlined,
} from '@ant-design/icons'
import { departmentApi } from '@/api'
import { Department } from '@/api/departments'
import './style.css'

const { Search } = Input

const DepartmentList = () => {
  const queryClient = useQueryClient()
  const [searchText, setSearchText] = useState('')
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [tableKey, setTableKey] = useState(0) // 用于强制表格重新渲染
  const [form] = Form.useForm()

  // 获取部门树形列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['departments', 'tree'],
    queryFn: () => departmentApi.getDepartments(),
    staleTime: 0, // 确保数据总是最新的
  })

  // 获取部门扁平列表（用于下拉选择）
  const { data: flatDeptsData } = useQuery({
    queryKey: ['departments', 'flat'],
    queryFn: () => departmentApi.getDepartmentsFlat(),
  })

  const departments = data?.data || []
  const flatDepts = flatDeptsData?.data || []

  // 过滤并构建表格数据（深拷贝避免修改原始数据）
  const tableData = useMemo(() => {
    const filterDepts = (depts: Department[]): Department[] => {
      if (!searchText) return depts
      
      return depts.filter((dept) => {
        const match = dept.name.toLowerCase().includes(searchText.toLowerCase()) ||
          dept.code.toLowerCase().includes(searchText.toLowerCase())
        if (match) return true
        if (dept.children && dept.children.length > 0) {
          const filteredChildren = filterDepts(dept.children)
          return filteredChildren.length > 0
        }
        return false
      })
    }
    
    // 深拷贝避免修改原始数据
    const copyDepts = JSON.parse(JSON.stringify(departments))
    return filterDepts(copyDepts)
  }, [departments, searchText])

  // 将部门列表转换为 TreeSelect 所需格式
  const deptTreeData = useMemo(() => {
    const convert = (depts: Department[]): any[] => {
      return depts.map((dept) => ({
        title: dept.name,
        value: dept.id,
        key: dept.id,
        children: dept.children ? convert(dept.children) : undefined,
      }))
    }
    return convert(departments)
  }, [departments])

  // 创建部门 mutation
  const createMutation = useMutation({
    mutationFn: departmentApi.createDepartment,
    onSuccess: async () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      await queryClient.invalidateQueries({ queryKey: ['departments'], refetchType: 'all' })
      await refetch()
      setTableKey(prev => prev + 1)
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '创建失败')
    },
  })

  // 更新部门 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Department> }) =>
      departmentApi.updateDepartment(id, data),
    onSuccess: async () => {
      message.success('更新成功')
      setModalVisible(false)
      await queryClient.invalidateQueries({ queryKey: ['departments'], refetchType: 'all' })
      await refetch()
      setTableKey(prev => prev + 1)
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '更新失败')
    },
  })

  // 删除部门 mutation
  const deleteMutation = useMutation({
    mutationFn: departmentApi.deleteDepartment,
    onSuccess: async () => {
      message.success('删除成功')
      // 强制刷新所有部门相关查询
      await queryClient.invalidateQueries({ queryKey: ['departments'], refetchType: 'all' })
      await refetch()
      // 强制表格重新渲染
      setTableKey(prev => prev + 1)
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '删除失败')
    },
  })

  // 判断是否有子部门
  const hasChildren = (record: Department): boolean => {
    return !!(record.children && Array.isArray(record.children) && record.children.length > 0)
  }

  const columns = [
    {
      title: '部门名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Department) => (
        <Space>
          <ApartmentOutlined style={{ color: '#1890ff' }} />
          <span>{name}</span>
          {hasChildren(record) && (
            <Tag color="blue">{record.children!.length} 个子部门</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '部门编码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Department) => {
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
            disabled: hasChildren(record),
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
    setSearchText(value)
  }

  const handleRefresh = () => {
    refetch()
    message.success('刷新成功')
  }

  // 生成随机编码
  const generateCode = () => {
    const prefix = 'DEPT'
    const random = Math.random().toString(36).substring(2, 6).toUpperCase()
    const timestamp = Date.now().toString(36).substring(0, 4).toUpperCase()
    return `${prefix}_${timestamp}${random}`
  }

  const handleAdd = () => {
    setEditingDept(null)
    form.resetFields()
    // 自动生成编码
    form.setFieldsValue({ code: generateCode() })
    setModalVisible(true)
  }

  const handleView = (dept: Department) => {
    setEditingDept(dept)
    setDetailVisible(true)
  }

  const handleEdit = (dept: Department) => {
    setEditingDept(dept)
    form.setFieldsValue({
      name: dept.name,
      code: dept.code,
      parent_id: dept.parent_id,
      sort_order: dept.sort_order,
      description: dept.description,
    })
    setModalVisible(true)
  }

  const handleDelete = (dept: Department) => {
    if (hasChildren(dept)) {
      message.warning('该部门下有子部门，请先删除子部门')
      return
    }
    Modal.confirm({
      title: '删除部门',
      content: `确定要删除部门 "${dept.name}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(dept.id)
      },
    })
  }

  const handleSubmit = async (values: any) => {
    if (editingDept) {
      updateMutation.mutate({ id: editingDept.id, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  return (
    <div className="department-list-page">
      <Card
        title="部门管理"
        extra={
          <Space>
            <Search
              placeholder="搜索部门名称/编码"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增部门
            </Button>
          </Space>
        }
      >
        <Table
          key={tableKey}
          columns={columns}
          dataSource={tableData}
          rowKey={(record) => `dept-${record.id}`}
          loading={isLoading}
          pagination={false}
          expandable={{
            defaultExpandAllRows: false,
            childrenColumnName: 'children',
            expandIcon: ({ expanded, onExpand, record }) => {
              // 没有子部门时不显示展开图标
              if (!hasChildren(record)) {
                return <span style={{ display: 'inline-block', width: 24 }} />
              }
              return (
                <span
                  onClick={(e) => onExpand!(record, e!)}
                  style={{
                    cursor: 'pointer',
                    padding: '0 8px',
                    color: '#8c8c8c',
                    display: 'inline-flex',
                    alignItems: 'center',
                  }}
                >
                  {expanded ? <DownOutlined /> : <RightOutlined />}
                </span>
              )
            },
          }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingDept ? '编辑部门' : '新增部门'}
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
              name="name"
              label="部门名称"
              rules={[{ required: true, message: '请输入部门名称' }]}
            >
              <Input placeholder="请输入部门名称" />
            </Form.Item>

            <Form.Item
              name="code"
              label="部门编码"
              rules={[{ required: true, message: '请输入部门编码' }]}
            >
              <Input
                readOnly
                placeholder="系统自动生成"
                style={{ backgroundColor: '#f5f5f5', color: '#666' }}
              />
            </Form.Item>
          </div>

          <div className="form-section">
            <div className="form-section-title other">其他信息</div>
            <Form.Item name="parent_id" label="上级部门">
              <TreeSelect
                treeData={deptTreeData}
                placeholder="请选择上级部门（不选则为顶级部门）"
                allowClear
                treeDefaultExpandAll
                disabled={editingDept?.id === 1} // 根部门不能修改上级
              />
            </Form.Item>

            <Form.Item name="sort_order" label="排序" initialValue={0}>
              <Input type="number" placeholder="请输入排序号，数字越小越靠前" />
            </Form.Item>

            <Form.Item name="description" label="描述">
              <Input.TextArea rows={3} placeholder="请输入部门描述" />
            </Form.Item>
          </div>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="部门详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={500}
      >
        {editingDept && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="部门名称">{editingDept.name}</Descriptions.Item>
            <Descriptions.Item label="部门编码">{editingDept.code}</Descriptions.Item>
            <Descriptions.Item label="上级部门">
              {editingDept.parent_id 
                ? flatDepts.find(d => d.id === editingDept.parent_id)?.name || '-' 
                : <Tag>顶级部门</Tag>
              }
            </Descriptions.Item>
            <Descriptions.Item label="排序">{editingDept.sort_order}</Descriptions.Item>
            <Descriptions.Item label="描述">{editingDept.description || '-'}</Descriptions.Item>
            <Descriptions.Item label="子部门数量">
              {editingDept.children?.length || 0} 个
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default DepartmentList
