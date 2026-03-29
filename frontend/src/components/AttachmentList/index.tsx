import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Upload,
  Button,
  List,
  message,
  Modal,
  Image,
  Space,
  Typography,
  Tooltip,
  Empty,
} from 'antd'
import {
  UploadOutlined,
  DeleteOutlined,
  EyeOutlined,
  DownloadOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileOutlined,
} from '@ant-design/icons'
import { attachmentApi, Attachment } from '@/api/attachments'
import './style.css'

const { Text } = Typography

interface AttachmentListProps {
  refType: 'contract' | 'invoice'
  refId: number
  canUpload?: boolean
  canDelete?: boolean
}

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
  if (['jpg', 'jpeg', 'png'].includes(fileExt.toLowerCase())) {
    return <FileImageOutlined style={{ color: '#52c41a', fontSize: 24 }} />
  }
  if (fileExt.toLowerCase() === 'pdf') {
    return <FilePdfOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />
  }
  return <FileOutlined style={{ color: '#1890ff', fontSize: 24 }} />
}

const AttachmentList = ({
  refType,
  refId,
  canUpload = true,
  canDelete = true,
}: AttachmentListProps) => {
  const queryClient = useQueryClient()
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewUrl, setPreviewUrl] = useState('')
  const [previewType, setPreviewType] = useState<'image' | 'pdf' | 'other'>('other')

  // 获取附件列表
  const { data: attachmentsData, isLoading } = useQuery({
    queryKey: ['attachments', refType, refId],
    queryFn: () => attachmentApi.getAttachments({ ref_type: refType, ref_id: refId }),
    enabled: !!refId,
  })

  const attachments = attachmentsData?.data?.items || []

  // 上传 mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => attachmentApi.uploadAttachment(file, refType, refId),
    onSuccess: () => {
      message.success('上传成功')
      queryClient.invalidateQueries({ queryKey: ['attachments', refType, refId] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || '上传失败')
    },
  })

  // 删除 mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => attachmentApi.deleteAttachment(id),
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['attachments', refType, refId] })
    },
    onError: () => {
      message.error('删除失败')
    },
  })

  // 下载
  const handleDownload = async (attachment: Attachment) => {
    try {
      const res = await attachmentApi.getDownloadUrl(attachment.id)
      if (res.data?.download_url) {
        // 创建临时链接下载
        const link = document.createElement('a')
        link.href = res.data.download_url
        link.download = attachment.file_name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    } catch {
      message.error('获取下载链接失败')
    }
  }

  // 预览
  const handlePreview = async (attachment: Attachment) => {
    try {
      const res = await attachmentApi.getPreviewUrl(attachment.id)
      if (res.data?.preview_url) {
        const fileExt = attachment.file_ext.toLowerCase()
        
        if (['jpg', 'jpeg', 'png'].includes(fileExt)) {
          setPreviewType('image')
          setPreviewUrl(res.data.preview_url)
          setPreviewVisible(true)
        } else if (fileExt === 'pdf') {
          setPreviewType('pdf')
          setPreviewUrl(res.data.preview_url)
          setPreviewVisible(true)
        } else {
          // 其他类型直接下载
          handleDownload(attachment)
        }
      }
    } catch {
      message.error('获取预览链接失败')
    }
  }

  // 自定义上传
  const customUpload = async (options: any) => {
    const { file, onSuccess, onError } = options
    try {
      const res = await uploadMutation.mutateAsync(file)
      onSuccess?.(res, file)
    } catch (error: any) {
      onError?.(error)
    }
  }

  // 上传前验证
  const beforeUpload = (file: File) => {
    const isAllowedType = ['application/pdf', 'image/jpeg', 'image/png'].includes(file.type)
    if (!isAllowedType) {
      message.error('只支持 PDF、JPG、PNG 格式的文件!')
      return false
    }
    const isLt50M = file.size / 1024 / 1024 < 50
    if (!isLt50M) {
      message.error('文件大小不能超过 50MB!')
      return false
    }
    return true
  }

  return (
    <div className="attachment-list">
      {/* 上传按钮 */}
      {canUpload && (
        <div className="attachment-upload">
          <Upload
            customRequest={customUpload}
            beforeUpload={beforeUpload}
            showUploadList={false}
            multiple
          >
            <Button
              icon={<UploadOutlined />}
              loading={uploadMutation.isPending}
            >
              上传附件
            </Button>
          </Upload>
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
            支持 PDF、JPG、PNG，单个文件最大 50MB
          </Text>
        </div>
      )}

      {/* 附件列表 */}
      {attachments.length > 0 ? (
        <List
          className="attachment-items"
          loading={isLoading}
          dataSource={attachments}
          renderItem={(item) => (
            <List.Item
              className="attachment-item"
              actions={[
                <Tooltip title="预览" key="preview">
                  <Button
                    type="text"
                    icon={<EyeOutlined />}
                    onClick={() => handlePreview(item)}
                  />
                </Tooltip>,
                <Tooltip title="下载" key="download">
                  <Button
                    type="text"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(item)}
                  />
                </Tooltip>,
                canDelete && (
                  <Tooltip title="删除" key="delete">
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      loading={deleteMutation.isPending}
                      onClick={() => {
                        Modal.confirm({
                          title: '确认删除',
                          content: `确定要删除 "${item.file_name}" 吗？`,
                          onOk: () => deleteMutation.mutate(item.id),
                        })
                      }}
                    />
                  </Tooltip>
                ),
              ]}
            >
              <List.Item.Meta
                avatar={getFileIcon(item.file_ext)}
                title={
                  <Text
                    ellipsis={{ tooltip: item.file_name }}
                    style={{ maxWidth: 300 }}
                  >
                    {item.file_name}
                  </Text>
                }
                description={
                  <Space size={16}>
                    <Text type="secondary">{formatFileSize(item.file_size)}</Text>
                    <Text type="secondary">
                      上传人: {item.uploader?.real_name || item.uploader?.username || '-'}
                    </Text>
                    <Text type="secondary">
                      {new Date(item.created_at).toLocaleString()}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无附件"
          style={{ marginTop: 20 }}
        />
      )}

      {/* 图片预览 */}
      <Image
        style={{ display: 'none' }}
        preview={{
          visible: previewVisible && previewType === 'image',
          src: previewUrl,
          onVisibleChange: (visible) => {
            setPreviewVisible(visible)
            if (!visible) setPreviewUrl('')
          },
        }}
      />

      {/* PDF 预览 */}
      <Modal
        open={previewVisible && previewType === 'pdf'}
        title="PDF 预览"
        footer={null}
        width={800}
        onCancel={() => {
          setPreviewVisible(false)
          setPreviewUrl('')
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

export default AttachmentList
