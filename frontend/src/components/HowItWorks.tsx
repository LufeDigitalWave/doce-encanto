export default function HowItWorks() {
  const steps = [
    { emoji: '🛍️', title: 'Escolha', desc: 'Navegue pela vitrine e adicione seus doces favoritos ao carrinho.' },
    { emoji: '📅', title: 'Agende', desc: 'Escolha a data e horário de retirada ou entrega.' },
    { emoji: '🎉', title: 'Receba', desc: 'Pague via Pix e receba seus doces fresquinhos.' },
  ]
  return (
    <section className="py-16 px-4 bg-white">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="font-display text-3xl font-bold mb-12 text-chocolate-900">Como funciona</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((s, i) => (
            <div key={i}>
              <div className="text-5xl mb-4">{s.emoji}</div>
              <h3 className="font-semibold text-lg text-chocolate-800 mb-2">{s.title}</h3>
              <p className="text-chocolate-600">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
