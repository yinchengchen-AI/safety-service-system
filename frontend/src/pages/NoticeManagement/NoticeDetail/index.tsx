import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  Tag,
  Space,
  message,
  Skeleton,
  Divider,
  Avatar,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  RollbackOutlined,
  EditOutlined,
  PushpinOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  UserOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  getNoticeDetail,
  markNoticeRead,
  Notice,
  getNoticeTypeColor,
  getNoticeStatusColor,
  getNoticeTypeLabel,
  getNoticeStatusLabel,
} from '@/api/notices';
import './style.css';

const NoticeDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [notice, setNotice] = useState<Notice | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchNoticeDetail();
    }
  }, [id]);

  const fetchNoticeDetail = async () => {
    try {
      setLoading(true);
      const response = await getNoticeDetail(Number(id));
      setNotice(response.data.data);
    } catch (error) {
      message.error('获取公告详情失败');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/notices');
  };

  const handleEdit = () => {
    navigate(`/notices/edit/${id}`);
  };

  if (loading) {
    return (
      <div className="notice-detail-page">
        <Card>
          <Skeleton active paragraph={{ rows: 10 }} />
        </Card>
      </div>
    );
  }

  if (!notice) {
    return (
      <div className="notice-detail-page">
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <p>公告不存在或已被删除</p>
            <Button type="primary" onClick={handleBack}>
              返回列表
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="notice-detail-page">
      <Card
        extra={
          <Space>
            <Button icon={<EditOutlined />} onClick={handleEdit}>
              编辑
            </Button>
            <Button icon={<RollbackOutlined />} onClick={handleBack}>
              返回
            </Button>
          </Space>
        }
      >
        {/* 公告头部 */}
        <div className="notice-header">
          <div className="notice-title">
            {notice.is_top && (
              <PushpinOutlined className="top-icon" />
            )}
            <h1>{notice.title}</h1>
          </div>
          
          <div className="notice-meta">
            <Space size="middle" wrap>
              <Tag color={getNoticeTypeColor(notice.type)}>
                {getNoticeTypeLabel(notice.type)}
              </Tag>
              <Tag color={getNoticeStatusColor(notice.status)}>
                {getNoticeStatusLabel(notice.status)}
              </Tag>
              
              {notice.publisher && (
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  <span>{notice.publisher.real_name || notice.publisher.username}</span>
                </Space>
              )}
              
              {notice.publish_time && (
                <Space>
                  <ClockCircleOutlined />
                  <span>发布于 {dayjs(notice.publish_time).format('YYYY-MM-DD HH:mm')}</span>
                </Space>
              )}
              
              <Space>
                <EyeOutlined />
                <span>{notice.view_count} 次浏览</span>
              </Space>
            </Space>
          </div>
        </div>

        <Divider />

        {/* 公告内容 */}
        <div className="notice-content">
          {notice.summary && (
            <div className="notice-summary">
              <strong>摘要：</strong>{notice.summary}
            </div>
          )}
          
          <div
            className="notice-body"
            dangerouslySetInnerHTML={{ __html: notice.content }}
          />
        </div>

        <Divider />

        {/* 公告信息 */}
        <Row gutter={24} className="notice-info">
          <Col xs={24} sm={12} md={8}>
            <Statistic
              title="创建时间"
              value={dayjs(notice.created_at).format('YYYY-MM-DD HH:mm:ss')}
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Statistic
              title="更新时间"
              value={dayjs(notice.updated_at).format('YYYY-MM-DD HH:mm:ss')}
            />
          </Col>
          {notice.expire_time && (
            <Col xs={24} sm={12} md={8}>
              <Statistic
                title="过期时间"
                value={dayjs(notice.expire_time).format('YYYY-MM-DD HH:mm:ss')}
              />
            </Col>
          )}
        </Row>

        {/* 阅读状态 */}
        {notice.is_read !== undefined && (
          <>
            <Divider />
            <div className="notice-read-status">
              {notice.is_read ? (
                <Tag color="success">
                  您已于 {dayjs(notice.read_time).format('YYYY-MM-DD HH:mm:ss')} 阅读此公告
                </Tag>
              ) : (
                <Tag color="warning">您尚未阅读此公告</Tag>
              )}
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default NoticeDetail;
