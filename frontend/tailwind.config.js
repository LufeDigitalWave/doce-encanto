/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Doce Encanto — confeitaria premium palette
        rosa: {
          50: '#fff5f7',
          100: '#ffe0e8',
          200: '#ffc2d4',
          300: '#ffa3c0',
          400: '#ff7aa8',
          500: '#f4508c',
          600: '#d63770',
          700: '#b72d5a',
          800: '#8f2247',
          900: '#6d1a36',
        },
        creme: {
          50: '#fffdf5',
          100: '#fff8e1',
          200: '#ffefc2',
          300: '#ffe5a3',
          400: '#ffd97a',
          500: '#f5c94a',
        },
        chocolate: {
          50: '#fdf6f0',
          100: '#f7e6d5',
          200: '#e8c6a5',
          300: '#d4a373',
          400: '#b87b4a',
          500: '#8b5e34',
          600: '#6b4727',
          700: '#4e331c',
          800: '#382413',
          900: '#251709',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}