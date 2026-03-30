import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Select,
  DatePicker,
  Switch,
  Button,
  Space,
  message,
  Row,
  Col,
  Divider,
  Radio,
} from 'antd';
import {
  SaveOutlined,
  RollbackOutlined,
  SendOutlined,
} from '@ant-design/icons';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import dayjs from 'dayjs';
import {
  createNotice,
  updateNotice,
  getNoticeDetail,
  Notice,
  noticeTypeOptions,
  noticeStatusOptions,
} from '@/api/notices';
import './style.css';

const { TextArea } = Input;
const { Option } = Select;

// 编辑器配置
const quillModules = {
  toolbar: [
    [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'color': [] }, { 'background': [] }],
    [{ 'align': [] }],
    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
    [{ 'indent': '-1' }, { 'indent': '+1' }],
    ['link', 'image'],
    ['clean']
  ],
};

const NoticeForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const isEdit = !!id;

  // 获取公告详情
  useEffect(() => {
    if (isEdit) {
      fetchNoticeDetail();
    }
  }, [id]);

  const fetchNoticeDetail = async () => {
    try {
      setLoading(true);
      const response = await getNoticeDetail(Number(id));
      const notice: Notice = response.data.data;
      
      form.setFieldsValue({
        title: notice.title,
        content: notice.content,
        summary: notice.summary,
        type: notice.type,
        expire_time: notice.expire_time ? dayjs(notice.expire_time) : null,
        is_top: notice.is_top,
        top_expire_time: notice.top_expire_time ? dayjs(notice.top_expire_time) : null,
        attachment: notice.attachment,
        status: notice.status,
      });
    } catch (error) {
      message.error('获取公告详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存公告
  const handleSave = async (publish: boolean = false) => {
    try {
      const values = await form.validateFields();
      setSubmitLoading(true);

      const data = {
        ...values,
        expire_time: values.expire_time ? values.expire_time.format('YYYY-MM-DD HH:mm:ss') : null,
        top_expire_time: values.top_expire_time ? values.top_expire_time.format('YYYY-MM-DD HH:mm:ss') : null,
        status: publish ? 'published' : (values.status || 'draft'),
      };

      if (isEdit) {
        await updateNotice(Number(id), data);
        message.success(publish ? '发布成功' : '更新成功');
      } else {
        await createNotice(data);
        message.success(publish ? '发布成功' : '保存成功');
      }

      navigate('/notices');
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请检查表单填写是否正确');
      } else {
        message.error(isEdit ? '更新失败' : '创建失败');
      }
    } finally {
      setSubmitLoading(false);
    }
  };

  // 返回列表
  const handleBack = () => {
    navigate('/notices');
  };

  return (
    <div className="notice-form-page">
      <Card
        title={isEdit ? '编辑公告' : '发布公告'}
        loading={loading}
        extra={
          <Button icon={<RollbackOutlined />} onClick={handleBack}>
            返回
          </Button>
        }
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            type: 'normal',
            status: 'draft',
            is_top: false,
          }}
        >
          {/* 基本信息区块 */}
          <div className="form-section" style={{ backgroundColor: '#f6ffed' }}>
            <div className="section-title" style={{ color: '#52c41a' }}>基本信息</div>
            
            <Row gutter={24}>
              <Col span={24}>
                <Form.Item
                  name="title"
                  label="公告标题"
                  rules={[{ required: true, message: '请输入公告标题' }]}
                >
                  <Input placeholder="请输入公告标题" maxLength={200} showCount />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={24}>
              <Col span={12}>
                <Form.Item
                  name="type"
                  label="公告类型"
                  rules={[{ required: true, message: '请选择公告类型' }]}
                >
                  <Select placeholder="请选择公告类型">
                    {noticeTypeOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="expire_time"
                  label="过期时间"
                  extra="设置后公告将在过期后自动下线"
                >
                  <DatePicker
                    showTime
                    placeholder="选择过期时间"
                    style={{ width: '100%' }}
                    format="YYYY-MM-DD HH:mm:ss"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={24}>
              <Col span={24}>
                <Form.Item
                  name="summary"
                  label="摘要"
                  extra="简要描述公告内容，用于列表展示"
                >
                  <TextArea
                    rows={3}
                    placeholder="请输入公告摘要"
                    maxLength={500}
                    showCount
                  />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 内容区块 */}
          <div className="form-section" style={{ backgroundColor: '#e6f7ff' }}>
            <div className="section-title" style={{ color: '#1890ff' }}>公告内容</div>
            
            <Form.Item
              name="content"
              label="详细内容"
              rules={[{ required: true, message: '请输入公告内容' }]}
            >
              <ReactQuill
                theme="snow"
                modules={quillModules}
                placeholder="请输入公告详细内容..."
                style={{ height: 300, marginBottom: 50 }}
              />
            </Form.Item>
          </div>

          {/* 置顶设置区块 */}
          <div className="form-section" style={{ backgroundColor: '#fff7e6' }}>
            <div className="section-title" style={{ color: '#fa8c16' }}>置顶设置</div>
            
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item
                  name="is_top"
                  label="是否置顶"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="置顶" unCheckedChildren="不置顶" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="top_expire_time"
                  label="置顶过期时间"
                  extra="设置后置顶将在过期后自动取消"
                >
                  <DatePicker
                    showTime
                    placeholder="选择置顶过期时间"
                    style={{ width: '100%' }}
                    format="YYYY-MM-DD HH:mm:ss"
                  />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* 发布设置区块 */}
          <div className="form-section" style={{ backgroundColor: '#f9f0ff' }}>
            <div className="section-title" style={{ color: '#722ed1' }}>发布设置</div>
            
            <Form.Item
              name="status"
              label="发布状态"
              rules={[{ required: true, message: '请选择发布状态' }]}
            >
              <Radio.Group>
                <Radio.Button value="draft">保存草稿</Radio.Button>
                <Radio.Button value="published">立即发布</Radio.Button>
              </Radio.Group>
            </Form.Item>
          </div>

          <Divider />

          {/* 操作按钮 */}
          <Form.Item>
            <Space size="middle">
              <Button
                type="default"
                icon={<SaveOutlined />}
                loading={submitLoading}
                onClick={() => handleSave(false)}
              >
                保存草稿
              </Button>
              <Button
                type="primary"
                icon={<SendOutlined />}
                loading={submitLoading}
                onClick={() => handleSave(true)}
              >
                {isEdit ? '更新并发布' : '立即发布'}
              </Button>
              <Button onClick={handleBack}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default NoticeForm;
