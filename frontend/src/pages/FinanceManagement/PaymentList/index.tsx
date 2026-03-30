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
  InputNumber,
  Select,
  message,
  Statistic,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  DeleteOutlined,
  MoneyCollectOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { financeApi, Payment } from '@/api/finance'
import './style.css'

const { Search } = Input
const { Option } = Select

const PaymentList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState({
    page: 1,
    page_size: 10,
    keyword: '',
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  // 获取收款列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['payments', query],
    queryFn: () => financeApi.getPayments({
      page: query.page,
      page_size: query.page_size,
    }),
  })

  const payments = data?.data?.items || []
  const total = data?.data?.total || 0

  // 计算收款总额
  const totalAmount = payments.reduce((sum, p) => sum + p.amount, 0)

  // 创建收款 mutation
  const createMutation = useMutation({
    mutationFn: financeApi.createPayment,
    onSuccess: () => {
      message.success('收款登记成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['payments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '收款登记失败')
    },
  })

  // 删除收款 mutation
  const deleteMutation = useMutation({
    mutationFn: financeApi.deletePayment,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['payments'] })
    },
  })

  // 处理创建收款
  const handleSubmit = (values: any) => {
    createMutation.mutate({
      contract_id: values.contract_id,
      invoice_id: values.invoice_id,
      amount: values.amount,
      payment_date: values.payment_date.format('YYYY-MM-DD'),
      method: values.method,
      payer_name: values.payer_name,
      voucher_no: values.voucher_no,
      remark: values.remark,
    })
  }

  const columns = [
    {
      title: '收款编号',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: '合同',
      key: 'contract',
      render: (_: any, record: Payment) => (
        <div>
          <div>{record.contract?.name}</div>
          <div className="text-gray">{record.contract?.code}</div>
        </div>
      ),
    },
    {
      title: '关联发票',
      key: 'invoice',
      render: (_: any, record: Payment) => (
        record.invoice ? (
          <div>
            <div>{record.invoice.invoice_no}</div>
            <div className="text-gray">¥{record.invoice.amount.toLocaleString()}</div>
          </div>
        ) : (
          <Tag>预收款</Tag>
        )
      ),
    },
    {
      title: '收款金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (amount: number) => (
        <span className="amount-highlight">¥{amount.toLocaleString()}</span>
      ),
    },
    {
      title: '收款日期',
      dataIndex: 'payment_date',
      key: 'payment_date',
      width: 120,
    },
    {
      title: '收款方式',
      dataIndex: 'method',
      key: 'method',
      width: 100,
      render: (method: string) => {
        const methodMap: Record<string, string> = {
          bank_transfer: '银行转账',
          cash: '现金',
          cheque: '支票',
          other: '其他',
        }
        return methodMap[method] || method
      },
    },
    {
      title: '付款方',
      dataIndex: 'payer_name',
      key: 'payer_name',
      width: 150,
    },
    {
      title: '登记人',
      key: 'recorder',
      width: 100,
      render: (_: any, record: Payment) => record.recorder?.real_name || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Payment) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => {
            Modal.confirm({
              title: '确认删除',
              content: `确定要删除收款记录 "${record.code}" 吗？`,
              onOk: () => deleteMutation.mutate(record.id),
            })
          }}
        >
          删除
        </Button>
      ),
    },
  ]

  return (
    <div className="payment-list-page">
      <Card
        title={
          <Space>
            <MoneyCollectOutlined />
            <span>收款管理</span>
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
                form.setFieldsValue({
                  payment_date: dayjs(),
                  method: 'bank_transfer',
                })
                setModalVisible(true)
              }}
            >
              登记收款
            </Button>
          </Space>
        }
      >
        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="本页收款总额"
                value={totalAmount}
                prefix="¥"
                precision={2}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="收款笔数"
                value={payments.length}
                suffix="笔"
              />
            </Card>
          </Col>
        </Row>

        {/* 搜索栏 */}
        <div className="search-bar">
          <Search
            placeholder="搜索收款编号、合同名称"
            allowClear
            value={query.keyword}
            onChange={(e) => setQuery({ ...query, keyword: e.target.value })}
            onSearch={() => setQuery({ ...query, page: 1 })}
            style={{ width: 300 }}
            prefix={<SearchOutlined />}
          />
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={payments}
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

      {/* 收款登记弹窗 */}
      <Modal
        title="登记收款"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ marginTop: -8 }}
        >
          <div className="form-section">
            <div className="form-section-title basic">关联信息</div>
            <Form.Item
              name="contract_id"
              label="合同"
              rules={[{ required: true, message: '请选择合同' }]}
            >
              <Select
                placeholder="请选择合同"
                showSearch
                optionFilterProp="children"
              >
                {/* 这里应该从后端获取合同列表 */}
                <Option value={1}>合同示例 1</Option>
                <Option value={2}>合同示例 2</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="invoice_id"
              label="关联发票（可选）"
            >
              <Select
                allowClear
                placeholder="不选则为预收款"
              >
                <Option value={1}>发票 001（未收：¥10,000）</Option>
                <Option value={2}>发票 002（未收：¥20,000）</Option>
              </Select>
            </Form.Item>
          </div>

          <div className="form-section">
            <div className="form-section-title business">收款信息</div>
            <Form.Item
              name="amount"
              label="收款金额"
              rules={[{ required: true, message: '请输入收款金额' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                prefix="¥"
                precision={2}
                min={0.01}
                placeholder="请输入收款金额"
              />
            </Form.Item>

            <Form.Item
              name="payment_date"
              label="收款日期"
              rules={[{ required: true }]}
            >
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="method"
              label="收款方式"
              rules={[{ required: true }]}
            >
              <Select>
                <Option value="bank_transfer">银行转账</Option>
                <Option value="cash">现金</Option>
                <Option value="cheque">支票</Option>
                <Option value="other">其他</Option>
              </Select>
            </Form.Item>
          </div>

          <div className="form-section">
            <div className="form-section-title other">其他信息</div>
            <Form.Item
              name="payer_name"
              label="付款方"
            >
              <Input placeholder="请输入付款方名称" />
            </Form.Item>

            <Form.Item
              name="voucher_no"
              label="凭证号"
            >
              <Input placeholder="请输入凭证号" />
            </Form.Item>

            <Form.Item
              name="remark"
              label="备注"
            >
              <Input.TextArea rows={3} placeholder="请输入备注" />
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default PaymentList
