import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatBRL } from '@/lib/formatters'

export default function AdminProducts() {
  const { data: products = [] } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => api.get('/admin/products').then((r) => r.data),
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-chocolate-900 mb-6">Produtos</h1>
      <div className="space-y-3">
        {products.map((p: any) => (
          <div key={p.id} className="bg-white p-4 rounded-lg shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 bg-rosa-100 rounded-lg flex items-center justify-center text-xl">🧁</div>
            <div className="flex-1">
              <p className="font-semibold text-chocolate-900">{p.name}</p>
              <p className="text-sm text-chocolate-600">{formatBRL(p.price_cents)}</p>
            </div>
            <span className={`text-xs font-semibold px-2 py-1 rounded ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {p.is_active ? 'Ativo' : 'Inativo'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
