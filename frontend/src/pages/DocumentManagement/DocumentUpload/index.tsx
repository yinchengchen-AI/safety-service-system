import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Upload,
  Space,
  message,
  Row,
  Col,
  Switch,
} from 'antd'
import {
  UploadOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { documentApi } from '@/api/documents'
import type { UploadFile } from 'antd/es/upload/interface'

const { Option } = Select
const { TextArea } = Input

const DOCUMENT_TYPES = [
  { value: 'contract', label: '合同文档' },
  { value: 'report', label: '报告文档' },
  { value: 'certificate', label: '资质证书' },
  { value: 'training', label: '培训资料' },
  { value: 'policy', label: '政策法规' },
  { value: 'other', label: '其他' },
]

const ALLOWED_EXTENSIONS = [
  'pdf', 'jpg', 'jpeg', 'png', 'gif',
  'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
  'txt', 'zip', 'rar'
]

const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

const DocumentUpload = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])

  // 获取分类列表
  const { data: categoriesData } = useQuery({
    queryKey: ['documentCategories'],
    queryFn: () => documentApi.getCategories(),
  })

  const categories = categoriesData?.data || []

  // 上传 mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, values }: { file: File; values: any }) =>
      documentApi.uploadDocument(file, {
        title: values.title,
        type: values.type,
        category_id: values.category_id,
        description: values.description,
        version: values.version,
        is_public: values.is_public,
        allow_download: values.allow_download,
      }),
    onSuccess: () => {
      message.success('文档上传成功')
      navigate('/documents')
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.message || '上传失败')
    },
  })

  const beforeUpload = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      message.error(`不支持的文件类型，仅支持: ${ALLOWED_EXTENSIONS.join(', ')}`)
      return Upload.LIST_IGNORE
    }
    if (file.size > MAX_FILE_SIZE) {
      message.error('文件大小超过限制（最大100MB）')
      return Upload.LIST_IGNORE
    }
    setFileList([{ uid: '-1', name: file.name, status: 'done', originFileObj: file as any }])
    return false
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    const file = fileList[0]?.originFileObj as File | undefined
    if (!file) {
      message.error('请选择要上传的文件')
      return
    }
    uploadMutation.mutate({ file, values })
  }

  return (
    <div className="document-upload-page" style={{ padding: 24 }}>
      <Card
        title={
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/documents')}>
              返回
            </Button>
            <span>上传文档</span>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            version: '1.0',
            is_public: false,
            allow_download: true,
          }}
          style={{ maxWidth: 800 }}
        >
          {/* 基本信息区块 */}
          <div style={{ background: '#f6ffed', padding: 16, borderRadius: 8, marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, color: '#389e0d' }}>基本信息</h4>
            <Row gutter={16}>
              <Col span={16}>
                <Form.Item
                  name="title"
                  label="文档标题"
                  rules={[{ required: true, message: '请输入文档标题' }]}
                >
                  <Input placeholder="请输入文档标题" maxLength={200} showCount />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="type"
                  label="文档类型"
                  rules={[{ required: true, message: '请选择文档类型' }]}
                >
                  <Select placeholder="请选择文档类型">
                    {DOCUMENT_TYPES.map(t => (
                      <Option key={t.value} value={t.value}>{t.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="description" label="文档描述">
              <TextArea rows={3} placeholder="请输入文档描述（可选）" maxLength={500} showCount />
            </Form.Item>
          </div>

          {/* 文件信息区块 */}
          <div style={{ background: '#e6f7ff', padding: 16, borderRadius: 8, marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, color: '#096dd9' }}>文件信息</h4>
            <Form.Item
              label="上传文件"
              required
              rules={[{ required: true, message: '请选择要上传的文件' }]}
            >
              <Upload
                beforeUpload={beforeUpload}
                fileList={fileList}
                onRemove={() => setFileList([])}
                maxCount={1}
              >
                <Button icon={<UploadOutlined />}>选择文件</Button>
              </Upload>
              <div style={{ marginTop: 8, color: '#8c8c8c', fontSize: 12 }}>
                支持格式：PDF、Word、Excel、PPT、图片、压缩包、文本等<br />
                单个文件最大 100MB
              </div>
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="category_id" label="文档分类">
                  <Select placeholder="请选择分类（可选）" allowClear>
                    {categories.map(cat => (
                      <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="version" label="版本号">
                  <Input placeholder="如 1.0" maxLength={20} />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 权限设置区块 */}
          <div style={{ background: '#f9f0ff', padding: 16, borderRadius: 8, marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, color: '#531dab' }}>权限设置</h4>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="is_public"
                  label="是否公开"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="公开" unCheckedChildren="不公开" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="allow_download"
                  label="允许下载"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="允许" unCheckedChildren="不允许" defaultChecked />
                </Form.Item>
              </Col>
            </Row>
          </div>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                onClick={handleSubmit}
                loading={uploadMutation.isPending}
                disabled={fileList.length === 0}
              >
                上传文档
              </Button>
              <Button onClick={() => navigate('/documents')}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default DocumentUpload
