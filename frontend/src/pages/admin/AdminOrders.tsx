import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatBRL, formatDate } from '@/lib/formatters'
import toast from 'react-hot-toast'

const STATUSES = ['pending_payment', 'paid', 'preparing', 'ready', 'delivered', 'canceled']

export default function AdminOrders() {
  const qc = useQueryClient()
  const { data: orders = [] } = useQuery({
    queryKey: ['admin-orders'],
    queryFn: () => api.get('/admin/orders').then((r) => r.data),
    refetchInterval: 5000,
  })

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.patch(`/admin/orders/${id}/status`, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-orders'] })
      toast.success('Status atualizado')
    },
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-chocolate-900 mb-6">Pedidos</h1>
      <div className="space-y-4">
        {orders.map((o: any) => (
          <div key={o.id} className="bg-white p-4 rounded-xl shadow-sm flex flex-col md:flex-row md:items-center gap-4">
            <div className="flex-1">
              <p className="font-bold text-rosa-600">{o.order_number}</p>
              <p className="text-sm text-chocolate-600">{o.customer_name} — {formatBRL(o.total_cents)}</p>
              <p className="text-sm text-chocolate-500">{formatDate(o.scheduled_date)} — {o.fulfillment_type}</p>
            </div>
            <select
              value={o.status}
              onChange={(e) => updateStatus.mutate({ id: o.id, status: e.target.value })}
              className="border rounded-lg p-2 text-sm"
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
        ))}
        {orders.length === 0 && <p className="text-chocolate-500">Nenhum pedido ainda.</p>}
      </div>
    </div>
  )
}
