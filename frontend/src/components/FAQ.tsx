import { useState } from 'react'

const faqs = [
  { q: 'Qual o prazo mínimo de encomenda?', a: 'Pedidos devem ser feitos com pelo menos 24 horas de antecedência.' },
  { q: 'Qual a área de entrega?', a: 'Atendemos toda a Grande São Paulo. O frete é fixo de R$ 12,00, grátis acima de R$ 150.' },
  { q: 'Quais as formas de pagamento?', a: 'Aceitamos Pix (pagamento instantâneo via QR Code).' },
  { q: 'Posso cancelar um pedido?', a: 'Sim, pedidos podem ser cancelados até 12h antes do horário agendado.' },
  { q: 'Aceitam encomendas grandes (acima de 200 doces)?', a: 'Sim! Entre em contato pelo WhatsApp para combinarmos prazo e desconto especial.' },
]

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section className="py-16 px-4 max-w-3xl mx-auto">
      <h2 className="font-display text-3xl font-bold text-center mb-12 text-chocolate-900">
        Perguntas Frequentes
      </h2>
      <div className="space-y-3">
        {faqs.map((f, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm">
            <button
              className="w-full text-left px-6 py-4 font-medium text-chocolate-800 flex justify-between items-center"
              onClick={() => setOpen(open === i ? null : i)}
            >
              {f.q}
              <span className="text-rosa-500">{open === i ? '−' : '+'}</span>
            </button>
            {open === i && (
              <div className="px-6 pb-4 text-chocolate-600">{f.a}</div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
