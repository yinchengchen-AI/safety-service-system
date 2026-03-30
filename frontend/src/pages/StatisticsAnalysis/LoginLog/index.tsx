import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, DatePicker, Input, Select, Button, Space, message } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SearchOutlined,
  DesktopOutlined,
  MobileOutlined,
} from '@ant-design/icons';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns } from '@ant-design/pro-components';
import dayjs from 'dayjs';
import { getLoginLogs } from '@/api/statistics';
import './style.css';

const { RangePicker } = DatePicker;
const { Search } = Input;

interface LoginLog {
  id: number;
  username: string;
  real_name: string;
  login_type: string;
  login_status: 'success' | 'fail';
  ip_address: string;
  browser: string;
  os: string;
  device: string;
  fail_reason?: string;
  login_time: string;
}

const LoginLogPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<LoginLog[]>([]);
  const [total, setTotal] = useState(0);
  const [current, setCurrent] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [filters, setFilters] = useState({
    username: '',
    login_status: undefined as string | undefined,
    dateRange: null as [dayjs.Dayjs, dayjs.Dayjs] | null,
  });

  const fetchData = async (page = current, size = pageSize) => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: size,
      };

      if (filters.username) {
        params.username = filters.username;
      }
      if (filters.login_status) {
        params.login_status = filters.login_status;
      }
      if (filters.dateRange) {
        params.start_time = filters.dateRange[0].format('YYYY-MM-DD');
        params.end_time = filters.dateRange[1].format('YYYY-MM-DD');
      }

      const response = await getLoginLogs(params);
      setData(response.data.data.items || []);
      setTotal(response.data.data.total || 0);
    } catch (error) {
      message.error('获取登录日志失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleSearch = () => {
    setCurrent(1);
    fetchData(1);
  };

  const handleReset = () => {
    setFilters({
      username: '',
      login_status: undefined,
      dateRange: null,
    });
    setCurrent(1);
  };

  const columns: ProColumns<LoginLog>[] = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (text: string, record: LoginLog) => (
        <span>{record.real_name || text}</span>
      ),
    },
    {
      title: '登录状态',
      dataIndex: 'login_status',
      key: 'login_status',
      width: 100,
      render: (status: string) => (
        status === 'success' ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>成功</Tag>
        ) : (
          <Tag color="error" icon={<CloseCircleOutlined />}>失败</Tag>
        )
      ),
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
    },
    {
      title: '设备信息',
      key: 'device_info',
      width: 200,
      render: (_, record: LoginLog) => (
        <Space direction="vertical" size={0}>
          <span>{record.browser || '-'}</span>
          <span style={{ color: '#999', fontSize: 12 }}>{record.os || '-'}</span>
        </Space>
      ),
    },
    {
      title: '失败原因',
      dataIndex: 'fail_reason',
      key: 'fail_reason',
      width: 150,
      render: (text: string, record: LoginLog) => (
        record.login_status === 'fail' ? (
          <span style={{ color: '#f5222d' }}>{text || '未知错误'}</span>
        ) : (
          '-'
        )
      ),
    },
    {
      title: '登录时间',
      dataIndex: 'login_time',
      key: 'login_time',
      width: 180,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
  ];

  return (
    <div className="login-log-page">
      <Card>
        {/* 筛选栏 */}
        <Space className="filter-bar" wrap>
          <Search
            placeholder="搜索用户名"
            value={filters.username}
            onChange={(e) => setFilters({ ...filters, username: e.target.value })}
            onSearch={handleSearch}
            style={{ width: 200 }}
            allowClear
          />
          <Select
            placeholder="登录状态"
            value={filters.login_status}
            onChange={(value) => setFilters({ ...filters, login_status: value })}
            style={{ width: 120 }}
            allowClear
          >
            <Select.Option value="success">成功</Select.Option>
            <Select.Option value="fail">失败</Select.Option>
          </Select>
          <RangePicker
            value={filters.dateRange}
            onChange={(dates) => setFilters({ ...filters, dateRange: dates as [dayjs.Dayjs, dayjs.Dayjs] })}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            查询
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>

        {/* 表格 */}
        <ProTable<LoginLog>
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          search={false}
          options={false}
          pagination={{
            current,
            pageSize,
            total,
            showQuickJumper: true,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, size) => {
              setCurrent(page);
              setPageSize(size || 20);
              fetchData(page, size);
            },
          }}
          scroll={{ x: 800 }}
        />
      </Card>
    </div>
  );
};

export default LoginLogPage;
