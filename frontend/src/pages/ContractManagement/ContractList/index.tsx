import { useState } from 'react'
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
  Select,
  DatePicker,
  InputNumber,
  Row,
  Col,
  message,
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { contractApi, Contract, ContractQuery } from '@/api/contracts'
import { companyApi } from '@/api/companies'
import { userApi } from '@/api/users'
import ContractDetailModal from './ContractDetailModal'
import './style.css'

const { Search } = Input
const { Option } = Select
const { RangePicker } = DatePicker
const { TextArea } = Input

const ContractList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState<ContractQuery>({
    page: 1,
    page_size: 10,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingContract, setEditingContract] = useState<Contract | null>(null)
  const [form] = Form.useForm()

  // 获取合同列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['contracts', query],
    queryFn: () => contractApi.getContracts(query),
  })

  const contracts = data?.data?.items || []
  const total = data?.data?.total || 0

  // 获取客户列表
  const { data: companiesData } = useQuery({
    queryKey: ['companies', 'all'],
    queryFn: () => companyApi.getCompanies({ page: 1, page_size: 100 }),
  })
  const companies = companiesData?.data?.items || []

  // 获取用户列表
  const { data: usersData } = useQuery({
    queryKey: ['users', 'all'],
    queryFn: () => userApi.getUsers({ page: 1, page_size: 100 }),
  })
  const users = usersData?.data?.items || []

  // 创建合同 mutation
  const createMutation = useMutation({
    mutationFn: contractApi.createContract,
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
    },
  })

  // 更新合同 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Contract> }) =>
      contractApi.updateContract(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
    },
  })

  // 删除合同 mutation
  const deleteMutation = useMutation({
    mutationFn: contractApi.deleteContract,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
    },
  })

  const typeMap: Record<string, string> = {
    safety_evaluation: '安全评价',
    safety_consulting: '安全咨询',
    safety_training: '安全培训',
    hazard_assessment: '隐患排查',
    emergency_plan: '应急预案',
    other: '其他',
  }

  const statusMap: Record<string, { color: string; text: string }> = {
    draft: { color: 'default', text: '草稿' },
    pending: { color: 'processing', text: '待审批' },
    approved: { color: 'blue', text: '已审批' },
    signed: { color: 'cyan', text: '已签订' },
    executing: { color: 'success', text: '执行中' },
    completed: { color: 'green', text: '已完成' },
    terminated: { color: 'orange', text: '已终止' },
    expired: { color: 'red', text: '已过期' },
  }

  const columns = [
    {
      title: '合同信息',
      key: 'info',
      render: (_: any, record: Contract) => (
        <div className="contract-info">
          <div className="contract-name">{record.name}</div>
          <div className="contract-meta">
            <span className="contract-code">{record.code}</span>
            <Tag>{typeMap[record.type]}</Tag>
          </div>
        </div>
      ),
    },
    {
      title: '客户',
      dataIndex: ['company', 'name'],
      ellipsis: true,
    },
    {
      title: '合同金额',
      dataIndex: 'amount',
      render: (amount: number) => `¥${amount?.toLocaleString() || 0}`,
    },
    {
      title: '合同期限',
      key: 'period',
      render: (_: any, record: Contract) => (
        <div className="contract-period">
          <div>{record.start_date ? dayjs(record.start_date).format('YYYY-MM-DD') : '-'}</div>
          <div className="period-separator">至</div>
          <div>{record.end_date ? dayjs(record.end_date).format('YYYY-MM-DD') : '-'}</div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: string) => {
        const { color, text } = statusMap[status] || { color: 'default', text: status }
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '负责人',
      dataIndex: ['manager', 'real_name'],
      render: (name: string) => name || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: any, record: Contract) => {
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
    const prefix = 'HT'
    const random = Math.random().toString(36).substring(2, 6).toUpperCase()
    const timestamp = Date.now().toString(36).substring(0, 4).toUpperCase()
    return `${prefix}${timestamp}${random}`
  }

  const handleAdd = () => {
    setEditingContract(null)
    form.resetFields()
    // 自动生成编码
    form.setFieldsValue({ code: generateCode() })
    setModalVisible(true)
  }

  const handleView = (contract: Contract) => {
    setEditingContract(contract)
    setDetailVisible(true)
  }

  const handleEdit = (contract: Contract) => {
    setEditingContract(contract)
    form.setFieldsValue({
      ...contract,
      dates: contract.start_date && contract.end_date 
        ? [dayjs(contract.start_date), dayjs(contract.end_date)] 
        : undefined,
    })
    setModalVisible(true)
  }

  const handleDelete = (contract: Contract) => {
    Modal.confirm({
      title: '删除合同',
      content: `确定要删除合同 "${contract.name}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(contract.id)
      },
    })
  }

  const handleSubmit = async (values: any) => {
    const data = {
      ...values,
      start_date: values.dates?.[0]?.format('YYYY-MM-DD'),
      end_date: values.dates?.[1]?.format('YYYY-MM-DD'),
    }
    delete data.dates

    if (editingContract) {
      updateMutation.mutate({ id: editingContract.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  return (
    <div className="contract-list-page">
      <Card
        title="合同管理"
        extra={
          <Space>
            <Search
              placeholder="搜索合同名称/编号"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增合同
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={contracts}
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
        title={editingContract ? '编辑合同' : '新增合同'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
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
                  label="合同名称"
                  rules={[{ required: true, message: '请输入合同名称' }]}
                >
                  <Input placeholder="请输入合同名称" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="code"
                  label="合同编号"
                  rules={[{ required: true, message: '请输入合同编号' }]}
                >
                  <Input 
                    readOnly 
                    placeholder="系统自动生成" 
                    style={{ backgroundColor: '#f5f5f5', color: '#666' }}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="type"
                  label="合同类型"
                  rules={[{ required: true, message: '请选择合同类型' }]}
                >
                  <Select placeholder="请选择合同类型">
                    <Option value="safety_evaluation">安全评价</Option>
                    <Option value="safety_consulting">安全咨询</Option>
                    <Option value="safety_training">安全培训</Option>
                    <Option value="hazard_assessment">隐患排查</Option>
                    <Option value="emergency_plan">应急预案</Option>
                    <Option value="other">其他</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="company_id"
                  label="签约客户"
                  rules={[{ required: true, message: '请选择签约客户' }]}
                >
                  <Select
                    placeholder="请选择签约客户"
                    showSearch
                    optionFilterProp="children"
                  >
                    {companies.map((company) => (
                      <Option key={company.id} value={company.id}>
                        {company.name}
                      </Option>
                    ))}
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
          </div>

          {/* 合同信息区块 */}
          <div className="form-section">
            <div className="form-section-title business">合同信息</div>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="amount"
                  label="合同金额"
                  rules={[{ required: true, message: '请输入合同金额' }]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    prefix="¥"
                    placeholder="请输入合同金额"
                    min={0}
                    precision={2}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="status"
                  label="合同状态"
                  initialValue="draft"
                >
                  <Select placeholder="请选择状态">
                    <Option value="draft">草稿</Option>
                    <Option value="pending">待审批</Option>
                    <Option value="approved">已审批</Option>
                    <Option value="signed">已签订</Option>
                    <Option value="executing">执行中</Option>
                    <Option value="completed">已完成</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="dates"
                  label="合同期限"
                  rules={[{ required: true, message: '请选择合同期限' }]}
                >
                  <RangePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 服务信息区块 */}
          <div className="form-section">
            <div className="form-section-title location">服务信息</div>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="service_times"
                  label="服务次数"
                  rules={[{ required: true, message: '请输入服务次数' }]}
                  initialValue={1}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="请输入服务次数"
                    min={1}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="service_cycle"
                  label="服务周期"
                >
                  <Select placeholder="请选择服务周期" allowClear>
                    <Option value="once">一次性</Option>
                    <Option value="monthly">月度</Option>
                    <Option value="quarterly">季度</Option>
                    <Option value="yearly">年度</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="service_content"
                  label="服务内容"
                >
                  <TextArea rows={2} placeholder="请输入服务内容" />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 其他信息区块 */}
          <div className="form-section">
            <div className="form-section-title other">其他信息</div>
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="payment_terms"
                  label="付款条款"
                >
                  <Select placeholder="请选择付款条款" allowClear>
                    <Option value="prepay">预付全款</Option>
                    <Option value="prepay_50">预付50%</Option>
                    <Option value="postpay">后付全款</Option>
                    <Option value="installment">分期付款</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col span={24}>
                <Form.Item
                  name="remark"
                  label="备注"
                >
                  <TextArea rows={1} placeholder="请输入备注信息" />
                </Form.Item>
              </Col>
            </Row>
          </div>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <ContractDetailModal
        visible={detailVisible}
        contract={editingContract}
        onClose={() => setDetailVisible(false)}
      />
    </div>
  )
}

export default ContractList
