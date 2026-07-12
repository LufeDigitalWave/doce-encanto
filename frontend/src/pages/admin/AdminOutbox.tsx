import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export default function AdminOutbox() {
  const { data: notifications = [] } = useQuery({
    queryKey: ['admin-outbox'],
    queryFn: () => api.get('/admin/notifications').then((r) => r.data),
    refetchInterval: 5000,
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-chocolate-900 mb-6">Caixa de Saída</h1>
      <div className="space-y-4">
        {notifications.map((n: any) => (
          <div key={n.id} className="bg-white p-4 rounded-xl shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-lg">{n.channel === 'email' ? '📧' : '💬'}</span>
              <span className="font-semibold text-chocolate-900 text-sm">{n.template_key}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${n.status === 'sent' ? 'bg-green-100 text-green-700' : n.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {n.status}
              </span>
              <span className="text-xs text-chocolate-400 ml-auto">{new Date(n.created_at).toLocaleString('pt-BR')}</span>
            </div>
            <p className="text-sm text-chocolate-600 mb-1">Para: {n.recipient}</p>
            <pre className="text-xs bg-creme-100 p-3 rounded-lg whitespace-pre-wrap font-body text-chocolate-700">
              {n.rendered_body}
            </pre>
          </div>
        ))}
        {notifications.length === 0 && (
          <p className="text-chocolate-500">Nenhuma notificação enviada ainda.</p>
        )}
      </div>
    </div>
  )
}
