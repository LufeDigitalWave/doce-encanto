const testimonials = [
  { name: 'Maria Silva', bairro: 'Vila Mariana', text: 'Os brigadeiros mais gostosos que já provei! Fiz pedido para o aniversário da minha filha e todo mundo amou.' },
  { name: 'João Pereira', bairro: 'Moema', text: 'Atendimento impecável, entregaram no horário e a embalagem era linda. Virei cliente fiel.' },
  { name: 'Ana Costa', bairro: 'Pinheiros', text: 'O bolo vulcão é SURREAL. Pedi para o Dia das Mães e minha sogra chorou de felicidade.' },
]

export default function Testimonials() {
  return (
    <section className="py-16 px-4 max-w-4xl mx-auto">
      <h2 className="font-display text-3xl font-bold text-center mb-12 text-chocolate-900">
        O que dizem nossos clientes
      </h2>
      <div className="grid md:grid-cols-3 gap-6">
        {testimonials.map((t, i) => (
          <div key={i} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <p className="text-chocolate-700 mb-4 italic">"{t.text}"</p>
            <p className="font-semibold text-rosa-600">{t.name}</p>
            <p className="text-sm text-chocolate-500">{t.bairro}, SP</p>
          </div>
        ))}
      </div>
    </section>
  )
}
