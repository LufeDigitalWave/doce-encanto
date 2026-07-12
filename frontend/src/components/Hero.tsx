export default function Hero() {
  return (
    <section className="bg-gradient-to-b from-rosa-50 to-creme-100 py-20 text-center">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="font-display text-5xl md:text-6xl font-bold text-chocolate-900 mb-4">
          Doce Encanto
        </h1>
        <p className="text-xl text-chocolate-700 mb-8">
          Doces artesanais feitos com amor em São Paulo. Encomende com antecedência e receba fresquinho.
        </p>
        <a
          href="#vitrine"
          className="inline-block px-8 py-3 bg-rosa-500 text-white text-lg font-semibold rounded-lg hover:bg-rosa-600 transition-colors shadow-lg shadow-rosa-200"
        >
          Fazer meu pedido
        </a>
      </div>
    </section>
  )
}
