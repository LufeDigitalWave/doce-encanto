const steps = [
  {
    num: '01',
    icon: '🛍️',
    title: 'Escolha',
    desc: 'Navegue pela vitrine e adicione seus doces favoritos ao carrinho. Sem mínimo de pedido.',
  },
  {
    num: '02',
    icon: '📅',
    title: 'Agende',
    desc: 'Escolha a data e horário de retirada na Vila Mariana ou entrega em domicílio.',
  },
  {
    num: '03',
    icon: '💳',
    title: 'Pague',
    desc: 'Pague via Pix (QR Code instantâneo). Sem cadastro, sem complicação.',
  },
]

export default function HowItWorks() {
  return (
    <section id="como-funciona" className="py-20 px-4 bg-creme-50">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <p className="font-script text-rosa-500 text-2xl mb-2">como funciona</p>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-chocolate-800">
            3 passos e pronto
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((s, i) => (
            <div
              key={i}
              className="relative bg-white p-8 rounded-2xl text-center
                         hover:shadow-lg transition-shadow duration-300
                         opacity-0 animate-fade-up"
              style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'forwards' }}
            >
              {/* Step number */}
              <span className="absolute top-4 left-5 font-display text-4xl font-black text-chocolate-100">
                {s.num}
              </span>

              <div className="text-4xl mb-4 relative z-10">{s.icon}</div>
              <h3 className="font-display font-bold text-xl text-chocolate-800 mb-2">{s.title}</h3>
              <p className="text-sm text-chocolate-500 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
