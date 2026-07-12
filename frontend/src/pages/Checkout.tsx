import { useState } from 'react'
import { useCart } from '@/lib/cart'
import { formatBRL } from '@/lib/formatters'
import StepCustomer from '@/components/checkout/StepCustomer'
import StepScheduling from '@/components/checkout/StepScheduling'
import StepPayment from '@/components/checkout/StepPayment'
import StepConfirmation from '@/components/checkout/StepConfirmation'
import Header from '@/components/Header'

const STEPS = ['Dados', 'Agendamento', 'Pagamento', 'Confirmação']

export interface CheckoutData {
  customer: { name: string; email: string; phone: string; cpf: string }
  fulfillmentType: 'pickup' | 'delivery'
  address: {
    cep: string; street: string; number: string; complement: string; neighborhood: string; city: string; state: string
  } | null
  scheduledDate: string
  slotId: number | null
  orderId: number | null
  orderNumber: string
  publicToken: string
}

const initial: CheckoutData = {
  customer: { name: '', email: '', phone: '', cpf: '' },
  fulfillmentType: 'pickup',
  address: null,
  scheduledDate: '',
  slotId: null,
  orderId: null,
  orderNumber: '',
  publicToken: '',
}

export default function Checkout() {
  const [step, setStep] = useState(0)
  const [data, setData] = useState<CheckoutData>(initial)
  const { count } = useCart()

  return (
    <div className="min-h-screen bg-creme-50">
      <Header cartCount={count()} onCartClick={() => {}} />
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Stepper */}
        <div className="flex items-center mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex-1 text-center">
              <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-sm font-bold ${
                i <= step ? 'bg-rosa-500 text-white' : 'bg-creme-200 text-chocolate-600'
              }`}>
                {i + 1}
              </div>
              <p className={`text-xs mt-1 ${i <= step ? 'text-rosa-600 font-semibold' : 'text-chocolate-400'}`}>
                {s}
              </p>
            </div>
          ))}
        </div>

        {step === 0 && (
          <StepCustomer
            data={data}
            onNext={(d) => { setData(d); setStep(1) }}
          />
        )}
        {step === 1 && (
          <StepScheduling
            data={data}
            onNext={(d) => { setData(d); setStep(2) }}
            onBack={() => setStep(0)}
          />
        )}
        {step === 2 && (
          <StepPayment
            data={data}
            onNext={(d) => { setData(d); setStep(3) }}
            onBack={() => setStep(1)}
          />
        )}
        {step === 3 && <StepConfirmation data={data} />}
      </div>
    </div>
  )
}
