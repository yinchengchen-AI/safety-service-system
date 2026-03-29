import { useState } from 'react'
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
} from '@ant-design/icons'
import { attachmentApi, Attachment } from '@/api/attachments'
import './style.css'

const { Search } = Input
const { Option } = Select

const DocumentList = () => {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState({
    page: 1,
    page_size: 10,
    ref_type: undefined as string | undefined,
    keyword: '',
  })
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewUrl, setPreviewUrl] = useState('')
  const [previewType, setPreviewType] = useState<'image' | 'pdf' | 'other'>('other')
  const [previewTitle, setPreviewTitle] = useState('')

  // 获取附件列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['attachments', query],
    queryFn: () => attachmentApi.getAttachments({
      page: query.page,
      page_size: query.page_size,
      ref_type: query.ref_type,
    }),
  })

  const attachments = data?.data?.items || []
  const total = data?.data?.total || 0

  // 删除 mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => attachmentApi.deleteAttachment(id),
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['attachments'] })
    },
    onError: () => {
      message.error('删除失败')
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
    return <FileOutlined style={{ color: '#8c8c8c', fontSize: 24 }} />
  }

  // 获取文件类型标签
  const getFileTypeTag = (refType: string) => {
    if (refType === 'contract') {
      return <Tag color="blue">合同附件</Tag>
    }
    if (refType === 'invoice') {
      return <Tag color="green">发票附件</Tag>
    }
    return <Tag>其他</Tag>
  }

  // 预览
  const handlePreview = async (record: Attachment) => {
    try {
      const res = await attachmentApi.getPreviewUrl(record.id)
      if (res.data?.preview_url) {
        const fileExt = record.file_ext.toLowerCase()
        setPreviewTitle(record.file_name)
        
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
  const handleDownload = async (record: Attachment) => {
    try {
      const res = await attachmentApi.getDownloadUrl(record.id)
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

  // 搜索过滤
  const filteredAttachments = attachments.filter(item => {
    if (query.keyword) {
      return item.file_name.toLowerCase().includes(query.keyword.toLowerCase())
    }
    return true
  })

  const columns = [
    {
      title: '文件',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text: string, record: Attachment) => (
        <Space>
          {getFileIcon(record.file_ext)}
          <div>
            <div className="file-name">{text}</div>
            <div className="file-size">{formatFileSize(record.file_size)}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'ref_type',
      key: 'ref_type',
      width: 120,
      render: (refType: string) => getFileTypeTag(refType),
    },
    {
      title: '关联信息',
      key: 'ref_info',
      width: 150,
      render: (_: any, record: Attachment) => (
        <span className="ref-info">
          {record.ref_type === 'contract' ? '合同' : '发票'} #{record.ref_id}
        </span>
      ),
    },
    {
      title: '上传人',
      dataIndex: 'uploader',
      key: 'uploader',
      width: 120,
      render: (uploader: Attachment['uploader']) =>
        uploader?.real_name || uploader?.username || '-',
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
      width: 150,
      render: (_: any, record: Attachment) => (
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
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '确认删除',
                  content: `确定要删除 "${record.file_name}" 吗？`,
                  onOk: () => deleteMutation.mutate(record.id),
                })
              }}
            />
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
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
          </Space>
        }
      >
        {/* 搜索栏 */}
        <div className="search-bar">
          <Space>
            <Select
              placeholder="全部类型"
              allowClear
              style={{ width: 150 }}
              value={query.ref_type}
              onChange={(value) => setQuery({ ...query, ref_type: value, page: 1 })}
            >
              <Option value="contract">合同附件</Option>
              <Option value="invoice">发票附件</Option>
            </Select>
            <Search
              placeholder="搜索文件名"
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
          dataSource={filteredAttachments}
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
    </div>
  )
}

export default DocumentList
