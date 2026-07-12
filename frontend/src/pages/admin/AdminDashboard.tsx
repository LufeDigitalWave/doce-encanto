import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatBRL } from '@/lib/formatters'

export default function AdminDashboard() {
  const { data } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => api.get('/admin/dashboard').then((r) => r.data),
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-chocolate-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <p className="text-chocolate-600 text-sm">Pedidos hoje</p>
          <p className="text-3xl font-bold text-rosa-600">{data?.orders_today || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <p className="text-chocolate-600 text-sm">Receita hoje</p>
          <p className="text-3xl font-bold text-green-600">{formatBRL(data?.revenue_today_cents || 0)}</p>
        </div>
      </div>
    </div>
  )
}
