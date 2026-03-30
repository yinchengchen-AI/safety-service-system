import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  message,
  Skeleton,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tag,
  Space,
} from 'antd';
import {
  RollbackOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Pie } from '@ant-design/charts';
import dayjs from 'dayjs';
import { getNoticeReadStats, NoticeReadStats } from '@/api/notices';
import './style.css';

interface ReadDetail {
  user_id: number;
  username: string;
  real_name: string;
  is_read: boolean;
  read_time?: string;
}

const NoticeStats: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [stats, setStats] = useState<NoticeReadStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [readDetails, setReadDetails] = useState<ReadDetail[]>([]);

  useEffect(() => {
    if (id) {
      fetchStats();
    }
  }, [id]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await getNoticeReadStats(Number(id));
      setStats(response.data.data);
      
      // 模拟阅读详情数据（实际应从后端获取）
      generateMockDetails(response.data.data);
    } catch (error) {
      message.error('获取阅读统计失败');
    } finally {
      setLoading(false);
    }
  };

  // 生成模拟阅读详情数据
  const generateMockDetails = (statsData: NoticeReadStats) => {
    const details: ReadDetail[] = [];
    const readCount = statsData.read_count;
    const unreadCount = statsData.unread_count;
    
    // 已读用户
    for (let i = 0; i < readCount; i++) {
      details.push({
        user_id: i + 1,
        username: `user${i + 1}`,
        real_name: `用户${i + 1}`,
        is_read: true,
        read_time: dayjs().subtract(Math.floor(Math.random() * 7), 'day').format('YYYY-MM-DD HH:mm:ss'),
      });
    }
    
    // 未读用户
    for (let i = 0; i < unreadCount; i++) {
      details.push({
        user_id: readCount + i + 1,
        username: `user${readCount + i + 1}`,
        real_name: `用户${readCount + i + 1}`,
        is_read: false,
      });
    }
    
    setReadDetails(details);
  };

  const handleBack = () => {
    navigate('/notices');
  };

  if (loading) {
    return (
      <div className="notice-stats-page">
        <Card>
          <Skeleton active paragraph={{ rows: 10 }} />
        </Card>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="notice-stats-page">
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <p>统计数据加载失败</p>
            <Button type="primary" onClick={handleBack}>
              返回列表
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // 图表数据
  const pieData = [
    { type: '已读', value: stats.read_count },
    { type: '未读', value: stats.unread_count },
  ];

  const pieConfig = {
    data: pieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    color: ['#52c41a', '#ff4d4f'],
    legend: {
      position: 'bottom',
    },
  };

  const columns = [
    {
      title: '用户姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      render: (text: string, record: ReadDetail) => (
        <Space>
          <span>{text || record.username}</span>
        </Space>
      ),
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '阅读状态',
      dataIndex: 'is_read',
      key: 'is_read',
      render: (is_read: boolean) => (
        is_read ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>已读</Tag>
        ) : (
          <Tag color="error" icon={<CloseCircleOutlined />}>未读</Tag>
        )
      ),
    },
    {
      title: '阅读时间',
      dataIndex: 'read_time',
      key: 'read_time',
      render: (time: string) => time || '-',
    },
  ];

  return (
    <div className="notice-stats-page">
      <Card
        title={`公告阅读统计 - ${stats.title}`}
        extra={
          <Button icon={<RollbackOutlined />} onClick={handleBack}>
            返回
          </Button>
        }
      >
        {/* 统计卡片 */}
        <Row gutter={24} className="stats-cards">
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总人数"
                value={stats.total_users}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="已读人数"
                value={stats.read_count}
                valueStyle={{ color: '#52c41a' }}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="未读人数"
                value={stats.unread_count}
                valueStyle={{ color: '#ff4d4f' }}
                prefix={<CloseCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="阅读率"
                value={stats.read_rate}
                suffix="%"
                prefix={<EyeOutlined />}
              />
              <Progress
                percent={stats.read_rate}
                status={stats.read_rate >= 80 ? 'success' : stats.read_rate >= 50 ? 'normal' : 'exception'}
                showInfo={false}
              />
            </Card>
          </Col>
        </Row>

        {/* 图表和详情 */}
        <Row gutter={24} style={{ marginTop: 24 }}>
          <Col xs={24} lg={12}>
            <Card title="阅读分布">
              <Pie {...pieConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="阅读详情">
              <Table
                dataSource={readDetails}
                columns={columns}
                rowKey="user_id"
                pagination={{
                  pageSize: 10,
                  showQuickJumper: true,
                  showSizeChanger: true,
                }}
                scroll={{ y: 400 }}
              />
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default NoticeStats;
