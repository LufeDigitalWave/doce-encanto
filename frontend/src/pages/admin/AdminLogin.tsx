import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import toast from 'react-hot-toast'

export default function AdminLogin() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.post('/admin/login', { username, password })
      localStorage.setItem('admin_token', res.data.access_token)
      navigate('/admin')
    } catch {
      toast.error('Credenciais inválidas')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-creme-50">
      <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm space-y-4">
        <h1 className="font-display text-2xl font-bold text-center text-chocolate-900">🧁 Admin</h1>
        <input
          className="w-full p-3 border rounded-lg"
          placeholder="Usuário"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="w-full p-3 border rounded-lg"
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="w-full py-3 bg-rosa-500 text-white rounded-lg font-semibold hover:bg-rosa-600">
          Entrar
        </button>
      </form>
    </div>
  )
}
