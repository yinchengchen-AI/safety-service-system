import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Modal,
  Card,
  Table,
  Button,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Space,
  Tag,
  Descriptions,
  message,
  Tabs,
  Statistic,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  MoneyCollectOutlined,
  FileTextOutlined,
  PaperClipOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { Contract } from '@/api/contracts'
import { financeApi, Invoice, Payment } from '@/api/finance'
import AttachmentList from '@/components/AttachmentList'

const { TabPane } = Tabs
const { Option } = Select

interface ContractDetailModalProps {
  visible: boolean
  contract: Contract | null
  onClose: () => void
}

const ContractDetailModal = ({ visible, contract, onClose }: ContractDetailModalProps) => {
  const queryClient = useQueryClient()
  const [invoiceModalVisible, setInvoiceModalVisible] = useState(false)
  const [paymentModalVisible, setPaymentModalVisible] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [invoiceForm] = Form.useForm()
  const [paymentForm] = Form.useForm()

  if (!contract) return null

  // 获取财务汇总
  const { data: financeData, isLoading: financeLoading } = useQuery({
    queryKey: ['contract-finance', contract.id],
    queryFn: () => financeApi.getContractFinanceSummary(contract.id),
    enabled: visible && !!contract,
  })

  const finance = financeData?.data

  // 创建开票 mutation
  const createInvoiceMutation = useMutation({
    mutationFn: financeApi.createInvoice,
    onSuccess: () => {
      message.success('开票成功')
      setInvoiceModalVisible(false)
      invoiceForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['contract-finance', contract.id] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '开票失败')
    },
  })

  // 删除开票 mutation
  const deleteInvoiceMutation = useMutation({
    mutationFn: financeApi.deleteInvoice,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['contract-finance', contract.id] })
    },
  })

  // 创建收款 mutation
  const createPaymentMutation = useMutation({
    mutationFn: financeApi.createPayment,
    onSuccess: () => {
      message.success('收款登记成功')
      setPaymentModalVisible(false)
      paymentForm.resetFields()
      setSelectedInvoice(null)
      queryClient.invalidateQueries({ queryKey: ['contract-finance', contract.id] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '收款登记失败')
    },
  })

  // 删除收款 mutation
  const deletePaymentMutation = useMutation({
    mutationFn: financeApi.deletePayment,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['contract-finance', contract.id] })
    },
  })

  // 处理开票
  const handleCreateInvoice = (values: any) => {
    createInvoiceMutation.mutate({
      contract_id: contract.id,
      invoice_no: values.invoice_no,
      invoice_code: values.invoice_code,
      type: values.type,
      amount: values.amount,
      tax_amount: values.tax_amount,
      issue_date: values.issue_date.format('YYYY-MM-DD'),
      buyer_name: values.buyer_name,
      buyer_tax_no: values.buyer_tax_no,
      remark: values.remark,
    })
  }

  // 处理收款
  const handleCreatePayment = (values: any) => {
    createPaymentMutation.mutate({
      contract_id: contract.id,
      invoice_id: selectedInvoice?.id,
      amount: values.amount,
      payment_date: values.payment_date.format('YYYY-MM-DD'),
      method: values.method,
      payer_name: values.payer_name,
      voucher_no: values.voucher_no,
      remark: values.remark,
    })
  }

  // 发票表格列
  const invoiceColumns = [
    {
      title: '发票号码',
      dataIndex: 'invoice_no',
      key: 'invoice_no',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          special: '专票',
          normal: '普票',
          electronic: '电子',
        }
        return typeMap[type] || type
      },
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => `¥${amount.toLocaleString()}`,
    },
    {
      title: '已收款',
      dataIndex: 'paid_amount',
      key: 'paid_amount',
      render: (amount: number) => `¥${amount.toLocaleString()}`,
    },
    {
      title: '开票日期',
      dataIndex: 'issue_date',
      key: 'issue_date',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          issued: { color: 'green', text: '已开具' },
          sent: { color: 'blue', text: '已寄送' },
          cancelled: { color: 'red', text: '已作废' },
        }
        const s = statusMap[status] || { color: 'default', text: status }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Invoice) => (
        <Space>
          <Button
            type="link"
            size="small"
            disabled={record.paid_amount > 0}
            onClick={() => {
              if (record.paid_amount > 0) {
                message.warning('该发票已有收款记录，不能删除')
                return
              }
              deleteInvoiceMutation.mutate(record.id)
            }}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  // 收款表格列
  const paymentColumns = [
    {
      title: '收款编号',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => `¥${amount.toLocaleString()}`,
    },
    {
      title: '收款日期',
      dataIndex: 'payment_date',
      key: 'payment_date',
    },
    {
      title: '关联发票',
      dataIndex: 'invoice',
      key: 'invoice',
      render: (invoice: Invoice | null) => invoice?.invoice_no || '预收款',
    },
    {
      title: '收款方式',
      dataIndex: 'method',
      key: 'method',
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
      title: '操作',
      key: 'action',
      render: (_: any, record: Payment) => (
        <Button
          type="link"
          size="small"
          onClick={() => deletePaymentMutation.mutate(record.id)}
        >
          删除
        </Button>
      ),
    },
  ]

  return (
    <>
      <Modal
        title="合同详情"
        open={visible}
        onCancel={onClose}
        footer={null}
        width={900}
      >
        <Tabs defaultActiveKey="finance">
          <TabPane
            tab={<span><MoneyCollectOutlined /> 财务信息</span>}
            key="finance"
          >
            {/* 财务统计 */}
            <Card loading={financeLoading} style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={6}>
                  <Statistic
                    title="合同金额"
                    value={finance?.contract_amount || 0}
                    prefix="¥"
                    precision={2}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="已开票"
                    value={finance?.invoiced_amount || 0}
                    prefix="¥"
                    precision={2}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="已收款"
                    value={finance?.paid_amount || 0}
                    prefix="¥"
                    precision={2}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="未收款"
                    value={finance?.unpaid_amount || 0}
                    prefix="¥"
                    precision={2}
                    valueStyle={{ color: '#ff4d4f' }}
                  />
                </Col>
              </Row>
            </Card>

            {/* 开票记录 */}
            <Card
              title="开票记录"
              extra={
                <Button
                  type="primary"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    invoiceForm.setFieldsValue({
                      buyer_name: contract.company?.name,
                      issue_date: dayjs(),
                      type: 'special',
                    })
                    setInvoiceModalVisible(true)
                  }}
                >
                  开票
                </Button>
              }
              style={{ marginBottom: 16 }}
            >
              <Table
                dataSource={finance?.invoices as Invoice[] || []}
                columns={invoiceColumns}
                rowKey="id"
                pagination={false}
                size="small"
              />
            </Card>

            {/* 收款记录 */}
            <Card
              title="收款记录"
              extra={
                <Button
                  type="primary"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    paymentForm.setFieldsValue({
                      payment_date: dayjs(),
                      method: 'bank_transfer',
                    })
                    setSelectedInvoice(null)
                    setPaymentModalVisible(true)
                  }}
                >
                  收款
                </Button>
              }
            >
              <Table
                dataSource={finance?.payments as Payment[] || []}
                columns={paymentColumns}
                rowKey="id"
                pagination={false}
                size="small"
              />
            </Card>
          </TabPane>

          <TabPane
            tab={<span><FileTextOutlined /> 基本信息</span>}
            key="info"
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="合同编号">{contract.code}</Descriptions.Item>
              <Descriptions.Item label="合同名称">{contract.name}</Descriptions.Item>
              <Descriptions.Item label="客户">{contract.company?.name}</Descriptions.Item>
              <Descriptions.Item label="合同金额">¥{contract.amount?.toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="签订日期">{contract.sign_date}</Descriptions.Item>
              <Descriptions.Item label="到期日期">{contract.end_date}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={contract.status === 'executing' ? 'green' : 'default'}>
                  {contract.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="负责人">{contract.manager?.real_name}</Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane
            tab={<span><PaperClipOutlined /> 附件</span>}
            key="attachments"
          >
            <AttachmentList refType="contract" refId={contract.id} />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 开票弹窗 */}
      <Modal
        title="开具发票"
        open={invoiceModalVisible}
        onCancel={() => setInvoiceModalVisible(false)}
        onOk={() => invoiceForm.submit()}
        confirmLoading={createInvoiceMutation.isPending}
      >
        <Form
          form={invoiceForm}
          layout="vertical"
          onFinish={handleCreateInvoice}
        >
          <Form.Item
            name="invoice_no"
            label="发票号码"
            rules={[{ required: true, message: '请输入发票号码' }]}
          >
            <Input placeholder="请输入发票号码" />
          </Form.Item>

          <Form.Item
            name="invoice_code"
            label="发票代码"
          >
            <Input placeholder="请输入发票代码" />
          </Form.Item>

          <Form.Item
            name="type"
            label="发票类型"
            rules={[{ required: true }]}
          >
            <Select>
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
              precision={2}
              min={0.01}
              max={finance?.uninvoiced_amount}
              placeholder={`剩余可开金额: ¥${(finance?.uninvoiced_amount || 0).toLocaleString()}`}
            />
          </Form.Item>

          <Form.Item
            name="tax_amount"
            label="税额"
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="¥"
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="issue_date"
            label="开票日期"
            rules={[{ required: true }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="buyer_name"
            label="购方名称"
            rules={[{ required: true }]}
          >
            <Input placeholder="请输入购方名称" />
          </Form.Item>

          <Form.Item
            name="buyer_tax_no"
            label="购方税号"
          >
            <Input placeholder="请输入购方税号" />
          </Form.Item>

          <Form.Item
            name="remark"
            label="备注"
          >
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 收款弹窗 */}
      <Modal
        title="登记收款"
        open={paymentModalVisible}
        onCancel={() => setPaymentModalVisible(false)}
        onOk={() => paymentForm.submit()}
        confirmLoading={createPaymentMutation.isPending}
      >
        <Form
          form={paymentForm}
          layout="vertical"
          onFinish={handleCreatePayment}
        >
          <Form.Item
            name="invoice_id"
            label="关联发票（可选）"
          >
            <Select
              allowClear
              placeholder="不选则为预收款"
              onChange={(value) => {
                const invoice = finance?.invoices.find(i => i.id === value) as Invoice | undefined
                setSelectedInvoice(invoice || null)
              }}
            >
              {finance?.invoices.map(inv => (
                <Option key={inv.id} value={inv.id}>
                  {inv.invoice_no}（未收: ¥{(inv.amount - inv.paid_amount).toLocaleString()}）
                </Option>
              ))}
            </Select>
          </Form.Item>

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
              max={selectedInvoice ? selectedInvoice.amount - selectedInvoice.paid_amount : undefined}
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
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

export default ContractDetailModal
