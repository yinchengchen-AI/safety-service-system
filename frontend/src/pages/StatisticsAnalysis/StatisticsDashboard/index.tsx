import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Spin, message } from 'antd';
import {
  UserOutlined,
  FileTextOutlined,
  DollarOutlined,
  SafetyCertificateOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons';
import { Line, Pie, Column } from '@ant-design/charts';
import dayjs from 'dayjs';
import {
  getBusinessOverview,
  getBusinessTrend,
  getBusinessDistribution,
  getSystemUsage,
} from '@/api/statistics';
import './style.css';

const { RangePicker } = DatePicker;

const StatisticsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [overviewData, setOverviewData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [distributionData, setDistributionData] = useState<any[]>([]);
  const [systemUsage, setSystemUsage] = useState<any>(null);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(1, 'year'),
    dayjs(),
  ]);

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [overviewRes, trendRes, distributionRes, systemRes] = await Promise.all([
        getBusinessOverview({
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        }),
        getBusinessTrend({ months: 12 }),
        getBusinessDistribution('contract_status'),
        getSystemUsage(30),
      ]);

      setOverviewData(overviewRes.data.data);
      setTrendData(trendRes.data.data);
      setDistributionData(distributionRes.data.data);
      setSystemUsage(systemRes.data.data);
    } catch (error) {
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 趋势图配置
  const trendConfig = {
    data: trendData?.contract_trend?.map((item: any) => ({
      ...item,
      type: '合同金额',
    })) || [],
    xField: 'period',
    yField: 'amount',
    seriesField: 'type',
    smooth: true,
    point: {
      size: 4,
      shape: 'circle',
    },
    label: {
      style: {
        fill: '#aaa',
      },
    },
  };

  // 分布图配置
  const pieConfig = {
    data: distributionData,
    angleField: 'value',
    colorField: 'name',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    legend: {
      position: 'bottom',
    },
  };

  return (
    <div className="statistics-dashboard">
      <Spin spinning={loading}>
        {/* 日期筛选 */}
        <Card className="filter-card">
          <RangePicker
            value={dateRange}
            onChange={(dates) => dates && setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
            style={{ width: 300 }}
          />
        </Card>

        {/* 概览统计 */}
        <Row gutter={[16, 16]} className="overview-row">
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="客户总数"
                value={overviewData?.companies?.total || 0}
                prefix={<UserOutlined />}
                suffix={
                  overviewData?.companies?.growth_rate > 0 ? (
                    <RiseOutlined style={{ color: '#52c41a' }} />
                  ) : (
                    <FallOutlined style={{ color: '#f5222d' }} />
                  )
                }
              />
              <div className="stat-footer">
                新增: {overviewData?.companies?.new_this_period || 0} 
                ({overviewData?.companies?.growth_rate || 0}%)
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="合同总数"
                value={overviewData?.contracts?.total || 0}
                prefix={<FileTextOutlined />}
              />
              <div className="stat-footer">
                金额: ¥{(overviewData?.contracts?.total_amount || 0).toLocaleString()}
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="收款总额"
                value={overviewData?.payments?.total || 0}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => `¥${Number(value).toLocaleString()}`}
              />
              <div className="stat-footer">
                回款率: {overviewData?.payments?.collection_rate || 0}%
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="服务完成"
                value={overviewData?.services?.completed || 0}
                prefix={<SafetyCertificateOutlined />}
                suffix={`/ ${overviewData?.services?.total || 0}`}
              />
              <div className="stat-footer">
                完成率: {overviewData?.services?.completion_rate || 0}%
              </div>
            </Card>
          </Col>
        </Row>

        {/* 图表区域 */}
        <Row gutter={[16, 16]} className="charts-row">
          <Col xs={24} lg={16}>
            <Card title="业务趋势（合同金额）">
              <Line {...trendConfig} height={300} />
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="合同状态分布">
              <Pie {...pieConfig} height={300} />
            </Card>
          </Col>
        </Row>

        {/* 系统使用情况 */}
        <Row gutter={[16, 16]} className="system-row">
          <Col xs={24} md={8}>
            <Card title="系统登录">
              <Statistic
                title="登录次数"
                value={systemUsage?.login?.total || 0}
                suffix={`(成功: ${systemUsage?.login?.success || 0})`}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card title="操作统计">
              <Statistic
                title="操作次数"
                value={systemUsage?.operation?.total || 0}
                suffix={`(成功: ${systemUsage?.operation?.success || 0})`}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card title="活跃用户">
              <Statistic
                title="活跃用户数"
                value={systemUsage?.active_users || 0}
                suffix={`(${systemUsage?.period?.days || 30}天)`}
              />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default StatisticsDashboard;
