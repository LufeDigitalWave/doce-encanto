import { Link } from 'react-router-dom'

interface HeaderProps {
  cartCount: number
  onCartClick: () => void
}

export default function Header({ cartCount, onCartClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-creme-50/80 backdrop-blur-md border-b border-chocolate-100/50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2">
          <span className="font-script text-2xl text-rosa-500">Doce Encanto</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          <Link to="/#vitrine" className="text-sm font-medium text-chocolate-600 hover:text-rosa-500 transition-colors">Cardápio</Link>
          <Link to="/#como-funciona" className="text-sm font-medium text-chocolate-600 hover:text-rosa-500 transition-colors">Como funciona</Link>
          <Link to="/#faq" className="text-sm font-medium text-chocolate-600 hover:text-rosa-500 transition-colors">Dúvidas</Link>
          <Link to="/admin/login" className="text-sm font-medium text-chocolate-400 hover:text-rosa-500 transition-colors">
            Admin
          </Link>
        </nav>

        <button
          onClick={onCartClick}
          className="relative flex items-center gap-2 px-4 py-2.5 bg-chocolate-800 text-creme-50
                     rounded-full text-sm font-semibold hover:bg-rosa-600 active:scale-95 transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          Carrinho
          {cartCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 bg-rosa-500 text-white text-[10px] font-bold
                           w-5 h-5 rounded-full flex items-center justify-center animate-pulse-soft">
              {cartCount}
            </span>
          )}
        </button>
      </div>
    </header>
  )
}
