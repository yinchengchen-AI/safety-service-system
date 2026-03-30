import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Modal,
  Form,
  DatePicker,
  Select,
  Row,
  Col,
  message,
  Descriptions,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { contractApi } from '@/api/contracts'
import { userApi } from '@/api/users'
import './style.css'

const { Search } = Input
const { Option } = Select
const { TextArea } = Input

// 模拟服务数据类型
interface Service {
  id: number
  name: string
  contract_id: number
  contract_name: string
  contract_code: string
  status: 'pending' | 'executing' | 'completed' | 'cancelled'
  service_date: string
  completion_date: string | null
  content: string
  manager_name: string
}

const ServiceList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState({
    page: 1,
    page_size: 10,
    keyword: '',
    status: undefined as string | undefined,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingService, setEditingService] = useState<Service | null>(null)
  const [form] = Form.useForm()

  // 获取合同列表（用于关联选择）
  const { data: contractsData } = useQuery({
    queryKey: ['contracts', 'all'],
    queryFn: () => contractApi.getContracts({ page: 1, page_size: 100 }),
  })
  const contracts = contractsData?.data?.items || []

  // 获取用户列表
  const { data: usersData } = useQuery({
    queryKey: ['users', 'all'],
    queryFn: () => userApi.getUsers({ page: 1, page_size: 100 }),
  })
  const users = usersData?.data?.items || []

  // 模拟服务数据
  const mockServices: Service[] = [
    {
      id: 1,
      name: '安全评价现场检测',
      contract_id: 1,
      contract_name: 'A公司安全评价项目',
      contract_code: 'HT2024001',
      status: 'completed',
      service_date: '2024-01-15',
      completion_date: '2024-01-20',
      content: '对A公司生产车间进行安全检测，包括消防设施、电气安全等',
      manager_name: '张三',
    },
    {
      id: 2,
      name: '隐患排查治理',
      contract_id: 2,
      contract_name: 'B公司隐患排查',
      contract_code: 'HT2024002',
      status: 'executing',
      service_date: '2024-02-01',
      completion_date: null,
      content: '对B公司全厂进行隐患排查，制定整改方案',
      manager_name: '李四',
    },
    {
      id: 3,
      name: '安全培训',
      contract_id: 3,
      contract_name: 'C公司安全培训',
      contract_code: 'HT2024003',
      status: 'pending',
      service_date: '2024-03-01',
      completion_date: null,
      content: '为企业员工提供安全生产培训',
      manager_name: '王五',
    },
  ]

  // 模拟查询
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['services', query],
    queryFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500))
      return {
        data: {
          items: mockServices,
          total: mockServices.length,
          page: query.page,
          page_size: query.page_size,
        }
      }
    },
  })

  const services = data?.data?.items || []
  const total = data?.data?.total || 0

  // 创建服务 mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))
      return { code: 200, data: { id: Date.now(), ...data } }
    },
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })

  // 更新服务 mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      console.log('Update service', id, data)
      await new Promise(resolve => setTimeout(resolve, 500))
      return { code: 200 }
    },
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      setEditingService(null)
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })

  // 删除服务 mutation
  const deleteMutation = useMutation({
    mutationFn: async (_id: number) => {
      await new Promise(resolve => setTimeout(resolve, 500))
      return { code: 200 }
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })

  // 处理提交
  const handleSubmit = (values: any) => {
    const data = {
      ...values,
      service_date: values.service_date?.format('YYYY-MM-DD'),
      completion_date: values.completion_date?.format('YYYY-MM-DD'),
    }

    if (editingService) {
      updateMutation.mutate({ id: editingService.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const statusMap: Record<string, { color: string; text: string }> = {
    pending: { color: 'default', text: '待执行' },
    executing: { color: 'processing', text: '执行中' },
    completed: { color: 'success', text: '已完成' },
    cancelled: { color: 'error', text: '已取消' },
  }

  const columns = [
    {
      title: '服务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '关联合同',
      key: 'contract',
      render: (_: any, record: Service) => (
        <div>
          <div>{record.contract_name}</div>
          <div className="text-gray">{record.contract_code}</div>
        </div>
      ),
    },
    {
      title: '服务日期',
      dataIndex: 'service_date',
      key: 'service_date',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const s = statusMap[status] || { color: 'default', text: status }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '负责人',
      dataIndex: 'manager_name',
      key: 'manager_name',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Service) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => {
              setEditingService(record)
              setDetailVisible(true)
            }}
          >
            查看
          </Button>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingService(record)
              form.setFieldsValue({
                ...record,
                service_date: record.service_date ? dayjs(record.service_date) : null,
                completion_date: record.completion_date ? dayjs(record.completion_date) : null,
              })
              setModalVisible(true)
            }}
          >
            编辑
          </Button>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: `确定要删除服务 "${record.name}" 吗？`,
                onOk: () => deleteMutation.mutate(record.id),
              })
            }}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div className="service-list-page">
      <Card
        title={
          <Space>
            <SafetyCertificateOutlined />
            <span>服务管理</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEditingService(null)
                form.resetFields()
                setModalVisible(true)
              }}
            >
              新增服务
            </Button>
          </Space>
        }
      >
        {/* 搜索栏 */}
        <div className="search-bar">
          <Space>
            <Select
              placeholder="全部状态"
              allowClear
              style={{ width: 120 }}
              value={query.status}
              onChange={(value) => setQuery({ ...query, status: value, page: 1 })}
            >
              <Option value="pending">待执行</Option>
              <Option value="executing">执行中</Option>
              <Option value="completed">已完成</Option>
              <Option value="cancelled">已取消</Option>
            </Select>
            <Search
              placeholder="搜索服务名称、合同名称"
              allowClear
              value={query.keyword}
              onChange={(e) => setQuery({ ...query, keyword: e.target.value })}
              onSearch={() => setQuery({ ...query, page: 1 })}
              style={{ width: 300 }}
              prefix={<SearchOutlined />}
            />
          </Space>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={services}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: query.page,
            pageSize: query.page_size,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setQuery({ ...query, page, page_size: pageSize || 10 })
            },
          }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingService ? '编辑服务' : '新增服务'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          setEditingService(null)
        }}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ marginTop: -8 }}
        >
          {/* 基本信息区块 */}
          <div className="form-section">
            <div className="form-section-title basic">基本信息</div>
            
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="name"
                  label="服务名称"
                  rules={[{ required: true, message: '请输入服务名称' }]}
                >
                  <Input placeholder="请输入服务名称" />
                </Form.Item>
              </Col>
            </Row>
            
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="contract_id"
                  label="关联合同"
                  rules={[{ required: true, message: '请选择关联合同' }]}
                >
                  <Select
                    placeholder="请选择关联合同"
                    showSearch
                    optionFilterProp="children"
                  >
                    {contracts.map((contract) => (
                      <Option key={contract.id} value={contract.id}>
                        {contract.name}（{contract.code}）
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 服务信息区块 */}
          <div className="form-section">
            <div className="form-section-title business">服务信息</div>
            
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="status"
                  label="服务状态"
                  rules={[{ required: true }]}
                  initialValue="pending"
                >
                  <Select placeholder="请选择状态">
                    <Option value="pending">待执行</Option>
                    <Option value="executing">执行中</Option>
                    <Option value="completed">已完成</Option>
                    <Option value="cancelled">已取消</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="manager_id"
                  label="负责人"
                >
                  <Select
                    placeholder="请选择负责人"
                    allowClear
                  >
                    {users.map((user) => (
                      <Option key={user.id} value={user.id}>
                        {user.real_name || user.username}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="service_date"
                  label="计划服务日期"
                  rules={[{ required: true }]}
                >
                  <DatePicker 
                    style={{ width: '100%' }} 
                    placeholder="请选择日期"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="completion_date"
                  label="实际完成日期"
                >
                  <DatePicker 
                    style={{ width: '100%' }} 
                    placeholder="完成后填写"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="content"
                  label="服务内容"
                >
                  <TextArea 
                    rows={2}
                    placeholder="请输入服务内容" 
                  />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 备注信息区块 */}
          <div className="form-section">
            <div className="form-section-title other">备注信息</div>
            
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="remark"
                  label="备注"
                >
                  <TextArea 
                    rows={1}
                    placeholder="请输入备注信息" 
                  />
                </Form.Item>
              </Col>
            </Row>
          </div>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="服务详情"
        open={detailVisible}
        onCancel={() => {
          setDetailVisible(false)
          setEditingService(null)
        }}
        footer={null}
        width={600}
      >
        {editingService && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="服务名称">{editingService.name}</Descriptions.Item>
            <Descriptions.Item label="关联合同">
              {editingService.contract_name} ({editingService.contract_code})
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={statusMap[editingService.status]?.color}>
                {statusMap[editingService.status]?.text}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="服务日期">{editingService.service_date}</Descriptions.Item>
            <Descriptions.Item label="完成日期">{editingService.completion_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="负责人">{editingService.manager_name}</Descriptions.Item>
            <Descriptions.Item label="服务内容">{editingService.content}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default ServiceList
