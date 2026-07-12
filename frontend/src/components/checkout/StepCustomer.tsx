import { useState } from 'react'
import type { CheckoutData } from '@/pages/Checkout'

interface Props {
  data: CheckoutData
  onNext: (data: CheckoutData) => void
}

export default function StepCustomer({ data, onNext }: Props) {
  const [form, setForm] = useState(data.customer)
  const [fulfillment, setFulfillment] = useState(data.fulfillmentType)
  const [address, setAddress] = useState(data.address || { cep: '', street: '', number: '', complement: '', neighborhood: '', city: 'São Paulo', state: 'SP' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.name.trim()) e.name = 'Nome obrigatório'
    if (!form.email.includes('@')) e.email = 'E-mail inválido'
    if (form.phone.replace(/\D/g, '').length < 10) e.phone = 'WhatsApp inválido'
    if (fulfillment === 'delivery' && !address.cep) e.cep = 'CEP obrigatório'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!validate()) return
    onNext({
      ...data,
      customer: form,
      fulfillmentType: fulfillment,
      address: fulfillment === 'delivery' ? address : null,
    })
  }

  return (
    <div className="space-y-4">
      <h2 className="font-display text-2xl font-bold text-chocolate-900 mb-4">Seus dados</h2>
      <input
        className="w-full p-3 border rounded-lg"
        placeholder="Nome completo"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
      />
      {errors.name && <p className="text-red-500 text-sm">{errors.name}</p>}

      <input
        className="w-full p-3 border rounded-lg"
        placeholder="E-mail"
        type="email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />
      {errors.email && <p className="text-red-500 text-sm">{errors.email}</p>}

      <input
        className="w-full p-3 border rounded-lg"
        placeholder="WhatsApp (11) 98765-4321"
        value={form.phone}
        onChange={(e) => setForm({ ...form, phone: e.target.value })}
      />
      {errors.phone && <p className="text-red-500 text-sm">{errors.phone}</p>}

      <input
        className="w-full p-3 border rounded-lg"
        placeholder="CPF (opcional)"
        value={form.cpf}
        onChange={(e) => setForm({ ...form, cpf: e.target.value })}
      />

      {/* Fulfillment type */}
      <div className="flex gap-4 pt-4">
        <button
          className={`flex-1 p-3 rounded-lg border-2 font-semibold ${fulfillment === 'pickup' ? 'border-rosa-500 bg-rosa-50 text-rosa-700' : 'border-gray-200'}`}
          onClick={() => setFulfillment('pickup')}
        >
          🏠 Retirada
        </button>
        <button
          className={`flex-1 p-3 rounded-lg border-2 font-semibold ${fulfillment === 'delivery' ? 'border-rosa-500 bg-rosa-50 text-rosa-700' : 'border-gray-200'}`}
          onClick={() => setFulfillment('delivery')}
        >
          🚗 Entrega
        </button>
      </div>

      {fulfillment === 'delivery' && (
        <div className="space-y-2 pt-2">
          <input className="w-full p-3 border rounded-lg" placeholder="CEP"
            value={address.cep} onChange={(e) => setAddress({ ...address, cep: e.target.value })} />
          {errors.cep && <p className="text-red-500 text-sm">{errors.cep}</p>}
          <input className="w-full p-3 border rounded-lg" placeholder="Rua"
            value={address.street} onChange={(e) => setAddress({ ...address, street: e.target.value })} />
          <div className="grid grid-cols-2 gap-2">
            <input className="p-3 border rounded-lg" placeholder="Nº"
              value={address.number} onChange={(e) => setAddress({ ...address, number: e.target.value })} />
            <input className="p-3 border rounded-lg" placeholder="Complemento"
              value={address.complement} onChange={(e) => setAddress({ ...address, complement: e.target.value })} />
          </div>
          <input className="w-full p-3 border rounded-lg" placeholder="Bairro"
            value={address.neighborhood} onChange={(e) => setAddress({ ...address, neighborhood: e.target.value })} />
        </div>
      )}

      {fulfillment === 'pickup' && (
        <div className="bg-creme-100 p-4 rounded-lg text-sm text-chocolate-700">
          📍 Retirada na Rua dos Doces, 123 — Vila Mariana, São Paulo/SP
        </div>
      )}

      <button
        onClick={handleSubmit}
        className="w-full py-3 bg-rosa-500 text-white font-semibold rounded-lg hover:bg-rosa-600"
      >
        Continuar para agendamento →
      </button>
    </div>
  )
}
