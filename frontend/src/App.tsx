import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Checkout from './pages/Checkout'
import OrderTracking from './pages/OrderTracking'
import PaymentDone from './pages/PaymentDone'
import AdminLogin from './pages/admin/AdminLogin'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminOrders from './pages/admin/AdminOrders'
import AdminProducts from './pages/admin/AdminProducts'
import AdminOutbox from './pages/admin/AdminOutbox'
import AdminLayout from './components/AdminLayout'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/checkout" element={<Checkout />} />
      <Route path="/pedido/done" element={<PaymentDone />} />
      <Route path="/pedido/:token" element={<OrderTracking />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="orders" element={<AdminOrders />} />
        <Route path="products" element={<AdminProducts />} />
        <Route path="outbox" element={<AdminOutbox />} />
      </Route>
    </Routes>
  )
}
