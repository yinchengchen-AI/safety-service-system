import { useQuery } from '@tanstack/react-query'
import { Row, Col, Card, Statistic, Badge, List, Tag, Skeleton } from 'antd'
import {
  TeamOutlined,
  FileTextOutlined,
  DollarOutlined,
  SafetyCertificateOutlined,
  BellOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { dashboardApi } from '@/api'
import './style.css'

const Dashboard = () => {
  // 获取统计数据
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => dashboardApi.getStats(),
  })

  // 获取待办事项
  const { data: todosData, isLoading: todosLoading } = useQuery({
    queryKey: ['dashboard', 'todos'],
    queryFn: () => dashboardApi.getTodos(),
  })

  // 获取最近动态
  const { data: activitiesData, isLoading: activitiesLoading } = useQuery({
    queryKey: ['dashboard', 'activities'],
    queryFn: () => dashboardApi.getActivities(),
  })

  const stats = statsData?.data
  const todos = todosData?.data || []
  const activities = activitiesData?.data || []

  const statistics = [
    {
      title: '本月合同金额',
      value: stats?.total_contract_amount || 0,
      prefix: '¥',
      precision: 2,
      change: 12.5,
      changeType: 'up',
      icon: <FileTextOutlined />,
      color: '#1890ff',
      loading: statsLoading,
    },
    {
      title: '本月收款金额',
      value: stats?.total_payment_amount || 0,
      prefix: '¥',
      precision: 2,
      change: 8.2,
      changeType: 'up',
      icon: <DollarOutlined />,
      color: '#52c41a',
      loading: statsLoading,
    },
    {
      title: '进行中服务',
      value: stats?.active_services || 0,
      change: -2,
      changeType: 'down',
      icon: <SafetyCertificateOutlined />,
      color: '#faad14',
      loading: statsLoading,
    },
    {
      title: '客户总数',
      value: stats?.total_customers || 0,
      change: 5,
      changeType: 'up',
      icon: <TeamOutlined />,
      color: '#722ed1',
      loading: statsLoading,
    },
  ]

  const quickItems = [
    { icon: <FileTextOutlined />, title: '新建合同', color: '#1890ff', path: '/contracts' },
    { icon: <TeamOutlined />, title: '新增客户', color: '#52c41a', path: '/companies' },
    { icon: <DollarOutlined />, title: '开票申请', color: '#faad14', path: '/invoices' },
    { icon: <SafetyCertificateOutlined />, title: '服务登记', color: '#722ed1', path: '/services' },
  ]

  return (
    <div className="dashboard">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} className="stat-row">
        {statistics.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card className="stat-card" bordered={false}>
              <div className="stat-icon" style={{ background: `${stat.color}15`, color: stat.color }}>
                {stat.icon}
              </div>
              {stat.loading ? (
                <Skeleton active paragraph={false} />
              ) : (
                <>
                  <Statistic
                    title={stat.title}
                    value={stat.value}
                    prefix={stat.prefix}
                    precision={stat.precision}
                    valueStyle={{ color: '#262626', fontSize: 28, fontWeight: 600 }}
                  />
                  <div className="stat-change">
                    {stat.changeType === 'up' ? (
                      <span className="change-up">
                        <ArrowUpOutlined /> {stat.change}%
                      </span>
                    ) : (
                      <span className="change-down">
                        <ArrowDownOutlined /> {Math.abs(stat.change)}%
                      </span>
                    )}
                    <span className="change-text">较上月</span>
                  </div>
                </>
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* 快捷操作和待办 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="快捷入口" bordered={false} className="quick-card">
            <Row gutter={[16, 16]}>
              {quickItems.map((item, index) => (
                <Col span={6} key={index}>
                  <div 
                    className="quick-item" 
                    style={{ '--item-color': item.color } as React.CSSProperties}
                    onClick={() => window.location.href = item.path}
                  >
                    <div className="quick-icon">{item.icon}</div>
                    <div className="quick-title">{item.title}</div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card
            title={
              <span>
                <BellOutlined style={{ marginRight: 8 }} />
                待办事项
              </span>
            }
            bordered={false}
            extra={<a href="#">查看全部</a>}
            className="todo-card"
          >
            {todosLoading ? (
              <Skeleton active />
            ) : (
              <List
                dataSource={todos}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <div className="todo-title">
                          <Badge status={item.type as any} />
                          <span>{item.title}</span>
                        </div>
                      }
                      description={
                        <div className="todo-desc">
                          <span>{item.description}</span>
                          <Tag>{item.date}</Tag>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 最近动态 */}
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="最近动态" bordered={false} extra={<a href="#">查看更多</a>}>
            {activitiesLoading ? (
              <Skeleton active />
            ) : (
              <List
                dataSource={activities}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<div className="activity-avatar">{item.user[0]}</div>}
                      title={
                        <span>
                          <strong>{item.user}</strong>
                          <span className="activity-action"> {item.action} </span>
                          <a>{item.target}</a>
                        </span>
                      }
                      description={
                        <span className="activity-time">
                          <ClockCircleOutlined /> {item.time}
                        </span>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
