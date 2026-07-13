const testimonials = [
  {
    name: 'Maria Silva',
    bairro: 'Vila Mariana',
    text: 'Os brigadeiros mais gostosos que já provei! Fiz pedido para o aniversário da minha filha e todo mundo amou. As crianças pediram bis.',
    avatar: '👩',
  },
  {
    name: 'João Pereira',
    bairro: 'Moema',
    text: 'Atendimento impecável, entregaram 15 minutos antes do horário combinado. A embalagem era linda, dava até pena de abrir. Virei cliente fiel.',
    avatar: '👨',
  },
  {
    name: 'Ana Costa',
    bairro: 'Pinheiros',
    text: 'O bolo vulcão é SURREAL. Pedi para o Dia das Mães e minha sogra chorou de felicidade. Já agendei o próximo pro aniversário dela.',
    avatar: '👩‍🦱',
  },
]

export default function Testimonials() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <p className="font-script text-rosa-500 text-2xl mb-2">depoimentos</p>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-chocolate-800">
            Quem provou, recomenda
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="relative bg-creme-50 p-7 rounded-2xl border border-chocolate-100/50
                         hover:shadow-lg hover:-translate-y-1 transition-all duration-300
                         opacity-0 animate-fade-up"
              style={{ animationDelay: `${i * 120}ms`, animationFillMode: 'forwards' }}
            >
              {/* Quote mark */}
              <span className="absolute top-4 right-5 font-display text-5xl text-rosa-200 select-none">"</span>

              <p className="text-chocolate-700 text-sm leading-relaxed mb-5 relative z-10">
                {t.text}
              </p>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-rosa-100 flex items-center justify-center text-lg">
                  {t.avatar}
                </div>
                <div>
                  <p className="font-semibold text-chocolate-800 text-sm">{t.name}</p>
                  <p className="text-xs text-chocolate-400">{t.bairro}, SP</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
