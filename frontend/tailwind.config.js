/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Doce Encanto — confeitaria premium palette (cream-dominant)
        rosa: {
          50: '#FFF5F7',
          100: '#FFE0E8',
          200: '#FFC2D4',
          300: '#FFA3C0',
          400: '#FF7AA8',
          500: '#F4508C',
          600: '#D63770',
          700: '#B72D5A',
          800: '#8F2247',
          900: '#6D1A36',
        },
        creme: {
          50: '#FFFDF8',
          100: '#FFF8EC',
          200: '#FFF1D6',
          300: '#FFE5A3',
          400: '#FFD97A',
          500: '#F5C94A',
        },
        chocolate: {
          50: '#FAF4ED',
          100: '#F2E4D2',
          200: '#E8C6A5',
          300: '#D4A373',
          400: '#B87B4A',
          500: '#8B5E34',
          600: '#6B4727',
          700: '#4E331C',
          800: '#382413',
          900: '#251709',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        body: ['"DM Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        script: ['Caveat', 'cursive'],
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease-out forwards',
        'fade-in': 'fadeIn 0.4s ease-out forwards',
        'drawer-slide': 'drawerSlide 0.35s cubic-bezier(0.32, 0.72, 0, 1) forwards',
        'pulse-soft': 'pulseSoft 2.5s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        drawerSlide: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.95 0 0 0 0 0.91 0 0 0 0 0.85 0 0 0 0.18 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [],
}