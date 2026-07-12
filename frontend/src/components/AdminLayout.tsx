import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

export default function AdminLayout() {
  const navigate = useNavigate()
  const token = localStorage.getItem('admin_token')

  useEffect(() => {
    if (!token) navigate('/admin/login')
  }, [token])

  const logout = () => {
    localStorage.removeItem('admin_token')
    navigate('/admin/login')
  }

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-chocolate-900 text-creme-100 p-6 space-y-4">
        <h2 className="font-display text-lg font-bold mb-6">🧁 Admin</h2>
        <nav className="space-y-2">
          <Link to="/admin" className="block hover:text-rosa-300">Dashboard</Link>
          <Link to="/admin/orders" className="block hover:text-rosa-300">Pedidos</Link>
          <Link to="/admin/products" className="block hover:text-rosa-300">Produtos</Link>
          <Link to="/admin/outbox" className="block hover:text-rosa-300">Caixa de Saída</Link>
        </nav>
        <button onClick={logout} className="text-sm text-chocolate-400 hover:text-red-300 pt-8">
          Sair
        </button>
      </aside>
      <main className="flex-1 bg-creme-50 p-8">
        <Outlet />
      </main>
    </div>
  )
}
