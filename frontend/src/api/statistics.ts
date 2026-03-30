import api from './api';

// 经营概览
export const getBusinessOverview = (params?: { start_date?: string; end_date?: string }) => {
  return api.get('/statistics/business/overview', { params });
};

// 业务趋势
export const getBusinessTrend = (params?: { period?: string; months?: number }) => {
  return api.get('/statistics/business/trend', { params });
};

// 业务分布
export const getBusinessDistribution = (type: string) => {
  return api.get('/statistics/business/distribution', { params: { type } });
};

// Top客户
export const getTopCustomers = (limit: number = 10) => {
  return api.get('/statistics/business/top-customers', { params: { limit } });
};

// 财务概览
export const getFinanceOverview = (year?: number) => {
  return api.get('/statistics/finance/overview', { params: { year } });
};

// 月度财务
export const getFinanceMonthly = (year?: number) => {
  return api.get('/statistics/finance/monthly', { params: { year } });
};

// 系统使用情况
export const getSystemUsage = (days: number = 30) => {
  return api.get('/statistics/system/usage', { params: { days } });
};

// 登录日志
export const getLoginLogs = (params?: {
  page?: number;
  page_size?: number;
  username?: string;
  login_status?: string;
  start_time?: string;
  end_time?: string;
}) => {
  return api.get('/logs/login', { params });
};

// 图表颜色配置
export const chartColors = [
  '#1890ff', '#52c41a', '#faad14', '#f5222d', 
  '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
];
