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
  Cascader,
  Row,
  Col,
  message,
  Tooltip,
  Badge,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons'
import { companyApi, Company, CompanyQuery } from '@/api/companies'
import { userApi } from '@/api/users'
import './style.css'

const { Search } = Input
const { Option } = Select
const { TextArea } = Input

// 杭州市地区数据（区/县 -> 镇街）
const hangzhouDistricts = [
  {
    value: '上城区',
    label: '上城区',
    children: [
      { value: '湖滨街道', label: '湖滨街道' },
      { value: '清波街道', label: '清波街道' },
      { value: '望江街道', label: '望江街道' },
      { value: '南星街道', label: '南星街道' },
      { value: '紫阳街道', label: '紫阳街道' },
      { value: '小营街道', label: '小营街道' },
      { value: '四季青街道', label: '四季青街道' },
      { value: '凯旋街道', label: '凯旋街道' },
      { value: '采荷街道', label: '采荷街道' },
      { value: '闸弄口街道', label: '闸弄口街道' },
      { value: '彭埠街道', label: '彭埠街道' },
      { value: '笕桥街道', label: '笕桥街道' },
      { value: '九堡街道', label: '九堡街道' },
      { value: '丁兰街道', label: '丁兰街道' },
    ],
  },
  {
    value: '拱墅区',
    label: '拱墅区',
    children: [
      { value: '米市巷街道', label: '米市巷街道' },
      { value: '湖墅街道', label: '湖墅街道' },
      { value: '小河街道', label: '小河街道' },
      { value: '和睦街道', label: '和睦街道' },
      { value: '拱宸桥街道', label: '拱宸桥街道' },
      { value: '大关街道', label: '大关街道' },
      { value: '上塘街道', label: '上塘街道' },
      { value: '祥符街道', label: '祥符街道' },
      { value: '半山街道', label: '半山街道' },
      { value: '康桥街道', label: '康桥街道' },
      { value: '石桥街道', label: '石桥街道' },
    ],
  },
  {
    value: '西湖区',
    label: '西湖区',
    children: [
      { value: '北山街道', label: '北山街道' },
      { value: '西溪街道', label: '西溪街道' },
      { value: '灵隐街道', label: '灵隐街道' },
      { value: '翠苑街道', label: '翠苑街道' },
      { value: '文新街道', label: '文新街道' },
      { value: '古荡街道', label: '古荡街道' },
      { value: '转塘街道', label: '转塘街道' },
      { value: '留下街道', label: '留下街道' },
      { value: '蒋村街道', label: '蒋村街道' },
      { value: '三墩镇', label: '三墩镇' },
      { value: '双浦镇', label: '双浦镇' },
    ],
  },
  {
    value: '滨江区',
    label: '滨江区',
    children: [
      { value: '西兴街道', label: '西兴街道' },
      { value: '长河街道', label: '长河街道' },
      { value: '浦沿街道', label: '浦沿街道' },
    ],
  },
  {
    value: '萧山区',
    label: '萧山区',
    children: [
      { value: '城厢街道', label: '城厢街道' },
      { value: '北干街道', label: '北干街道' },
      { value: '蜀山街道', label: '蜀山街道' },
      { value: '新塘街道', label: '新塘街道' },
      { value: '楼塔镇', label: '楼塔镇' },
      { value: '河上镇', label: '河上镇' },
      { value: '戴村镇', label: '戴村镇' },
      { value: '浦阳镇', label: '浦阳镇' },
      { value: '进化镇', label: '进化镇' },
      { value: '临浦镇', label: '临浦镇' },
      { value: '义桥镇', label: '义桥镇' },
      { value: '所前镇', label: '所前镇' },
      { value: '衙前镇', label: '衙前镇' },
      { value: '瓜沥镇', label: '瓜沥镇' },
      { value: '益农镇', label: '益农镇' },
      { value: '党湾镇', label: '党湾镇' },
      { value: '靖江街道', label: '靖江街道' },
      { value: '南阳街道', label: '南阳街道' },
      { value: '闻堰街道', label: '闻堰街道' },
      { value: '宁围街道', label: '宁围街道' },
      { value: '新街街道', label: '新街街道' },
      { value: '盈丰街道', label: '盈丰街道' },
    ],
  },
  {
    value: '余杭区',
    label: '余杭区',
    children: [
      { value: '五常街道', label: '五常街道' },
      { value: '仁和街道', label: '仁和街道' },
      { value: '良渚街道', label: '良渚街道' },
      { value: '闲林街道', label: '闲林街道' },
      { value: '仓前街道', label: '仓前街道' },
      { value: '余杭街道', label: '余杭街道' },
      { value: '中泰街道', label: '中泰街道' },
      { value: '百丈镇', label: '百丈镇' },
      { value: '鸬鸟镇', label: '鸬鸟镇' },
      { value: '黄湖镇', label: '黄湖镇' },
      { value: '径山镇', label: '径山镇' },
      { value: '瓶窑镇', label: '瓶窑镇' },
    ],
  },
  {
    value: '临平区',
    label: '临平区',
    children: [
      { value: '临平街道', label: '临平街道' },
      { value: '南苑街道', label: '南苑街道' },
      { value: '东湖街道', label: '东湖街道' },
      { value: '星桥街道', label: '星桥街道' },
      { value: '乔司街道', label: '乔司街道' },
      { value: '运河街道', label: '运河街道' },
      { value: '崇贤街道', label: '崇贤街道' },
      { value: '塘栖镇', label: '塘栖镇' },
    ],
  },
  {
    value: '钱塘区',
    label: '钱塘区',
    children: [
      { value: '下沙街道', label: '下沙街道' },
      { value: '白杨街道', label: '白杨街道' },
      { value: '河庄街道', label: '河庄街道' },
      { value: '义蓬街道', label: '义蓬街道' },
      { value: '新湾街道', label: '新湾街道' },
      { value: '临江街道', label: '临江街道' },
      { value: '前进街道', label: '前进街道' },
    ],
  },
  {
    value: '富阳区',
    label: '富阳区',
    children: [
      { value: '富春街道', label: '富春街道' },
      { value: '东洲街道', label: '东洲街道' },
      { value: '春江街道', label: '春江街道' },
      { value: '鹿山街道', label: '鹿山街道' },
      { value: '银湖街道', label: '银湖街道' },
      { value: '万市镇', label: '万市镇' },
      { value: '洞桥镇', label: '洞桥镇' },
      { value: '渌渚镇', label: '渌渚镇' },
      { value: '永昌镇', label: '永昌镇' },
      { value: '里山镇', label: '里山镇' },
      { value: '常绿镇', label: '常绿镇' },
      { value: '场口镇', label: '场口镇' },
      { value: '常安镇', label: '常安镇' },
      { value: '龙门镇', label: '龙门镇' },
      { value: '新登镇', label: '新登镇' },
      { value: '胥口镇', label: '胥口镇' },
      { value: '大源镇', label: '大源镇' },
      { value: '灵桥镇', label: '灵桥镇' },
      { value: '新桐乡', label: '新桐乡' },
      { value: '上官乡', label: '上官乡' },
      { value: '环山乡', label: '环山乡' },
      { value: '湖源乡', label: '湖源乡' },
      { value: '春建乡', label: '春建乡' },
    ],
  },
  {
    value: '临安区',
    label: '临安区',
    children: [
      { value: '锦城街道', label: '锦城街道' },
      { value: '玲珑街道', label: '玲珑街道' },
      { value: '青山湖街道', label: '青山湖街道' },
      { value: '锦南街道', label: '锦南街道' },
      { value: '锦北街道', label: '锦北街道' },
      { value: '板桥镇', label: '板桥镇' },
      { value: '高虹镇', label: '高虹镇' },
      { value: '太湖源镇', label: '太湖源镇' },
      { value: '於潜镇', label: '於潜镇' },
      { value: '天目山镇', label: '天目山镇' },
      { value: '太阳镇', label: '太阳镇' },
      { value: '潜川镇', label: '潜川镇' },
      { value: '昌化镇', label: '昌化镇' },
      { value: '龙岗镇', label: '龙岗镇' },
      { value: '河桥镇', label: '河桥镇' },
      { value: '湍口镇', label: '湍口镇' },
      { value: '清凉峰镇', label: '清凉峰镇' },
      { value: '岛石镇', label: '岛石镇' },
    ],
  },
  {
    value: '桐庐县',
    label: '桐庐县',
    children: [
      { value: '旧县街道', label: '旧县街道' },
      { value: '桐君街道', label: '桐君街道' },
      { value: '城南街道', label: '城南街道' },
      { value: '凤川街道', label: '凤川街道' },
      { value: '富春江镇', label: '富春江镇' },
      { value: '横村镇', label: '横村镇' },
      { value: '分水镇', label: '分水镇' },
      { value: '瑶琳镇', label: '瑶琳镇' },
      { value: '百江镇', label: '百江镇' },
      { value: '江南镇', label: '江南镇' },
      { value: '莪山畲族乡', label: '莪山畲族乡' },
      { value: '钟山乡', label: '钟山乡' },
      { value: '新合乡', label: '新合乡' },
      { value: '合村乡', label: '合村乡' },
    ],
  },
  {
    value: '淳安县',
    label: '淳安县',
    children: [
      { value: '千岛湖镇', label: '千岛湖镇' },
      { value: '文昌镇', label: '文昌镇' },
      { value: '石林镇', label: '石林镇' },
      { value: '临岐镇', label: '临岐镇' },
      { value: '威坪镇', label: '威坪镇' },
      { value: '姜家镇', label: '姜家镇' },
      { value: '梓桐镇', label: '梓桐镇' },
      { value: '汾口镇', label: '汾口镇' },
      { value: '中洲镇', label: '中洲镇' },
      { value: '大墅镇', label: '大墅镇' },
      { value: '枫树岭镇', label: '枫树岭镇' },
      { value: '里商乡', label: '里商乡' },
      { value: '金峰乡', label: '金峰乡' },
      { value: '富文乡', label: '富文乡' },
      { value: '左口乡', label: '左口乡' },
      { value: '屏门乡', label: '屏门乡' },
      { value: '瑶山乡', label: '瑶山乡' },
      { value: '王阜乡', label: '王阜乡' },
      { value: '宋村乡', label: '宋村乡' },
      { value: '鸠坑乡', label: '鸠坑乡' },
      { value: '浪川乡', label: '浪川乡' },
      { value: '界首乡', label: '界首乡' },
      { value: '安阳乡', label: '安阳乡' },
    ],
  },
  {
    value: '建德市',
    label: '建德市',
    children: [
      { value: '新安江街道', label: '新安江街道' },
      { value: '洋溪街道', label: '洋溪街道' },
      { value: '更楼街道', label: '更楼街道' },
      { value: '莲花镇', label: '莲花镇' },
      { value: '乾潭镇', label: '乾潭镇' },
      { value: '梅城镇', label: '梅城镇' },
      { value: '杨村桥镇', label: '杨村桥镇' },
      { value: '下涯镇', label: '下涯镇' },
      { value: '大洋镇', label: '大洋镇' },
      { value: '三都镇', label: '三都镇' },
      { value: '寿昌镇', label: '寿昌镇' },
      { value: '航头镇', label: '航头镇' },
      { value: '大慈岩镇', label: '大慈岩镇' },
      { value: '大同镇', label: '大同镇' },
      { value: '李家镇', label: '李家镇' },
      { value: '钦堂乡', label: '钦堂乡' },
    ],
  },
]

const CompanyList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState<CompanyQuery>({
    page: 1,
    page_size: 10,
  })
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [editingCompany, setEditingCompany] = useState<Company | null>(null)
  const [districtValue, setDistrictValue] = useState<string[]>([]) // 级联选择器值
  const [form] = Form.useForm()

  // 获取客户列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['companies', query],
    queryFn: () => companyApi.getCompanies(query),
  })

  const companies = data?.data?.items || []
  const total = data?.data?.total || 0

  // 获取用户列表（用于负责人选择）
  const { data: usersData } = useQuery({
    queryKey: ['users', 'all'],
    queryFn: () => userApi.getUsers({ page: 1, page_size: 100 }),
  })

  const users = usersData?.data?.items || []

  // 创建客户 mutation
  const createMutation = useMutation({
    mutationFn: companyApi.createCompany,
    onSuccess: () => {
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '创建失败')
    },
  })

  // 更新客户 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Company> }) =>
      companyApi.updateCompany(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '更新失败')
    },
  })

  // 删除客户 mutation
  const deleteMutation = useMutation({
    mutationFn: companyApi.deleteCompany,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '删除失败')
    },
  })

  const statusMap: Record<string, { color: string; text: string }> = {
    potential: { color: 'default', text: '潜在客户' },
    active: { color: 'success', text: '合作中' },
    inactive: { color: 'warning', text: '暂停合作' },
    lost: { color: 'error', text: '流失客户' },
  }

  const scaleMap: Record<string, string> = {
    small: '小型 (<50人)',
    medium: '中型 (50-300人)',
    large: '大型 (300-1000人)',
    xlarge: '超大型 (>1000人)',
  }

  const columns = [
    {
      title: '企业信息',
      key: 'info',
      render: (_: any, record: Company) => (
        <div className="company-info">
          <div className="company-name">{record.name}</div>
          <div className="company-meta">
            <Tag>{record.industry || '未分类'}</Tag>
          </div>
        </div>
      ),
    },
    {
      title: '统一信用代码',
      dataIndex: 'unified_code',
      width: 180,
    },
    {
      title: '属地',
      key: 'region',
      render: (_: any, record: Company) => (
        <div className="region-info">
          <EnvironmentOutlined style={{ marginRight: 4 }} />
          {record.district}{record.street || ''}
        </div>
      ),
    },
    {
      title: '规模',
      dataIndex: 'scale',
      render: (scale: string) => scaleMap[scale] || scale,
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: string) => {
        const { color, text } = statusMap[status] || { color: 'default', text: status }
        return <Badge status={color as any} text={text} />
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
      render: (_: any, record: Company) => {
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
    const prefix = 'CUST'
    const random = Math.random().toString(36).substring(2, 6).toUpperCase()
    const timestamp = Date.now().toString(36).substring(0, 4).toUpperCase()
    return `${prefix}${timestamp}${random}`
  }

  const handleAdd = () => {
    setEditingCompany(null)
    form.resetFields()
    setDistrictValue([]) // 清空级联选择器
    // 自动生成编码
    form.setFieldsValue({ code: generateCode() })
    setModalVisible(true)
  }

  const handleView = (company: Company) => {
    setEditingCompany(company)
    setDetailVisible(true)
  }

  const handleEdit = (company: Company) => {
    setEditingCompany(company)
    form.setFieldsValue({
      ...company,
    })
    // 回显级联选择器值
    if (company.district && company.street) {
      setDistrictValue([company.district, company.street])
    } else if (company.district) {
      setDistrictValue([company.district])
    } else {
      setDistrictValue([])
    }
    setModalVisible(true)
  }

  const handleDelete = (company: Company) => {
    Modal.confirm({
      title: '删除客户',
      content: `确定要删除客户 "${company.name}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => {
        deleteMutation.mutate(company.id)
      },
    })
  }

  const handleSubmit = async (values: any) => {
    if (editingCompany) {
      updateMutation.mutate({ id: editingCompany.id, data: values })
    } else {
      createMutation.mutate(values)
    }
  }

  return (
    <div className="company-list-page">
      <Card
        title="客户管理"
        extra={
          <Space>
            <Search
              placeholder="搜索企业名称/编码"
              allowClear
              onSearch={handleSearch}
              style={{ width: 250 }}
            />
            <Tooltip title="刷新">
              <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
            </Tooltip>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增客户
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={companies}
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
        title={editingCompany ? '编辑客户' : '新增客户'}
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
                  label="企业名称"
                  rules={[{ required: true, message: '请输入企业名称' }]}
                >
                  <Input placeholder="请输入企业全称" />
                </Form.Item>
              </Col>
            </Row>
            
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item
                  name="code"
                  label="客户编码"
                  rules={[{ required: true, message: '请输入客户编码' }]}
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
                  name="short_name" 
                  label="企业简称"
                >
                  <Input placeholder="请输入企业简称" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12}>
              <Col span={24}>
                <Form.Item 
                  name="unified_code" 
                  label="统一社会信用代码"
                >
                  <Input placeholder="请输入18位统一社会信用代码" />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 业务信息区块 */}
          <div className="form-section">
            <div className="form-section-title business">业务信息</div>
            
            <Row gutter={12}>
              <Col span={8}>
                <Form.Item 
                  name="industry" 
                  label="所属行业"
                >
                  <Select placeholder="请选择行业">
                    <Option value="化工">化工</Option>
                    <Option value="制造业">制造业</Option>
                    <Option value="矿业">矿业</Option>
                    <Option value="能源">能源</Option>
                    <Option value="建筑">建筑</Option>
                    <Option value="其他">其他</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item 
                  name="scale" 
                  label="企业规模"
                >
                  <Select placeholder="请选择规模">
                    <Option value="small">小型 (&lt;50人)</Option>
                    <Option value="medium">中型 (50-300人)</Option>
                    <Option value="large">大型 (300-1000人)</Option>
                    <Option value="xlarge">超大型 (&gt;1000人)</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item 
                  name="status" 
                  label="客户状态"
                  initialValue="potential"
                >
                  <Select placeholder="请选择状态">
                    <Option value="potential">潜在客户</Option>
                    <Option value="active">合作中</Option>
                    <Option value="inactive">暂停合作</Option>
                    <Option value="lost">流失客户</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12}>
              <Col span={24}>
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

          {/* 属地信息区块 */}
          <div className="form-section">
            <div className="form-section-title location">属地信息</div>
            
            {/* 隐藏字段，用于提交数据 */}
            <Form.Item name="province" hidden><Input /></Form.Item>
            <Form.Item name="city" hidden><Input /></Form.Item>
            <Form.Item name="district" hidden><Input /></Form.Item>
            <Form.Item name="street" hidden><Input /></Form.Item>

            <Row gutter={12}>
              <Col span={24}>
                <Form.Item 
                  label="所在地区"
                  required
                >
                  <Cascader
                    value={districtValue}
                    options={hangzhouDistricts}
                    placeholder="请选择区/县、镇街"
                    onChange={(value) => {
                      setDistrictValue(value as string[])
                      if (value && value.length >= 2) {
                        const district = value[0] as string
                        const street = value[1] as string
                        form.setFieldsValue({
                          province: '浙江省',
                          city: '杭州市',
                          district: district,
                          street: street,
                          address: `浙江省杭州市${district}${street}`,
                        })
                      }
                    }}
                    style={{ width: '100%' }}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12}>
              <Col span={24}>
                <Form.Item 
                  name="address" 
                  label="详细地址"
                >
                  <TextArea 
                    rows={1}
                    placeholder="请输入详细地址（已自动填充，可补充具体门牌号）"
                  />
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
        title="客户详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {editingCompany && (
          <div className="company-detail">
            <h3>{editingCompany.name}</h3>
            <p>{editingCompany.address}</p>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default CompanyList
