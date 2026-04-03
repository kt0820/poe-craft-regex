/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // PoE dark UI palette
        'poe-bg':        '#0a0a0b',
        'poe-surface':   '#111114',
        'poe-panel':     '#16161a',
        'poe-border':    '#2a2418',
        'poe-gold':      '#c8a850',
        'poe-gold-light':'#e8c870',
        'poe-gold-dark': '#8a6f2e',
        'poe-text':      '#c0b090',
        'poe-text-dim':  '#6b5f45',
        'poe-red':       '#8b2020',
        'poe-highlight': '#1e1a12',
      },
      fontFamily: {
        'heading': ['"Cinzel"', 'serif'],
        'body':    ['"Crimson Text"', 'serif'],
        'mono':    ['"Fira Code"', 'monospace'],
      },
      boxShadow: {
        'poe':       '0 0 0 1px #2a2418, 0 4px 24px rgba(0,0,0,0.8)',
        'poe-inner': 'inset 0 1px 0 rgba(200,168,80,0.1)',
        'poe-glow':  '0 0 12px rgba(200,168,80,0.15)',
      },
    },
  },
  plugins: [],
}
