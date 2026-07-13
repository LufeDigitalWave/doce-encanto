export default function Hero() {
  return (
    <section className="relative min-h-[85vh] flex items-center overflow-hidden">
      {/* Background layers */}
      <div className="absolute inset-0 bg-gradient-to-br from-creme-50 via-creme-100 to-rosa-50" />
      <div className="absolute inset-0 bg-noise opacity-40" />

      {/* Decorative floating shapes */}
      <div className="absolute -top-20 -right-20 w-80 h-80 bg-rosa-200/30 rounded-full blur-3xl" />
      <div className="absolute bottom-10 -left-10 w-60 h-60 bg-creme-300/40 rounded-full blur-2xl" />

      {/* Watermark */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none">
        <p className="font-display text-[12vw] font-black text-chocolate-800/[0.03] whitespace-nowrap -rotate-12">
          DOCE ENCANTO
        </p>
      </div>

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 py-20 grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-8">
          {/* Script accent */}
          <p
            className="font-script text-rosa-500 text-2xl md:text-3xl opacity-0 animate-fade-up"
            style={{ animationDelay: '0ms' }}
          >
            doceria artesanal
          </p>

          {/* Main headline */}
          <h1
            className="font-display text-5xl md:text-7xl lg:text-8xl font-bold leading-[0.9] text-chocolate-900 opacity-0 animate-fade-up"
            style={{ animationDelay: '100ms' }}
          >
            Doce
            <br />
            <span className="text-rosa-500">Encanto</span>
          </h1>

          {/* Subtitle */}
          <p
            className="text-lg md:text-xl text-chocolate-600 max-w-md leading-relaxed opacity-0 animate-fade-up"
            style={{ animationDelay: '200ms' }}
          >
            Brigadeiros gourmet, bolos de pote, tortas e kits festa.
            Encomende com 24h de antecedência e receba fresquinho em casa.
          </p>

          {/* CTA */}
          <div
            className="flex flex-wrap gap-4 opacity-0 animate-fade-up"
            style={{ animationDelay: '300ms' }}
          >
            <a
              href="#vitrine"
              className="inline-flex items-center gap-2 px-8 py-4 bg-rosa-500 text-white text-lg font-semibold rounded-full
                         hover:bg-rosa-600 hover:shadow-xl hover:shadow-rosa-200/50 active:scale-95
                         transition-all duration-300"
            >
              Fazer meu pedido
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </a>
            <a
              href="#como-funciona"
              className="inline-flex items-center gap-2 px-6 py-4 text-chocolate-700 font-medium
                         hover:text-rosa-600 transition-colors"
            >
              Como funciona?
            </a>
          </div>

          {/* Social proof mini */}
          <div
            className="flex items-center gap-3 pt-4 opacity-0 animate-fade-up"
            style={{ animationDelay: '400ms' }}
          >
            <div className="flex -space-x-2">
              {['🧑‍🍳', '👩', '👨'].map((e, i) => (
                <div key={i} className="w-9 h-9 rounded-full bg-creme-200 border-2 border-white flex items-center justify-center text-sm">
                  {e}
                </div>
              ))}
            </div>
            <p className="text-sm text-chocolate-500">
              <span className="font-semibold text-chocolate-800">+200 pedidos</span> entregues este mês
            </p>
          </div>
        </div>

        {/* Right side — hero image collage */}
        <div className="hidden lg:grid grid-cols-2 gap-4 opacity-0 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <div className="space-y-4">
            <div className="rounded-3xl overflow-hidden shadow-2xl shadow-chocolate-200/30 rotate-2 hover:rotate-0 transition-transform duration-500">
              <img src="/products/brigadeiro-gourmet.jpg" alt="Brigadeiros gourmet" className="w-full h-48 object-cover" />
            </div>
            <div className="rounded-3xl overflow-hidden shadow-xl -rotate-1 hover:rotate-0 transition-transform duration-500">
              <img src="/products/torta-red-velvet.jpg" alt="Torta Red Velvet" className="w-full h-36 object-cover" />
            </div>
          </div>
          <div className="space-y-4 pt-8">
            <div className="rounded-3xl overflow-hidden shadow-xl rotate-1 hover:rotate-0 transition-transform duration-500">
              <img src="/products/bolo-vulcao.jpg" alt="Bolo Vulcão" className="w-full h-36 object-cover" />
            </div>
            <div className="rounded-3xl overflow-hidden shadow-2xl shadow-rosa-200/30 -rotate-2 hover:rotate-0 transition-transform duration-500">
              <img src="/products/kit-festa.jpg" alt="Kit Festa" className="w-full h-48 object-cover" />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
