/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef4ff',
          100: '#d9e6ff',
          500: '#3d5afe',
          600: '#2f46e0',
          700: '#2438b3',
          900: '#1a2673',
        },
      },
    },
  },
  plugins: [],
}
