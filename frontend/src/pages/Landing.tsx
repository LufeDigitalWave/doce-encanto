import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatBRL } from '@/lib/formatters'
import { useCart } from '@/lib/cart'
import Header from '@/components/Header'
import CartDrawer from '@/components/CartDrawer'
import Hero from '@/components/Hero'
import Testimonials from '@/components/Testimonials'
import Vitrine from '@/components/Vitrine'
import HowItWorks from '@/components/HowItWorks'
import FAQ from '@/components/FAQ'
import Footer from '@/components/Footer'

interface Product {
  id: number
  name: string
  slug: string
  description: string
  price_cents: number
  image_url: string | null
  is_active: boolean
}

export default function Landing() {
  const [cartOpen, setCartOpen] = useState(false)
  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: () => api.get('/products').then((r) => r.data),
  })

  const { count } = useCart()

  return (
    <div className="flex flex-col min-h-screen bg-creme-50">
      <Header cartCount={count()} onCartClick={() => setCartOpen(true)} />
      <main className="flex-1">
        <Hero />
        <Testimonials />
        <Vitrine products={products} />
        <HowItWorks />
        <FAQ />
      </main>
      <Footer />
      <CartDrawer open={cartOpen} onOpenChange={setCartOpen} />
    </div>
  )
}
