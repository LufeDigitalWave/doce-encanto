import { Link } from 'react-router-dom'
import { formatBRL, formatDate } from '@/lib/formatters'
import type { CheckoutData } from '@/pages/Checkout'

interface Props {
  data: CheckoutData
}

export default function StepConfirmation({ data }: Props) {
  return (
    <div className="text-center space-y-6">
      <div className="text-5xl mb-2">🎉</div>
      <h2 className="font-display text-2xl font-bold text-chocolate-900">
        Pedido confirmado!
      </h2>

      <div className="bg-white p-6 rounded-xl shadow-sm text-left space-y-3">
        <div className="flex justify-between">
          <span className="text-chocolate-600">Número:</span>
          <span className="font-bold text-rosa-600">{data.orderNumber}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-chocolate-600">Data agendada:</span>
          <span className="font-semibold">{formatDate(data.scheduledDate)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-chocolate-600">Tipo:</span>
          <span className="font-semibold">{data.fulfillmentType === 'pickup' ? 'Retirada' : 'Entrega'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-chocolate-600">Status:</span>
          <span className="font-semibold text-green-600">Pago ✅</span>
        </div>
      </div>

      <Link
        to={`/pedido/${data.publicToken}`}
        className="inline-block px-6 py-3 bg-rosa-500 text-white rounded-lg font-semibold hover:bg-rosa-600"
      >
        📦 Acompanhar pedido
      </Link>

      <Link to="/" className="block text-rosa-600 hover:underline text-sm">
        ← Voltar para a loja
      </Link>
    </div>
  )
}
