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
  message,
  Tooltip,
  Row,
  Col,
  Statistic,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { invoiceApi, Invoice, InvoiceQuery } from '@/api/invoices'
import AttachmentList from '@/components/AttachmentList'
import './style.css'

const { Search } = Input
const { Option } = Select
const { RangePicker } = DatePicker

const InvoiceList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState<InvoiceQuery>({
    page: 1,
    page_size: 10,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null)
  const [form] = Form.useForm()

  // 获取发票列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['invoices', query],
    queryFn: () => invoiceApi.getInvoices(query),
  })

  const invoices = data?.data?.items || []
  const total = data?.data?.total || 0

  // 计算统计
  const totalAmount = invoices.reduce((sum, item) => sum + (item.amount || 0), 0)
  const pendingCount = invoices.filter((item) => item.status === 'pending').length

  // 创建发票 mutation
  const createMutation = useMutation({
    mutationFn: invoiceApi.createInvoice,
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
    },
  })

  // 更新发票 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Invoice> }) =>
      invoiceApi.updateInvoice(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
    },
  })

  // 删除发票 mutation
  const deleteMutation = useMutation({
    mutationFn: invoiceApi.deleteInvoice,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
    },
  })

  const typeMap: Record<string, string> = {
    special: '增值税专用发票',
    normal: '增值税普通发票',
    electronic: '电子发票',
  }

  const statusMap: Record<string, { color: string; text: string }> = {
    pending: { color: 'default', text: '待开具' },
    issued: { color: 'processing', text: '已开具' },
    sent: { color: 'blue', text: '已寄送' },
    received: { color: 'success', text: '已签收' },
    cancelled: { color: 'red', text: '已作废' },
    red_flushed: { color: 'orange', text: '已红冲' },
  }

  const columns = [
    {
      title: '发票号码',
      dataIndex: 'invoice_no',
      render: (no: string, record: Invoice) => (
        <div>
          <div className="invoice-no">{no}</div>
          <div className="invoice-code">代码: {record.invoice_code || '-'}</div>
        </div>
      ),
    },
    {
      title: '发票类型',
      dataIndex: 'type',
      render: (type: string) => typeMap[type] || type,
    },
    {
      title: '金额',
      key: 'amount',
      render: (_: any, record: Invoice) => (
        <div>
          <div className="invoice-amount">¥{(record.amount || 0).toLocaleString()}</div>
          <div className="invoice-tax">税额: ¥{(record.tax_amount || 0).toLocaleString()}</div>
        </div>
      ),
    },
    {
      title: '购方名称',
      dataIndex: 'buyer_name',
      ellipsis: true,
    },
    {
      title: '开票日期',
      dataIndex: 'issue_date',
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '关联合同',
      dataIndex: ['contract', 'name'],
      render: (name: string) => name || '-',
      ellipsis: true,
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
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: any, record: Invoice) => {
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

  const handleAdd = () => {
    setEditingInvoice(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleView = (invoice: Invoice) => {
    setEditingInvoice(invoice)
    setDetailVisible(true)
  }

  const handleEdit = (invoice: Invoice) => {
    setEditingInvoice(invoice)
    form.setFieldsValue({
      ...invoice,
      issue_date: invoice.issue_date ? dayjs(invoice.issue_date) : undefined,
    })
    setModalVisible(true)
  }

  const handleDelete = (invoice: Invoice) => {
    Modal.confirm({
      title: '删除发票',
      content: `确定要删除发票 "${invoice.invoice_no}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(invoice.id)
      },
    })
  }

  const handleSubmit = async (values: any) => {
    const data = {
      ...values,
      issue_date: values.issue_date?.format('YYYY-MM-DD'),
    }

    if (editingInvoice) {
      updateMutation.mutate({ id: editingInvoice.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  return (
    <div className="invoice-list-page">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="发票总额"
              value={totalAmount}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="待开票数量"
              value={pendingCount}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="发票数量"
              value={total}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="开票管理"
        extra={
          <Space>
            <Search
              placeholder="搜索发票号码/购方名称"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              申请开票
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={invoices}
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
        title={editingInvoice ? '编辑发票' : '申请开票'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="type"
            label="发票类型"
            rules={[{ required: true, message: '请选择发票类型' }]}
          >
            <Select placeholder="请选择发票类型">
              <Option value="special">增值税专用发票</Option>
              <Option value="normal">增值税普通发票</Option>
              <Option value="electronic">电子发票</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="amount"
            label="开票金额"
            rules={[{ required: true, message: '请输入开票金额' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="¥"
              placeholder="请输入开票金额"
              min={0}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="buyer_name"
            label="购方名称"
            rules={[{ required: true, message: '请输入购方名称' }]}
          >
            <Input placeholder="请输入购方名称" />
          </Form.Item>

          <Form.Item name="buyer_tax_no" label="购方税号">
            <Input placeholder="请输入购方税号" />
          </Form.Item>

          <Form.Item
            name="issue_date"
            label="开票日期"
            rules={[{ required: true, message: '请选择开票日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          {/* 编辑时显示附件管理 */}
          {editingInvoice && (
            <div style={{ marginTop: 24 }}>
              <h4>附件</h4>
              <AttachmentList
                refType="invoice"
                refId={editingInvoice.id}
              />
            </div>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default InvoiceList
