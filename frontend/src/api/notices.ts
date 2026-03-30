import api from './api';

export interface Notice {
  id: number;
  title: string;
  content: string;
  summary?: string;
  type: 'normal' | 'important' | 'urgent';
  status: 'draft' | 'published' | 'withdrawn' | 'archived';
  publish_time?: string;
  expire_time?: string;
  is_top: boolean;
  top_expire_time?: string;
  attachment?: string;
  view_count: number;
  publisher_id: number;
  created_at: string;
  updated_at: string;
  publisher?: {
    id: number;
    real_name: string;
    username: string;
  };
  is_read?: boolean;
  read_time?: string;
}

export interface NoticeListParams {
  keyword?: string;
  type?: string;
  status?: string;
  is_top?: boolean;
  page?: number;
  page_size?: number;
}

export interface NoticeCreateParams {
  title: string;
  content: string;
  summary?: string;
  type?: string;
  status?: string;
  expire_time?: string;
  is_top?: boolean;
  top_expire_time?: string;
  attachment?: string;
}

export interface NoticeUpdateParams {
  title?: string;
  content?: string;
  summary?: string;
  type?: string;
  status?: string;
  expire_time?: string;
  is_top?: boolean;
  top_expire_time?: string;
  attachment?: string;
}

export interface NoticeReadStats {
  notice_id: number;
  title: string;
  total_users: number;
  read_count: number;
  unread_count: number;
  read_rate: number;
}

// 获取公告列表（管理后台）
export const getNoticeList = (params: NoticeListParams = {}) => {
  return api.get('/notices', { params });
};

// 获取已发布公告列表
export const getPublishedNotices = (params: { keyword?: string; type?: string; page?: number; page_size?: number } = {}) => {
  return api.get('/notices/published', { params });
};

// 获取我的公告列表
export const getMyNotices = (params: { is_read?: boolean; page?: number; page_size?: number } = {}) => {
  return api.get('/notices/my', { params });
};

// 获取未读公告数量
export const getUnreadCount = () => {
  return api.get('/notices/unread-count');
};

// 获取公告详情
export const getNoticeDetail = (id: number) => {
  return api.get(`/notices/${id}`);
};

// 创建公告
export const createNotice = (data: NoticeCreateParams) => {
  return api.post('/notices', data);
};

// 更新公告
export const updateNotice = (id: number, data: NoticeUpdateParams) => {
  return api.put(`/notices/${id}`, data);
};

// 删除公告
export const deleteNotice = (id: number) => {
  return api.delete(`/notices/${id}`);
};

// 标记公告为已读
export const markNoticeRead = (id: number) => {
  return api.post(`/notices/${id}/read`);
};

// 获取公告阅读统计
export const getNoticeReadStats = (id: number) => {
  return api.get(`/notices/${id}/read-stats`);
};

// 公告类型选项
export const noticeTypeOptions = [
  { label: '普通公告', value: 'normal', color: 'blue' },
  { label: '重要公告', value: 'important', color: 'orange' },
  { label: '紧急公告', value: 'urgent', color: 'red' },
];

// 公告状态选项
export const noticeStatusOptions = [
  { label: '草稿', value: 'draft', color: 'default' },
  { label: '已发布', value: 'published', color: 'success' },
  { label: '已撤回', value: 'withdrawn', color: 'warning' },
  { label: '已归档', value: 'archived', color: 'default' },
];

// 获取类型标签
export const getNoticeTypeLabel = (type: string) => {
  const option = noticeTypeOptions.find(opt => opt.value === type);
  return option?.label || type;
};

// 获取类型颜色
export const getNoticeTypeColor = (type: string) => {
  const option = noticeTypeOptions.find(opt => opt.value === type);
  return option?.color || 'blue';
};

// 获取状态标签
export const getNoticeStatusLabel = (status: string) => {
  const option = noticeStatusOptions.find(opt => opt.value === status);
  return option?.label || status;
};

// 获取状态颜色
export const getNoticeStatusColor = (status: string) => {
  const option = noticeStatusOptions.find(opt => opt.value === status);
  return option?.color || 'default';
};
