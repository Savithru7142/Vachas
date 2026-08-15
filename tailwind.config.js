/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        ink: '#0a0a0a',
        paper: '#fafaf8',
        'paper-warm': '#f5f3ef',
        charcoal: '#2b2b2b',
        smoke: '#6b6b6b',
        line: '#e5e5e5',
        ghost: '#ffffff',
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
};
