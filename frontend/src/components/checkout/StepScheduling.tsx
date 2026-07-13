import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import type { CheckoutData } from '@/pages/Checkout'

interface Slot {
  id: number
  date: string
  start_time: string
  end_time: string
  capacity: number
  remaining: number
  available: boolean
}

interface Props {
  data: CheckoutData
  onNext: (data: CheckoutData) => void
  onBack: () => void
}

function getDates(n: number): string[] {
  const dates: string[] = []
  const now = new Date()
  for (let i = 1; i <= n; i++) {
    const d = new Date(now)
    d.setDate(d.getDate() + i)
    if (d.getDay() === 0) continue // Sunday
    dates.push(d.toISOString().slice(0, 10))
    if (dates.length >= 14) break
  }
  return dates
}

export default function StepScheduling({ data, onNext, onBack }: Props) {
  const [selectedDate, setSelectedDate] = useState(data.scheduledDate || '')
  const [selectedSlot, setSelectedSlot] = useState<number | null>(data.slotId)
  const dates = getDates(20)

  const { data: availability } = useQuery({
    queryKey: ['availability', selectedDate, data.fulfillmentType],
    queryFn: () =>
      api
        .get('/scheduling/availability', {
          params: { date: selectedDate, fulfillment: data.fulfillmentType },
        })
        .then((r) => r.data),
    enabled: !!selectedDate,
  })

  const slots: Slot[] = availability?.slots || []

  const handleNext = () => {
    if (!selectedDate || !selectedSlot) return
    onNext({ ...data, scheduledDate: selectedDate, slotId: selectedSlot })
  }

  return (
    <div className="space-y-6">
      <h2 className="font-display text-2xl font-bold text-chocolate-900">Escolha data e horário</h2>

      {/* Date selector */}
      <div className="flex overflow-x-auto gap-2 pb-2">
        {dates.map((d) => {
          const dt = new Date(d + 'T00:00:00')
          const label = dt.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' })
          return (
            <button
              key={d}
              onClick={() => { setSelectedDate(d); setSelectedSlot(null) }}
              className={`shrink-0 px-4 py-2 rounded-lg border text-sm font-medium ${
                selectedDate === d
                  ? 'border-rosa-500 bg-rosa-50 text-rosa-700'
                  : 'border-gray-200 text-chocolate-600 hover:bg-creme-100'
              }`}
            >
              {label}
            </button>
          )
        })}
      </div>

      {/* Slot grid */}
      {selectedDate && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {slots.map((s) => (
            <button
              key={s.id}
              disabled={!s.available}
              onClick={() => setSelectedSlot(s.id)}
              className={`p-3 rounded-lg border text-center text-sm ${
                !s.available
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : selectedSlot === s.id
                  ? 'border-rosa-500 bg-rosa-50 text-rosa-700 font-semibold'
                  : 'border-gray-200 hover:bg-creme-100 text-chocolate-700'
              }`}
            >
              <div>{s.start_time}–{s.end_time}</div>
              <div className="text-xs mt-1 text-chocolate-500">
                {s.available ? `${s.remaining} horário${s.remaining !== 1 ? 's' : ''} disponível` : '⚫ Indisponível'}
              </div>
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <button onClick={onBack} className="flex-1 py-3 border rounded-lg text-chocolate-700">
          ← Voltar
        </button>
        <button
          onClick={handleNext}
          disabled={!selectedSlot}
          className="flex-1 py-3 bg-rosa-500 text-white font-semibold rounded-lg hover:bg-rosa-600 disabled:opacity-50"
        >
          Continuar para pagamento →
        </button>
      </div>
    </div>
  )
}
