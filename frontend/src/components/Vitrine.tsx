import { useCart } from '@/lib/cart'
import { formatBRL } from '@/lib/formatters'
import toast from 'react-hot-toast'

interface Product {
  id: number
  name: string
  slug: string
  description: string
  price_cents: number
  image_url: string | null
}

export default function Vitrine({ products }: { products: Product[] }) {
  const { addItem } = useCart()

  const handleAdd = (p: Product) => {
    addItem(p)
    toast.success(`${p.name} adicionado!`, { icon: '🧁' })
  }

  return (
    <section id="vitrine" className="py-20 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="font-script text-rosa-500 text-2xl mb-2">nossos doces</p>
          <h2 className="font-display text-4xl md:text-5xl font-bold text-chocolate-800">
            Feitos com amor
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {products.map((p, i) => (
            <div
              key={p.id}
              className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 opacity-0 animate-fade-up"
              style={{ animationDelay: `${i * 80}ms`, animationFillMode: 'forwards' }}
            >
              {/* Image */}
              <div className="relative h-56 overflow-hidden bg-creme-100">
                {p.image_url ? (
                  <img
                    src={p.image_url}
                    alt={p.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-5xl">🧁</div>
                )}
                {/* Price tag overlay */}
                <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-full shadow-sm">
                  <span className="font-display font-bold text-rosa-600 text-sm">
                    {formatBRL(p.price_cents)}
                  </span>
                </div>
              </div>

              {/* Content */}
              <div className="p-5">
                <h3 className="font-display font-semibold text-chocolate-900 text-lg mb-1.5 leading-tight">
                  {p.name}
                </h3>
                <p className="text-sm text-chocolate-500 mb-4 line-clamp-2">
                  {p.description}
                </p>
                <button
                  onClick={() => handleAdd(p)}
                  className="w-full py-2.5 bg-chocolate-800 text-creme-50 text-sm font-semibold rounded-xl
                             hover:bg-rosa-600 active:scale-95 transition-all duration-200"
                >
                  Adicionar ao carrinho
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
