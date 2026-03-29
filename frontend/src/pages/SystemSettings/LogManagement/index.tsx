import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  message,
  Modal,
  DatePicker,
  Select,
  Drawer,
  Descriptions,
} from 'antd'
import {
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import { logsApi, OperationLog, OperationLogDetail } from '@/api/logs'
import { useAuthStore } from '@/stores'
import './style.css'

const { RangePicker } = DatePicker
const { Option } = Select

const LogManagement = () => {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  const [query, setQuery] = useState({
    page: 1,
    page_size: 20,
    username: '',
    module: undefined as string | undefined,
    log_type: undefined as string | undefined,
    status: undefined as string | undefined,
    start_time: '',
    end_time: '',
  })
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const [detailVisible, setDetailVisible] = useState(false)
  const [currentLog, setCurrentLog] = useState<OperationLogDetail | null>(null)

  const isAdmin = user?.is_superuser

  // 获取日志列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['operationLogs', query],
    queryFn: () => logsApi.getOperationLogs({
      page: query.page,
      page_size: query.page_size,
      username: query.username || undefined,
      module: query.module,
      log_type: query.log_type,
      status: query.status,
      start_time: query.start_time,
      end_time: query.end_time,
    }),
  })

  // 获取模块列表
  const { data: modulesData } = useQuery({
    queryKey: ['logModules'],
    queryFn: () => logsApi.getLogModules(),
  })

  // 获取日志详情
  const fetchLogDetail = async (id: number) => {
    try {
      const res = await logsApi.getOperationLogDetail(id)
      if (res.code === 200) {
        setCurrentLog(res.data)
        setDetailVisible(true)
      }
    } catch {
      message.error('获取日志详情失败')
    }
  }

  // 删除 mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => logsApi.deleteOperationLog(id),
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['operationLogs'] })
    },
    onError: () => {
      message.error('删除失败')
    },
  })

  // 批量删除 mutation
  const batchDeleteMutation = useMutation({
    mutationFn: (ids: number[]) => logsApi.batchDeleteOperationLogs(ids),
    onSuccess: () => {
      message.success('批量删除成功')
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['operationLogs'] })
    },
    onError: () => {
      message.error('批量删除失败')
    },
  })

  const logs = data?.data?.items || []
  const total = data?.data?.total || 0
  const modules = modulesData?.data || []

  // 获取操作类型标签
  const getLogTypeTag = (type: string) => {
    const typeMap: Record<string, { color: string; text: string }> = {
      create: { color: 'green', text: '创建' },
      update: { color: 'blue', text: '更新' },
      delete: { color: 'red', text: '删除' },
      query: { color: 'cyan', text: '查询' },
      export: { color: 'purple', text: '导出' },
      import: { color: 'orange', text: '导入' },
      login: { color: 'success', text: '登录' },
      logout: { color: 'default', text: '登出' },
      other: { color: 'default', text: '其他' },
    }
    const config = typeMap[type] || { color: 'default', text: type }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 获取状态标签
  const getStatusTag = (status: string) => {
    return status === 'success' 
      ? <Tag color="success">成功</Tag>
      : <Tag color="error">失败</Tag>
  }

  // 获取请求方法标签
  const getMethodTag = (method: string | null) => {
    if (!method) return '-'
    const colorMap: Record<string, string> = {
      GET: 'blue',
      POST: 'green',
      PUT: 'orange',
      PATCH: 'gold',
      DELETE: 'red',
    }
    return <Tag color={colorMap[method] || 'default'}>{method}</Tag>
  }

  // 表格列定义
  const columns = [
    {
      title: '操作人',
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (text: string, record: OperationLog) => (
        <span>{record.real_name || text || '-'}</span>
      ),
    },
    {
      title: '操作类型',
      dataIndex: 'log_type',
      key: 'log_type',
      width: 100,
      render: (type: string) => getLogTypeTag(type),
    },
    {
      title: '操作模块',
      dataIndex: 'module',
      key: 'module',
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: '请求方法',
      dataIndex: 'request_method',
      key: 'request_method',
      width: 100,
      render: (method: string) => getMethodTag(method),
    },
    {
      title: '操作描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '执行时间',
      dataIndex: 'execution_time',
      key: 'execution_time',
      width: 100,
      render: (time: number) => time ? `${time}ms` : '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '操作时间',
      dataIndex: 'operation_time',
      key: 'operation_time',
      width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: OperationLog) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => fetchLogDetail(record.id)}
          >
            查看
          </Button>
          {isAdmin && (
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '确认删除',
                  content: '确定要删除这条日志吗？',
                  onOk: () => deleteMutation.mutate(record.id),
                })
              }}
            >
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ]

  // 处理日期范围变化
  const handleDateRangeChange = (dates: any) => {
    if (dates) {
      setQuery({
        ...query,
        start_time: dates[0]?.format('YYYY-MM-DD'),
        end_time: dates[1]?.format('YYYY-MM-DD'),
        page: 1,
      })
    } else {
      setQuery({
        ...query,
        start_time: '',
        end_time: '',
        page: 1,
      })
    }
  }

  return (
    <div className="log-management-page">
      <Card
        title="操作日志"
        extra={
          <Space>
            {isAdmin && selectedRowKeys.length > 0 && (
              <Button
                danger
                onClick={() => {
                  Modal.confirm({
                    title: '确认批量删除',
                    content: `确定要删除选中的 ${selectedRowKeys.length} 条日志吗？`,
                    onOk: () => batchDeleteMutation.mutate(selectedRowKeys),
                  })
                }}
              >
                批量删除
              </Button>
            )}
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
          </Space>
        }
      >
        {/* 搜索栏 */}
        <div className="search-bar">
          <Space wrap>
            <Input
              placeholder="操作人用户名"
              value={query.username}
              onChange={(e) => setQuery({ ...query, username: e.target.value, page: 1 })}
              style={{ width: 150 }}
              prefix={<SearchOutlined />}
              allowClear
            />
            <Select
              placeholder="操作模块"
              allowClear
              style={{ width: 150 }}
              value={query.module}
              onChange={(value) => setQuery({ ...query, module: value, page: 1 })}
            >
              {modules.map((module) => (
                <Option key={module} value={module}>{module}</Option>
              ))}
            </Select>
            <Select
              placeholder="操作类型"
              allowClear
              style={{ width: 120 }}
              value={query.log_type}
              onChange={(value) => setQuery({ ...query, log_type: value, page: 1 })}
            >
              <Option value="create">创建</Option>
              <Option value="update">更新</Option>
              <Option value="delete">删除</Option>
              <Option value="query">查询</Option>
              <Option value="export">导出</Option>
              <Option value="import">导入</Option>
              <Option value="other">其他</Option>
            </Select>
            <Select
              placeholder="操作状态"
              allowClear
              style={{ width: 120 }}
              value={query.status}
              onChange={(value) => setQuery({ ...query, status: value, page: 1 })}
            >
              <Option value="success">成功</Option>
              <Option value="fail">失败</Option>
            </Select>
            <RangePicker
              placeholder={['开始日期', '结束日期']}
              onChange={handleDateRangeChange}
            />
          </Space>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          rowSelection={isAdmin ? {
            selectedRowKeys,
            onChange: (keys) => setSelectedRowKeys(keys as number[]),
          } : undefined}
          pagination={{
            current: query.page,
            pageSize: query.page_size,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setQuery({ ...query, page, page_size: pageSize || 20 })
            },
          }}
        />
      </Card>

      {/* 详情抽屉 */}
      <Drawer
        title="日志详情"
        width={600}
        open={detailVisible}
        onClose={() => {
          setDetailVisible(false)
          setCurrentLog(null)
        }}
      >
        {currentLog && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="ID">{currentLog.id}</Descriptions.Item>
            <Descriptions.Item label="操作人">
              {currentLog.real_name || currentLog.username || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="用户ID">{currentLog.user_id || '-'}</Descriptions.Item>
            <Descriptions.Item label="操作类型">
              {getLogTypeTag(currentLog.log_type)}
            </Descriptions.Item>
            <Descriptions.Item label="操作模块">{currentLog.module}</Descriptions.Item>
            <Descriptions.Item label="操作动作">{currentLog.action}</Descriptions.Item>
            <Descriptions.Item label="操作描述">{currentLog.description || '-'}</Descriptions.Item>
            <Descriptions.Item label="请求方法">
              {getMethodTag(currentLog.request_method)}
            </Descriptions.Item>
            <Descriptions.Item label="请求URL">{currentLog.request_url || '-'}</Descriptions.Item>
            <Descriptions.Item label="请求参数" className="pre-wrap">
              {currentLog.request_params || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="响应数据" className="pre-wrap">
              {currentLog.response_data || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="IP地址">{currentLog.ip_address || '-'}</Descriptions.Item>
            <Descriptions.Item label="User-Agent">{currentLog.user_agent || '-'}</Descriptions.Item>
            <Descriptions.Item label="执行时间">{currentLog.execution_time}ms</Descriptions.Item>
            <Descriptions.Item label="状态">
              {getStatusTag(currentLog.status)}
            </Descriptions.Item>
            <Descriptions.Item label="错误信息" className="pre-wrap error-text">
              {currentLog.error_msg || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="操作时间">
              {currentLog.operation_time ? new Date(currentLog.operation_time).toLocaleString() : '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  )
}

export default LogManagement
