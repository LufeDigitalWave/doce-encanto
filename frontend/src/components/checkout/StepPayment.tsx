import { useState, useEffect, useRef } from 'react'
import { useCart } from '@/lib/cart'
import { formatBRL } from '@/lib/formatters'
import api from '@/lib/api'
import type { CheckoutData } from '@/pages/Checkout'
import toast from 'react-hot-toast'

interface Props {
  data: CheckoutData
  onNext: (data: CheckoutData) => void
  onBack: () => void
}

export default function StepPayment({ data, onNext, onBack }: Props) {
  const { items, total, clear } = useCart()
  const [loading, setLoading] = useState(false)
  const [orderId, setOrderId] = useState<number | null>(data.orderId)
  const [qrCode, setQrCode] = useState('')
  const [copyPaste, setCopyPaste] = useState('')
  const [checkoutUrl, setCheckoutUrl] = useState('')
  const [demoMode, setDemoMode] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState<string>('pending')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // 1. Create order
  const createOrder = async () => {
    setLoading(true)
    try {
      const res = await api.post('/orders', {
        items: items.map((i) => ({ product_id: i.productId, quantity: i.quantity })),
        customer: data.customer,
        fulfillment_type: data.fulfillmentType,
        address: data.address,
        scheduled_date: data.scheduledDate,
        slot_id: data.slotId,
        payment_method: 'pix',
      })
      const order = res.data
      setOrderId(order.id)
      return order
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Erro ao criar pedido')
      return null
    } finally {
      setLoading(false)
    }
  }

  // 2. Create PIX charge
  const createCharge = async (oid: number) => {
    const res = await api.post(`/orders/${oid}/pay`)
    const charge = res.data
    setQrCode(charge.qr_code_base64)
    setCopyPaste(charge.copy_paste_code)
    setCheckoutUrl(charge.checkout_url || '')
    setDemoMode(charge.demo_mode)

    // If real mode with hosted checkout, save order ID and redirect
    if (charge.checkout_url) {
      sessionStorage.setItem('doce_encanto_last_order_id', String(oid))
      window.location.href = charge.checkout_url
    }
  }

  // 3. Poll payment status
  const startPolling = (oid: number) => {
    pollRef.current = setInterval(async () => {
      const res = await api.get(`/orders/${oid}/payment-status`)
      if (res.data.status === 'paid') {
        setPaymentStatus('paid')
        if (pollRef.current) clearInterval(pollRef.current)
      }
    }, 3000)
  }

  // Kick off: create order then charge
  useEffect(() => {
    if (orderId) return
    ;(async () => {
      const order = await createOrder()
      if (order) {
        await createCharge(order.id)
        startPolling(order.id)
      }
    })()
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  // When paid, proceed
  useEffect(() => {
    if (paymentStatus === 'paid' && orderId) {
      // Fetch final order data
      api.get(`/orders/${orderId}`).then((res) => {
        clear()
        onNext({
          ...data,
          orderId: res.data.id,
          orderNumber: res.data.order_number,
          publicToken: res.data.public_token,
        })
      })
    }
  }, [paymentStatus])

  // Simulate payment (demo only)
  const handleSimulate = async () => {
    if (!orderId) return
    await api.post(`/orders/${orderId}/simulate-payment`)
    setPaymentStatus('paid')
  }

  return (
    <div className="space-y-6">
      <h2 className="font-display text-2xl font-bold text-chocolate-900">Pagamento via Pix</h2>

      <div className="bg-white p-6 rounded-xl shadow-sm text-center">
        <p className="text-lg font-bold text-chocolate-900 mb-4">
          Total: {formatBRL(total())}
        </p>

        {loading && <p className="text-chocolate-600">Gerando QR Code...</p>}

        {qrCode && paymentStatus === 'pending' && (
          <>
            <img
              src={qrCode}
              alt="QR Code Pix"
              className="mx-auto w-56 h-56 mb-4 rounded-lg"
            />
            <div className="bg-creme-100 p-3 rounded-lg mb-4">
              <p className="text-sm text-chocolate-600 mb-1">Copia e Cola:</p>
              <p className="text-xs font-mono break-all">{copyPaste}</p>
              <button
                className="mt-2 text-rosa-600 text-sm font-semibold"
                onClick={() => { navigator.clipboard.writeText(copyPaste); toast.success('Copiado!') }}
              >
                📋 Copiar código
              </button>
            </div>

            <p className="text-sm text-chocolate-500 animate-pulse">
              ⏳ Aguardando pagamento...
            </p>

            {demoMode && (
              <div className="mt-4 p-4 border-2 border-dashed border-rosa-300 rounded-lg">
                <p className="text-sm text-rosa-600 font-semibold mb-2">
                  🎭 Modo demonstração
                </p>
                <button
                  onClick={handleSimulate}
                  className="px-6 py-2 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600"
                >
                  ✅ Simular pagamento aprovado
                </button>
              </div>
            )}
          </>
        )}

        {paymentStatus === 'paid' && (
          <div className="text-center py-8">
            <div className="text-5xl mb-4">✅</div>
            <p className="text-xl font-bold text-green-700">Pagamento confirmado!</p>
          </div>
        )}
      </div>

      {paymentStatus === 'pending' && (
        <button onClick={onBack} className="w-full py-3 border rounded-lg text-chocolate-700">
          ← Voltar
        </button>
      )}
    </div>
  )
}
