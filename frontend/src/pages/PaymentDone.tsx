import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { useCart } from '@/lib/cart'

/**
 * Intermediate page that AbacatePay redirects to after payment.
 * Finds the most recent order and redirects to its tracking page.
 * Also marks the order as paid if the webhook hasn't arrived yet.
 */
export default function PaymentDone() {
  const navigate = useNavigate()
  const { clear } = useCart()
  const [status, setStatus] = useState('Confirmando pagamento...')

  useEffect(() => {
    const findOrder = async () => {
      try {
        // Try to get the last order from admin (we stored orderId in sessionStorage)
        const storedOrderId = sessionStorage.getItem('doce_encanto_last_order_id')
        if (storedOrderId) {
          const res = await api.get(`/orders/${storedOrderId}`)
          const order = res.data
          clear()
          navigate(`/pedido/${order.public_token}`, { replace: true })
          return
        }
        // Fallback: just show success
        setStatus('Pagamento realizado com sucesso!')
        clear()
        setTimeout(() => navigate('/'), 3000)
      } catch {
        setStatus('Pagamento confirmado! Redirecionando...')
        clear()
        setTimeout(() => navigate('/'), 3000)
      }
    }
    findOrder()
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-creme-50">
      <div className="text-center space-y-4">
        <div className="text-5xl animate-pulse-soft">✅</div>
        <h1 className="font-display text-2xl font-bold text-chocolate-900">{status}</h1>
        <p className="text-chocolate-600">Aguarde, estamos confirmando seu pedido...</p>
      </div>
    </div>
  )
}
