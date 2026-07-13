import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-chocolate-900 text-creme-100 py-16 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="grid md:grid-cols-3 gap-12 mb-12">
          {/* Brand */}
          <div>
            <p className="font-script text-3xl text-rosa-400 mb-3">Doce Encanto</p>
            <p className="text-sm text-chocolate-300 leading-relaxed">
              Doces artesanais feitos com amor em São Paulo.
              Encomende online e receba fresquinho.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-semibold text-creme-200 mb-4 text-sm uppercase tracking-wider">Links</h4>
            <nav className="space-y-2 text-sm">
              <a href="#vitrine" className="block text-chocolate-300 hover:text-rosa-400 transition-colors">Cardápio</a>
              <a href="#como-funciona" className="block text-chocolate-300 hover:text-rosa-400 transition-colors">Como funciona</a>
              <a href="#faq" className="block text-chocolate-300 hover:text-rosa-400 transition-colors">Dúvidas frequentes</a>
              <Link to="/admin/login" className="block text-chocolate-300 hover:text-rosa-400 transition-colors">Área admin</Link>
            </nav>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold text-creme-200 mb-4 text-sm uppercase tracking-wider">Contato</h4>
            <div className="space-y-2 text-sm text-chocolate-300">
              <p>📍 Rua dos Doces, 123 — Vila Mariana, SP</p>
              <p>📱 (11) 98765-4321</p>
              <p>✉️ contato@doceencanto.com.br</p>
              <p className="text-xs text-chocolate-500 mt-3">
                ⏰ Seg–Sáb: 9h–19h | Dom: fechado
              </p>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-chocolate-700 pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-chocolate-500">
            🔒 Pagamento seguro via Pix • Projeto de portfólio — dados fictícios
          </p>
          <div className="flex items-center gap-4 text-xs text-chocolate-500">
            <span>Powered by AbacatePay</span>
            <span>•</span>
            <a href="https://github.com/LufeDigitalWave/doce-encanto" target="_blank" rel="noopener"
               className="hover:text-rosa-400 transition-colors">
              GitHub ↗
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
