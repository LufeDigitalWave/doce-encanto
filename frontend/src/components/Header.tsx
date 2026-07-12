import { Link } from 'react-router-dom'

interface HeaderProps {
  cartCount: number
  onCartClick: () => void
}

export default function Header({ cartCount, onCartClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-white shadow-sm border-b border-rosa-200">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="font-display text-2xl font-bold text-rosa-600">
          🧁 Doce Encanto
        </Link>
        <div className="flex gap-4">
          <Link to="/admin/login" className="text-sm text-chocolate-600 hover:text-rosa-600">
            Admin
          </Link>
          <button
            onClick={onCartClick}
            className="relative px-3 py-2 bg-rosa-500 text-white rounded-lg hover:bg-rosa-600">
            🛒 Carrinho
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-chocolate-800 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
