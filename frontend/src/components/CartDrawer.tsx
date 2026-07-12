import { useCart } from '@/lib/cart'
import { formatBRL } from '@/lib/formatters'
import { useNavigate } from 'react-router-dom'

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function CartDrawer({ open, onOpenChange }: Props) {
  const { items, removeItem, updateQuantity, total, clear } = useCart()
  const navigate = useNavigate()

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 z-50"
        onClick={() => onOpenChange(false)}
      />
      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white z-50 shadow-xl flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="font-display text-xl font-bold text-chocolate-900">Seu Carrinho</h2>
          <button onClick={() => onOpenChange(false)} className="text-2xl text-chocolate-600">
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {items.length === 0 && (
            <p className="text-chocolate-600 text-center py-8">Carrinho vazio</p>
          )}
          {items.map((item) => (
            <div key={item.productId} className="flex gap-4 items-center">
              <div className="w-16 h-16 rounded-lg bg-rosa-100 flex items-center justify-center text-2xl">
                🧁
              </div>
              <div className="flex-1">
                <p className="font-semibold text-chocolate-900 text-sm">{item.name}</p>
                <p className="text-rosa-600 font-bold">{formatBRL(item.priceCents)}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="w-7 h-7 rounded bg-creme-200 text-chocolate-800"
                  onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                >
                  −
                </button>
                <span className="w-6 text-center font-medium">{item.quantity}</span>
                <button
                  className="w-7 h-7 rounded bg-creme-200 text-chocolate-800"
                  onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                >
                  +
                </button>
              </div>
              <button
                onClick={() => removeItem(item.productId)}
                className="text-red-400 hover:text-red-600 text-sm"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {items.length > 0 && (
          <div className="border-t px-6 py-4 space-y-3">
            <div className="flex justify-between font-bold text-lg text-chocolate-900">
              <span>Subtotal</span>
              <span>{formatBRL(total())}</span>
            </div>
            <button
              onClick={() => {
                onOpenChange(false)
                navigate('/checkout')
              }}
              className="w-full py-3 bg-rosa-500 text-white rounded-lg font-semibold hover:bg-rosa-600 transition-colors"
            >
              Finalizar pedido
            </button>
          </div>
        )}
      </div>
    </>
  )
}
