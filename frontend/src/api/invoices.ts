import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

export interface Invoice {
  id: number
  invoice_no: string
  invoice_code: string | null
  type: 'special' | 'normal' | 'electronic'
  amount: number
  tax_amount: number | null
  issue_date: string
  buyer_name: string
  buyer_tax_no: string | null
  seller_name: string
  seller_tax_no: string | null
  status: 'pending' | 'issued' | 'sent' | 'received' | 'cancelled' | 'red_flushed'
  contract_id: number | null
  contract?: {
    id: number
    name: string
  }
  created_at: string
  updated_at: string
}

export interface InvoiceQuery {
  keyword?: string
  status?: string
  page?: number
  page_size?: number
}

export const invoiceApi = {
  // 获取发票列表
  getInvoices: (params: InvoiceQuery): Promise<ApiResponse<PaginatedData<Invoice>>> => {
    return api.get('/invoices', { params })
  },

  // 获取发票详情
  getInvoice: (id: number): Promise<ApiResponse<Invoice>> => {
    return api.get(`/invoices/${id}`)
  },

  // 创建发票申请
  createInvoice: (data: Partial<Invoice>): Promise<ApiResponse<Invoice>> => {
    return api.post('/invoices', data)
  },

  // 更新发票
  updateInvoice: (id: number, data: Partial<Invoice>): Promise<ApiResponse<Invoice>> => {
    return api.put(`/invoices/${id}`, data)
  },

  // 删除发票
  deleteInvoice: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/invoices/${id}`)
  },
}
