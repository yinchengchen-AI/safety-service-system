import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  message,
  Modal,
  Image,
  Select,
  Tooltip,
  Form,
  Row,
  Col,
  Popconfirm,
} from 'antd'
import {
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  DownloadOutlined,
  DeleteOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FilePptOutlined,
  FileZipOutlined,
  FileTextOutlined,
  PlusOutlined,
  FolderOutlined,
  EditOutlined,
} from '@ant-design/icons'
import { documentApi, DocumentItem, DocumentCategory } from '@/api/documents'
import './style.css'

const { Search } = Input
const { Option } = Select

const DOCUMENT_TYPES = [
  { value: 'contract', label: '合同文档', color: 'blue' },
  { value: 'report', label: '报告文档', color: 'green' },
  { value: 'certificate', label: '资质证书', color: 'purple' },
  { value: 'training', label: '培训资料', color: 'orange' },
  { value: 'policy', label: '政策法规', color: 'cyan' },
  { value: 'other', label: '其他', color: 'default' },
]

const DOCUMENT_STATUS = [
  { value: 'active', label: '正常', color: 'success' },
  { value: 'archived', label: '已归档', color: 'warning' },
  { value: 'disabled', label: '已禁用', color: 'default' },
]

const DocumentList = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [query, setQuery] = useState({
    page: 1,
    page_size: 10,
    keyword: '',
    category_id: undefined as number | undefined,
    type: undefined as string | undefined,
    status: undefined as string | undefined,
  })
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewUrl, setPreviewUrl] = useState('')
  const [previewType, setPreviewType] = useState<'image' | 'pdf' | 'other'>('other')
  const [previewTitle, setPreviewTitle] = useState('')
  const [editVisible, setEditVisible] = useState(false)
  const [editingDoc, setEditingDoc] = useState<DocumentItem | null>(null)
  const [editForm] = Form.useForm()
  const [categoryModalVisible, setCategoryModalVisible] = useState(false)
  const [categoryForm] = Form.useForm()

  // 获取文档列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documents', query],
    queryFn: () => documentApi.getDocuments({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      category_id: query.category_id,
      type: query.type,
      status: query.status,
    }),
  })

  // 获取分类列表
  const { data: categoriesData } = useQuery({
    queryKey: ['documentCategories'],
    queryFn: () => documentApi.getCategories(),
  })

  const documents = data?.data?.items || []
  const total = data?.data?.total || 0
  const categories = categoriesData?.data || []

  // 删除 mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentApi.deleteDocument(id),
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: () => {
      message.error('删除失败')
    },
  })

  // 更新 mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof documentApi.updateDocument>[1] }) =>
      documentApi.updateDocument(id, data),
    onSuccess: () => {
      message.success('更新成功')
      setEditVisible(false)
      editForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: () => {
      message.error('更新失败')
    },
  })

  // 创建分类 mutation
  const createCategoryMutation = useMutation({
    mutationFn: (data: { name: string; code: string; description?: string }) =>
      documentApi.createCategory(data),
    onSuccess: () => {
      message.success('分类创建成功')
      setCategoryModalVisible(false)
      categoryForm.resetFields()
      queryClient.invalidateQueries({ queryKey: ['documentCategories'] })
    },
    onError: () => {
      message.error('分类创建失败')
    },
  })

  // 文件大小格式化
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 获取文件图标
  const getFileIcon = (fileExt: string) => {
    const ext = fileExt.toLowerCase()
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
      return <FileImageOutlined style={{ color: '#52c41a', fontSize: 24 }} />
    }
    if (ext === 'pdf') {
      return <FilePdfOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />
    }
    if (['doc', 'docx'].includes(ext)) {
      return <FileWordOutlined style={{ color: '#1890ff', fontSize: 24 }} />
    }
    if (['xls', 'xlsx'].includes(ext)) {
      return <FileExcelOutlined style={{ color: '#237804', fontSize: 24 }} />
    }
    if (['ppt', 'pptx'].includes(ext)) {
      return <FilePptOutlined style={{ color: '#fa8c16', fontSize: 24 }} />
    }
    if (['zip', 'rar', '7z'].includes(ext)) {
      return <FileZipOutlined style={{ color: '#722ed1', fontSize: 24 }} />
    }
    if (['txt', 'md'].includes(ext)) {
      return <FileTextOutlined style={{ color: '#595959', fontSize: 24 }} />
    }
    return <FileOutlined style={{ color: '#8c8c8c', fontSize: 24 }} />
  }

  // 获取文档类型标签
  const getTypeTag = (type: string) => {
    const item = DOCUMENT_TYPES.find(t => t.value === type)
    return <Tag color={item?.color || 'default'}>{item?.label || type}</Tag>
  }

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const item = DOCUMENT_STATUS.find(s => s.value === status)
    return <Tag color={item?.color || 'default'}>{item?.label || status}</Tag>
  }

  // 预览
  const handlePreview = async (record: DocumentItem) => {
    try {
      const res = await documentApi.getPreviewUrl(record.id)
      if (res.data?.preview_url) {
        const fileExt = record.file_ext.toLowerCase()
        setPreviewTitle(record.title)

        if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExt)) {
          setPreviewType('image')
          setPreviewUrl(res.data.preview_url)
          setPreviewVisible(true)
        } else if (fileExt === 'pdf') {
          setPreviewType('pdf')
          setPreviewUrl(res.data.preview_url)
          setPreviewVisible(true)
        } else {
          // 其他类型直接下载
          handleDownload(record)
        }
      }
    } catch {
      message.error('获取预览链接失败')
    }
  }

  // 下载
  const handleDownload = async (record: DocumentItem) => {
    try {
      const res = await documentApi.getDownloadUrl(record.id)
      if (res.data?.download_url) {
        const link = document.createElement('a')
        link.href = res.data.download_url
        link.download = record.file_name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    } catch {
      message.error('获取下载链接失败')
    }
  }

  // 编辑
  const handleEdit = (record: DocumentItem) => {
    setEditingDoc(record)
    editForm.setFieldsValue({
      title: record.title,
      description: record.description,
      category_id: record.category_id,
      type: record.type,
      version: record.version,
      status: record.status,
      is_public: record.is_public,
      allow_download: record.allow_download,
    })
    setEditVisible(true)
  }

  // 提交编辑
  const handleEditSubmit = async () => {
    const values = await editForm.validateFields()
    if (editingDoc) {
      updateMutation.mutate({ id: editingDoc.id, data: values })
    }
  }

  const columns = [
    {
      title: '文档',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: DocumentItem) => (
        <Space>
          {getFileIcon(record.file_ext)}
          <div>
            <div className="file-name">{text}</div>
            <div className="file-size">{formatFileSize(record.file_size)} · {record.file_name}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => getTypeTag(type),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: DocumentItem['category']) => category?.name || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '上传人',
      dataIndex: 'uploader',
      key: 'uploader',
      width: 120,
      render: (uploader: DocumentItem['uploader']) =>
        uploader?.real_name || uploader?.username || '-',
    },
    {
      title: '浏览/下载',
      key: 'counts',
      width: 120,
      render: (_: any, record: DocumentItem) => (
        <span>{record.view_count} / {record.download_count}</span>
      ),
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: DocumentItem) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Tooltip title="下载">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Popconfirm
              title="确认删除"
              description={`确定要删除 "${record.title}" 吗？`}
              onConfirm={() => deleteMutation.mutate(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <div className="document-list-page">
      <Card
        title="文档管理"
        extra={
          <Space>
            <Button icon={<FolderOutlined />} onClick={() => setCategoryModalVisible(true)}>
              分类管理
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/documents/upload')}>
              上传文档
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
          </Space>
        }
      >
        {/* 搜索栏 */}
        <div className="search-bar">
          <Row gutter={16}>
            <Col>
              <Select
                placeholder="全部分类"
                allowClear
                style={{ width: 150 }}
                value={query.category_id}
                onChange={(value) => setQuery({ ...query, category_id: value, page: 1 })}
              >
                {categories.map(cat => (
                  <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Select
                placeholder="全部类型"
                allowClear
                style={{ width: 150 }}
                value={query.type}
                onChange={(value) => setQuery({ ...query, type: value, page: 1 })}
              >
                {DOCUMENT_TYPES.map(t => (
                  <Option key={t.value} value={t.value}>{t.label}</Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Select
                placeholder="全部状态"
                allowClear
                style={{ width: 150 }}
                value={query.status}
                onChange={(value) => setQuery({ ...query, status: value, page: 1 })}
              >
                {DOCUMENT_STATUS.map(s => (
                  <Option key={s.value} value={s.value}>{s.label}</Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Search
                placeholder="搜索文档标题或文件名"
                allowClear
                value={query.keyword}
                onChange={(e) => setQuery({ ...query, keyword: e.target.value })}
                onSearch={() => setQuery({ ...query, page: 1 })}
                style={{ width: 300 }}
                prefix={<SearchOutlined />}
              />
            </Col>
          </Row>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={documents}
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

      {/* 图片预览 */}
      <Image
        style={{ display: 'none' }}
        preview={{
          visible: previewVisible && previewType === 'image',
          src: previewUrl,
          title: previewTitle,
          onVisibleChange: (visible) => {
            setPreviewVisible(visible)
            if (!visible) {
              setPreviewUrl('')
              setPreviewTitle('')
            }
          },
        }}
      />

      {/* PDF 预览 */}
      <Modal
        open={previewVisible && previewType === 'pdf'}
        title={previewTitle}
        footer={null}
        width={900}
        onCancel={() => {
          setPreviewVisible(false)
          setPreviewUrl('')
          setPreviewTitle('')
        }}
      >
        <iframe
          src={previewUrl}
          style={{ width: '100%', height: 600, border: 'none' }}
        />
      </Modal>

      {/* 编辑弹窗 */}
      <Modal
        open={editVisible}
        title="编辑文档"
        onOk={handleEditSubmit}
        onCancel={() => {
          setEditVisible(false)
          editForm.resetFields()
        }}
        confirmLoading={updateMutation.isPending}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="title"
            label="文档标题"
            rules={[{ required: true, message: '请输入文档标题' }]}
          >
            <Input placeholder="请输入文档标题" />
          </Form.Item>
          <Form.Item name="description" label="文档描述">
            <Input.TextArea rows={3} placeholder="请输入文档描述" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category_id" label="分类">
                <Select placeholder="选择分类" allowClear>
                  {categories.map(cat => (
                    <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="type" label="文档类型">
                <Select placeholder="选择类型">
                  {DOCUMENT_TYPES.map(t => (
                    <Option key={t.value} value={t.value}>{t.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="version" label="版本号">
                <Input placeholder="如 1.0" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="状态">
                <Select placeholder="选择状态">
                  {DOCUMENT_STATUS.map(s => (
                    <Option key={s.value} value={s.value}>{s.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="is_public" label="是否公开" valuePropName="checked">
                <Select>
                  <Option value={true}>公开</Option>
                  <Option value={false}>不公开</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="allow_download" label="允许下载" valuePropName="checked">
                <Select>
                  <Option value={true}>允许</Option>
                  <Option value={false}>不允许</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 分类管理弹窗 */}
      <Modal
        open={categoryModalVisible}
        title="分类管理"
        footer={null}
        onCancel={() => setCategoryModalVisible(false)}
        width={600}
      >
        <Table
          size="small"
          pagination={false}
          dataSource={categories}
          rowKey="id"
          columns={[
            { title: '分类名称', dataIndex: 'name', key: 'name' },
            { title: '编码', dataIndex: 'code', key: 'code' },
            {
              title: '操作',
              key: 'action',
              width: 100,
              render: (_: any, record: DocumentCategory) => (
                <Popconfirm
                  title="确认删除"
                  description={`确定删除分类 "${record.name}" 吗？`}
                  onConfirm={() => {
                    documentApi.deleteCategory(record.id).then(() => {
                      message.success('删除成功')
                      queryClient.invalidateQueries({ queryKey: ['documentCategories'] })
                    }).catch(() => {
                      message.error('删除失败，请检查是否有关联文档或子分类')
                    })
                  }}
                >
                  <Button type="link" danger size="small">删除</Button>
                </Popconfirm>
              ),
            },
          ]}
        />
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
          <Form form={categoryForm} layout="inline" onFinish={(values) => createCategoryMutation.mutate(values)}>
            <Form.Item
              name="name"
              rules={[{ required: true, message: '请输入分类名称' }]}
            >
              <Input placeholder="分类名称" />
            </Form.Item>
            <Form.Item
              name="code"
              rules={[{ required: true, message: '请输入分类编码' }]}
            >
              <Input placeholder="分类编码" />
            </Form.Item>
            <Form.Item name="description">
              <Input placeholder="描述（可选）" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={createCategoryMutation.isPending}>
                添加分类
              </Button>
            </Form.Item>
          </Form>
        </div>
      </Modal>
    </div>
  )
}

export default DocumentList
