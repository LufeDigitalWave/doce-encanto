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
    toast.success(`${p.name} adicionado!`)
  }

  return (
    <section id="vitrine" className="py-16 px-4 max-w-7xl mx-auto">
      <h2 className="font-display text-3xl font-bold text-center mb-12 text-chocolate-900">
        Nossos Doces
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {products.map((p) => (
          <div
            key={p.id}
            className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-4 flex flex-col"
          >
            <div className="h-40 bg-gradient-to-br from-rosa-100 to-creme-200 rounded-lg mb-4 flex items-center justify-center text-4xl">
              🧁
            </div>
            <h3 className="font-semibold text-chocolate-900 text-lg mb-1">{p.name}</h3>
            <p className="text-sm text-chocolate-600 flex-1 mb-3">{p.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-xl font-bold text-rosa-600">
                {formatBRL(p.price_cents)}
              </span>
              <button
                onClick={() => handleAdd(p)}
                className="px-3 py-2 bg-rosa-500 text-white text-sm rounded-lg hover:bg-rosa-600 transition-colors"
              >
                Adicionar
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
