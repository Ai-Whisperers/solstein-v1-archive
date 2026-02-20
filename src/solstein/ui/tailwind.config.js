/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        alchemist: {
          bg: '#030712',
          card: '#0f172a',
          gold: '#fbbf24',
          silver: '#94a3b8',
          glow: '#1e40af',
        }
      },
      fontFamily: {
        wizard: ['Cinzel', 'serif'],
        mono: ['Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
