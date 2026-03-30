import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Input,
  Select,
  Tag,
  Space,
  Tooltip,
  message,
  Popconfirm,
  Badge,
  Typography,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  PushpinOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { useRef } from 'react';
import {
  getNoticeList,
  deleteNotice,
  Notice,
  noticeTypeOptions,
  noticeStatusOptions,
  getNoticeTypeColor,
  getNoticeStatusColor,
  getNoticeTypeLabel,
  getNoticeStatusLabel,
} from '@/api/notices';
import { useAuthStore } from '@/stores/authStore';
import './style.css';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

const NoticeList: React.FC = () => {
  const navigate = useNavigate();
  const actionRef = useRef<ActionType>();
  const { user } = useAuthStore();
  const [keyword, setKeyword] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  const isAdmin = user?.is_superuser || user?.roles?.some((r: any) => r.code === 'admin');

  // 获取公告列表
  const fetchNotices = async (params: any) => {
    try {
      const response = await getNoticeList({
        keyword: params.keyword || keyword,
        type: typeFilter,
        status: statusFilter,
        page: params.current || 1,
        page_size: params.pageSize || 10,
      });
      return {
        data: response.data.data.items || [],
        success: true,
        total: response.data.data.total || 0,
      };
    } catch (error) {
      message.error('获取公告列表失败');
      return {
        data: [],
        success: false,
        total: 0,
      };
    }
  };

  // 删除公告
  const handleDelete = async (id: number) => {
    try {
      await deleteNotice(id);
      message.success('删除成功');
      actionRef.current?.reload();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 查看公告
  const handleView = (id: number) => {
    navigate(`/notices/detail/${id}`);
  };

  // 编辑公告
  const handleEdit = (id: number) => {
    navigate(`/notices/edit/${id}`);
  };

  // 创建公告
  const handleCreate = () => {
    navigate('/notices/create');
  };

  // 查看统计
  const handleStats = (id: number) => {
    navigate(`/notices/stats/${id}`);
  };

  const columns: ProColumns<Notice>[] = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (text: any, record: Notice) => (
        <Space>
          {record.is_top && (
            <Tooltip title="置顶">
              <PushpinOutlined style={{ color: '#ff4d4f' }} />
            </Tooltip>
          )}
          <Text strong={record.is_top}>{text}</Text>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => (
        <Tag color={getNoticeTypeColor(type)}>{getNoticeTypeLabel(type)}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge
          status={status === 'published' ? 'success' : status === 'draft' ? 'default' : status === 'withdrawn' ? 'warning' : 'default'}
          text={<Tag color={getNoticeStatusColor(status)}>{getNoticeStatusLabel(status)}</Tag>}
        />
      ),
    },
    {
      title: '发布人',
      dataIndex: ['publisher', 'real_name'],
      key: 'publisher',
      width: 120,
      render: (text: string, record: Notice) => (
        <span>{text || record.publisher?.username || '-'}</span>
      ),
    },
    {
      title: '发布时间',
      dataIndex: 'publish_time',
      key: 'publish_time',
      width: 180,
      render: (time: string) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '浏览次数',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 100,
      sorter: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record: Notice) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleView(record.id)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record.id)}
            />
          </Tooltip>
          <Tooltip title="统计">
            <Button
              type="text"
              icon={<BarChartOutlined />}
              onClick={() => handleStats(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="确定要删除这条公告吗？此操作不可恢复。"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="notice-list-page">
      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Search
              placeholder="搜索标题或内容"
              allowClear
              enterButton
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onSearch={() => actionRef.current?.reload()}
            />
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Select
              placeholder="公告类型"
              allowClear
              style={{ width: '100%' }}
              value={typeFilter}
              onChange={(value) => {
                setTypeFilter(value);
                actionRef.current?.reload();
              }}
            >
              {noticeTypeOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  <Tag color={opt.color}>{opt.label}</Tag>
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Select
              placeholder="公告状态"
              allowClear
              style={{ width: '100%' }}
              value={statusFilter}
              onChange={(value) => {
                setStatusFilter(value);
                actionRef.current?.reload();
              }}
            >
              {noticeStatusOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  <Tag color={opt.color}>{opt.label}</Tag>
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} style={{ textAlign: 'right' }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              发布公告
            </Button>
          </Col>
        </Row>

        <ProTable<Notice>
          actionRef={actionRef}
          columns={columns}
          request={fetchNotices}
          rowKey="id"
          pagination={{
            showQuickJumper: true,
            showSizeChanger: true,
            defaultPageSize: 10,
          }}
          search={false}
          options={{
            reload: true,
            density: true,
            fullScreen: true,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default NoticeList;
