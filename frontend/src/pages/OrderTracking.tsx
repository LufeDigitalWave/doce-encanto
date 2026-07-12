import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatBRL, formatDate } from '@/lib/formatters'
import Header from '@/components/Header'
import { useCart } from '@/lib/cart'

const STATUS_LABELS: Record<string, string> = {
  pending_payment: '⏳ Aguardando pagamento',
  paid: '✅ Pago',
  preparing: '👨‍🍳 Em preparo',
  ready: '📦 Pronto',
  delivered: '🎉 Entregue',
  canceled: '❌ Cancelado',
}

const STATUS_ORDER = ['pending_payment', 'paid', 'preparing', 'ready', 'delivered']

export default function OrderTracking() {
  const { token } = useParams()
  const { count } = useCart()
  const { data: order, isLoading } = useQuery({
    queryKey: ['tracking', token],
    queryFn: () => api.get(`/tracking/${token}`).then((r) => r.data),
    refetchInterval: 5000,
  })

  return (
    <div className="min-h-screen bg-creme-50">
      <Header cartCount={count()} onCartClick={() => {}} />
      <div className="max-w-xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-chocolate-900 mb-6">
          📦 Rastreamento do Pedido
        </h1>

        {isLoading && <p>Carregando...</p>}

        {order && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex justify-between mb-2">
                <span className="text-chocolate-600">Pedido:</span>
                <span className="font-bold text-rosa-600">{order.order_number}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-chocolate-600">Total:</span>
                <span className="font-bold">{formatBRL(order.total_cents)}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-chocolate-600">Agendamento:</span>
                <span className="font-semibold">{formatDate(order.scheduled_date)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-chocolate-600">Tipo:</span>
                <span>{order.fulfillment_type === 'pickup' ? 'Retirada' : 'Entrega'}</span>
              </div>
            </div>

            {/* Status timeline */}
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <h3 className="font-semibold text-chocolate-900 mb-4">Status</h3>
              <div className="space-y-3">
                {STATUS_ORDER.map((s) => {
                  const idx = STATUS_ORDER.indexOf(order.status)
                  const thisIdx = STATUS_ORDER.indexOf(s)
                  const passed = thisIdx <= idx
                  return (
                    <div key={s} className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full ${passed ? 'bg-green-500' : 'bg-gray-200'}`} />
                      <span className={passed ? 'font-semibold text-chocolate-900' : 'text-chocolate-400'}>
                        {STATUS_LABELS[s]}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Items */}
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <h3 className="font-semibold text-chocolate-900 mb-3">Itens</h3>
              {order.items.map((it: any) => (
                <div key={it.id} className="flex justify-between text-sm py-1">
                  <span>{it.quantity}x {it.product_name_snapshot}</span>
                  <span>{formatBRL(it.unit_price_cents * it.quantity)}</span>
                </div>
              ))}
            </div>

            <a
              href="https://wa.me/5511987654321"
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center py-3 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600"
            >
              💬 Falar com a doceria
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
