import api from './api'
import { ApiResponse, PaginatedData } from '@/types'

export interface Invoice {
  id: number
  invoice_no: string
  invoice_code: string | null
  type: 'special' | 'normal' | 'electronic'
  amount: number
  paid_amount: number
  tax_amount: number | null
  status: string
  issue_date: string
  buyer_name: string
  buyer_tax_no: string | null
  contract: {
    id: number
    name: string
    code: string
  } | null
  issuer: {
    id: number
    real_name: string
  } | null
  created_at: string
}

export interface Payment {
  id: number
  code: string
  amount: number
  payment_date: string
  method: string
  payer_name: string | null
  payer_account: string | null
  voucher_no: string | null
  remark: string | null
  contract: {
    id: number
    name: string
    code: string
  } | null
  invoice: {
    id: number
    invoice_no: string
    amount: number
  } | null
  recorder: {
    id: number
    real_name: string
  } | null
  created_at: string
}

export interface FinanceSummary {
  contract_id: number
  contract_name: string
  contract_amount: number
  invoiced_amount: number
  paid_amount: number
  uninvoiced_amount: number
  unpaid_amount: number
  invoices: Array<{
    id: number
    invoice_no: string
    amount: number
    paid_amount: number
    status: string
  }>
  payments: Array<{
    id: number
    code: string
    amount: number
    payment_date: string
  }>
}

export const financeApi = {
  // 开票管理
  getInvoices: (params: {
    contract_id?: number
    status?: string
    page?: number
    page_size?: number
  }): Promise<ApiResponse<PaginatedData<Invoice>>> => {
    return api.get('/finance/invoices', { params })
  },

  createInvoice: (data: {
    contract_id: number
    invoice_no: string
    invoice_code?: string
    type: 'special' | 'normal' | 'electronic'
    amount: number
    tax_amount?: number
    issue_date: string
    buyer_name?: string
    buyer_tax_no?: string
    seller_name?: string
    seller_tax_no?: string
    remark?: string
  }): Promise<ApiResponse<Invoice>> => {
    return api.post('/finance/invoices', data)
  },

  deleteInvoice: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/finance/invoices/${id}`)
  },

  // 收款管理
  getPayments: (params: {
    contract_id?: number
    invoice_id?: number
    page?: number
    page_size?: number
  }): Promise<ApiResponse<PaginatedData<Payment>>> => {
    return api.get('/finance/payments', { params })
  },

  createPayment: (data: {
    contract_id: number
    invoice_id?: number
    amount: number
    payment_date: string
    method?: string
    payer_name?: string
    payer_account?: string
    payer_bank?: string
    receiver_account?: string
    receiver_bank?: string
    voucher_no?: string
    remark?: string
  }): Promise<ApiResponse<Payment>> => {
    return api.post('/finance/payments', data)
  },

  deletePayment: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/finance/payments/${id}`)
  },

  // 财务统计
  getContractFinanceSummary: (contractId: number): Promise<ApiResponse<FinanceSummary>> => {
    return api.get(`/finance/contracts/${contractId}/finance-summary`)
  },
}
