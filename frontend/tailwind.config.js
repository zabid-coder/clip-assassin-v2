/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-bg': '#19122a', 
        'brand-card': 'rgba(255, 255, 255, 0.03)',
        'brand-border': 'rgba(255, 255, 255, 0.08)',
        'brand-primary': '#7e5cf5',
        'brand-secondary': '#8b5cf6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
